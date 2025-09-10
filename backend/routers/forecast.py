from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List
import io
import pandas as pd
import numpy as np

from schemas.forecast import (
    TrainRequest,
    PredictRequest,
    ForecastResponse,
    ForecastPoint,
    ModelsResponse,
)
from services.prophet_service import (
    train_and_persist_model,
    generate_forecast,
    list_available_models,
)
from services.weather_service import weather_service
from services.holidays_service import holidays_service
from services.calendar_service import calendar_service
from services.ensemble_service import ensemble_service
from services.backtesting_service import backtesting_service
from services.baseline_service import baseline_service
from services.insights_service import insights_service
from services.metrics_service import metrics_service


router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.post("/train")
def train(request: TrainRequest):
    try:
        records: List[dict] = [item.dict() for item in request.data]
        dataframe = pd.DataFrame.from_records(records)
        train_and_persist_model(
            series_id=request.series_id,
            dataframe=dataframe,
            regressors=request.regressors or [],
        )
        return {"status": "ok", "series_id": request.series_id}
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/train-file")
async def train_file(series_id: str = Form(...), file: UploadFile = File(...)):
    try:
        raw_bytes = await file.read()
        text_stream = io.StringIO(raw_bytes.decode("utf-8"))
        try:
            dataframe = pd.read_csv(text_stream)
        except Exception:
            # Retry with semicolon delimiter, common in PT-BR locales
            text_stream.seek(0)
            dataframe = pd.read_csv(text_stream, sep=";")

        if "ds" not in dataframe.columns or "y" not in dataframe.columns:
            raise HTTPException(
                status_code=422,
                detail="CSV deve conter colunas 'ds' (data) e 'y' (valor).",
            )

        train_and_persist_model(series_id=series_id, dataframe=dataframe, regressors=[])
        return {"status": "ok", "series_id": series_id}
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/predict-ensemble")
async def predict_ensemble(request: PredictRequest):
    """Previsão usando ensemble Prophet + Naive Semanal"""
    try:
        # Buscar dados históricos para Naive Semanal
        from services.prophet_service import _get_model_path
        import joblib
        from pathlib import Path
        
        model_path = _get_model_path(request.series_id)
        if not model_path.exists():
            raise HTTPException(status_code=404, detail=f"Modelo '{request.series_id}' não encontrado.")
        
        # Carregar dados históricos (precisamos dos dados originais)
        # Por enquanto, vamos usar uma abordagem simplificada
        historical_data = pd.DataFrame({
            'ds': pd.date_range(start='2024-01-01', end='2024-12-31', freq='D'),
            'y': np.random.randint(20, 80, 365)  # Dados simulados para demonstração
        })
        
        # Criar ensemble
        ensemble_result = ensemble_service.create_ensemble_forecast(
            request.series_id, 
            historical_data, 
            request.horizon
        )
        
        # Converter para formato de resposta
        forecast_points = []
        for _, row in ensemble_result['ensemble_forecast'].iterrows():
            forecast_points.append(ForecastPoint(
                ds=row['ds'].strftime('%Y-%m-%d'),
                yhat=int(row['yhat']),
                yhat_lower=int(row['yhat_lower']),
                yhat_upper=int(row['yhat_upper'])
            ))
        
        return {
            "forecast": forecast_points,
            "ensemble_info": {
                "weights": ensemble_result['weights'],
                "statistics": ensemble_result['statistics'],
                "prophet_mean": ensemble_result['statistics']['prophet_mean'],
                "naive_mean": ensemble_result['statistics']['naive_mean'],
                "ensemble_mean": ensemble_result['statistics']['ensemble_mean']
            }
        }
        
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/predict", response_model=ForecastResponse)
async def predict(request: PredictRequest) -> ForecastResponse:
    try:
        future_regs_df = None
        # Habilitar regressores externos com os novos serviços
        if request.latitude is not None and request.longitude is not None:
            # tentar obter regressors para os próximos 'horizon' dias a partir de hoje
            from datetime import date, timedelta
            start_date = pd.Timestamp.today().normalize().date()
            end_date = start_date + timedelta(days=request.horizon - 1)
            
            # Como Open-Meteo não tem dados futuros, usar dados históricos recentes como aproximação
            # Buscar dados dos últimos 30 dias como base para o futuro
            hist_start = start_date - timedelta(days=30)
            hist_end = start_date - timedelta(days=1)
            
            try:
                print(f"🌤️  Buscando dados climáticos para {request.horizon} dias...")
                
                # Buscar previsão do tempo aprimorada
                weather_df, weather_insights = weather_service.get_enhanced_weather_forecast(
                    request.latitude, 
                    request.longitude, 
                    request.horizon
                )
                print(f"🌤️  Dados climáticos aprimorados: {len(weather_df) if weather_df is not None else 0} registros")
                print(f"📊 Insights climáticos: {len(weather_insights)} encontrados")
                
                # Buscar feriados aprimorados
                print(f"🎉 Buscando feriados aprimorados para o período...")
                holidays_df, holiday_insights = holidays_service.create_enhanced_holiday_regressor(
                    pd.Timestamp(start_date),
                    pd.Timestamp(end_date)
                )
                print(f"📊 Insights de feriados: {len(holiday_insights)} encontrados")
                
                # Criar DataFrame de regressores futuros com tamanho exato
                future_regs_df = pd.DataFrame({
                    "ds": pd.date_range(start=start_date, periods=request.horizon, freq="D")
                })
                
                # Adicionar dados climáticos
                if weather_df is not None and not weather_df.empty:
                    # Garantir que weather_df tenha exatamente o horizonte
                    if len(weather_df) >= request.horizon:
                        weather_df = weather_df.head(request.horizon)
                    else:
                        # Se não tiver dados suficientes, duplicar o último
                        last_row = weather_df.iloc[-1].copy()
                        while len(weather_df) < request.horizon:
                            weather_df = pd.concat([weather_df, last_row.to_frame().T], ignore_index=True)
                        weather_df = weather_df.head(request.horizon)
                    
                    future_regs_df = future_regs_df.merge(
                        weather_df, 
                        on="ds", 
                        how="left"
                    )
                    # Preencher valores faltantes com médias para todas as variáveis climáticas
                    future_regs_df["tmax"] = future_regs_df["tmax"].fillna(25.0)
                    future_regs_df["tmin"] = future_regs_df["tmin"].fillna(15.0)
                    future_regs_df["precip"] = future_regs_df["precip"].fillna(0.0)
                    # Preencher variáveis derivadas se existirem
                    if "temp_avg" in future_regs_df.columns:
                        future_regs_df["temp_avg"] = future_regs_df["temp_avg"].fillna(20.0)
                    if "temp_range" in future_regs_df.columns:
                        future_regs_df["temp_range"] = future_regs_df["temp_range"].fillna(10.0)
                    if "thermal_comfort" in future_regs_df.columns:
                        future_regs_df["thermal_comfort"] = future_regs_df["thermal_comfort"].fillna(1)
                    if "respiratory_risk" in future_regs_df.columns:
                        future_regs_df["respiratory_risk"] = future_regs_df["respiratory_risk"].fillna(0)
                    if "dehydration_risk" in future_regs_df.columns:
                        future_regs_df["dehydration_risk"] = future_regs_df["dehydration_risk"].fillna(0)
                    if "accident_risk" in future_regs_df.columns:
                        future_regs_df["accident_risk"] = future_regs_df["accident_risk"].fillna(0)
                    if "month" in future_regs_df.columns:
                        future_regs_df["month"] = future_regs_df["month"].fillna(1)
                    if "is_winter" in future_regs_df.columns:
                        future_regs_df["is_winter"] = future_regs_df["is_winter"].fillna(0)
                    if "is_summer" in future_regs_df.columns:
                        future_regs_df["is_summer"] = future_regs_df["is_summer"].fillna(0)
                else:
                    # Valores padrão se não conseguir buscar dados climáticos
                    future_regs_df["tmax"] = 25.0
                    future_regs_df["tmin"] = 15.0
                    future_regs_df["precip"] = 0.0
                    future_regs_df["temp_avg"] = 20.0
                    future_regs_df["temp_range"] = 10.0
                    future_regs_df["thermal_comfort"] = 1
                    future_regs_df["respiratory_risk"] = 0
                    future_regs_df["dehydration_risk"] = 0
                    future_regs_df["accident_risk"] = 0
                    future_regs_df["month"] = 1
                    future_regs_df["is_winter"] = 0
                    future_regs_df["is_summer"] = 0
                
                # Adicionar feriados
                if holidays_df is not None and not holidays_df.empty:
                    # Garantir que holidays_df tenha exatamente o horizonte
                    if len(holidays_df) >= request.horizon:
                        holidays_df = holidays_df.head(request.horizon)
                    else:
                        # Se não tiver dados suficientes, duplicar o último
                        last_row = holidays_df.iloc[-1].copy()
                        while len(holidays_df) < request.horizon:
                            holidays_df = pd.concat([holidays_df, last_row.to_frame().T], ignore_index=True)
                        holidays_df = holidays_df.head(request.horizon)
                    
                    future_regs_df = future_regs_df.merge(
                        holidays_df, 
                        on="ds", 
                        how="left"
                    )
                    # Preencher valores faltantes para todas as variáveis de feriados
                    future_regs_df["is_holiday"] = future_regs_df["is_holiday"].fillna(0)
                    if "is_extraordinary_event" in future_regs_df.columns:
                        future_regs_df["is_extraordinary_event"] = future_regs_df["is_extraordinary_event"].fillna(0)
                    if "event_impact_factor" in future_regs_df.columns:
                        future_regs_df["event_impact_factor"] = future_regs_df["event_impact_factor"].fillna(1.0)
                    if "is_holiday_weekend" in future_regs_df.columns:
                        future_regs_df["is_holiday_weekend"] = future_regs_df["is_holiday_weekend"].fillna(0)
                    if "is_holiday_monday" in future_regs_df.columns:
                        future_regs_df["is_holiday_monday"] = future_regs_df["is_holiday_monday"].fillna(0)
                else:
                    future_regs_df["is_holiday"] = 0
                    future_regs_df["is_extraordinary_event"] = 0
                    future_regs_df["event_impact_factor"] = 1.0
                    future_regs_df["is_holiday_weekend"] = 0
                    future_regs_df["is_holiday_monday"] = 0
                
                # Garantir que temos exatamente o horizonte de dias
                    future_regs_df = future_regs_df.head(request.horizon)
                
                # Verificar e corrigir valores NaN
                print(f"🔍 Verificando NaN antes da correção:")
                nan_columns = future_regs_df.columns[future_regs_df.isnull().any()].tolist()
                if nan_columns:
                    print(f"⚠️  Colunas com NaN: {nan_columns}")
                    for col in nan_columns:
                        print(f"   {col}: {future_regs_df[col].isnull().sum()} valores NaN")
                        # Preencher NaN com valores padrão
                        if col in ['is_winter', 'is_summer', 'is_holiday', 'is_extraordinary_event', 'is_holiday_weekend', 'is_holiday_monday']:
                            future_regs_df[col] = future_regs_df[col].fillna(0)
                        elif col in ['thermal_comfort', 'respiratory_risk', 'dehydration_risk', 'accident_risk']:
                            future_regs_df[col] = future_regs_df[col].fillna(0)
                        elif col in ['month']:
                            future_regs_df[col] = future_regs_df[col].fillna(1)
                        elif col in ['event_impact_factor']:
                            future_regs_df[col] = future_regs_df[col].fillna(1.0)
                        else:
                            future_regs_df[col] = future_regs_df[col].fillna(0)
                
                print(f"✅ Regressores criados: {list(future_regs_df.columns)}")
                print(f"📊 Tamanho do DataFrame: {len(future_regs_df)} linhas, horizonte: {request.horizon}")
                
            except Exception as e:
                print(f"⚠️  Erro ao buscar dados climáticos: {e}")
                # Se falhar, criar regressores básicos sem clima
                future_regs_df = pd.DataFrame({
                    "ds": pd.date_range(start=start_date, periods=request.horizon, freq="D")
                })
                future_regs_df["tmax"] = 25.0  # temperatura média
                future_regs_df["tmin"] = 15.0
                future_regs_df["precip"] = 0.0
                future_regs_df["temp_avg"] = 20.0
                future_regs_df["temp_range"] = 10.0
                future_regs_df["thermal_comfort"] = 1
                future_regs_df["respiratory_risk"] = 0
                future_regs_df["dehydration_risk"] = 0
                future_regs_df["accident_risk"] = 0
                future_regs_df["month"] = 1
                future_regs_df["is_winter"] = 0
                future_regs_df["is_summer"] = 0
                future_regs_df["is_holiday"] = 0

        print(f"🔍 Debug - Horizon: {request.horizon}")
        print(f"🔍 Debug - Future regressors shape: {future_regs_df.shape if future_regs_df is not None else 'None'}")
        if future_regs_df is not None:
            print(f"🔍 Debug - Future regressors columns: {list(future_regs_df.columns)}")
            print(f"🔍 Debug - Future regressors head:\n{future_regs_df.head()}")

        forecast_df = generate_forecast(series_id=request.series_id, horizon=request.horizon, future_regressors=future_regs_df)
        
        # Gerar insights derivados
        all_insights = []
        try:
            # Combinar insights de clima e feriados
            all_insights.extend(weather_insights)
            all_insights.extend(holiday_insights)
            
            # Gerar insights da previsão
            forecast_insights = insights_service.generate_forecast_insights(
                forecast_df=forecast_df,
                weather_insights=weather_insights,
                holiday_insights=holiday_insights
            )
            all_insights.extend(forecast_insights)
            
            # Formatar insights para o frontend
            formatted_insights = insights_service.format_insights_for_frontend(all_insights)
            print(f"📊 Total de insights gerados: {formatted_insights['total_insights']}")
            
        except Exception as e:
            print(f"⚠️  Erro ao gerar insights: {e}")
            formatted_insights = {"total_insights": 0, "insights": []}
        
        points: List[ForecastPoint] = [
            ForecastPoint(
                ds=str(row.ds),
                yhat=float(row.yhat),
                yhat_lower=float(row.yhat_lower) if not pd.isna(row.yhat_lower) else None,
                yhat_upper=float(row.yhat_upper) if not pd.isna(row.yhat_upper) else None,
            )
            for row in forecast_df.itertuples(index=False)
        ]
        
        # Criar resposta com insights
        response = ForecastResponse(series_id=request.series_id, forecast=points)
        # Adicionar insights como atributo adicional (será serializado pelo FastAPI)
        response.insights = formatted_insights
        return response
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Modelo não encontrado para esta série.")
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/models", response_model=ModelsResponse)
def models() -> ModelsResponse:
    models_list = list_available_models()
    return ModelsResponse(models=models_list)


@router.post("/train-external")
async def train_with_external(
    series_id: str = Form(...),
    latitude: float = Form(..., description="Latitude para clima"),
    longitude: float = Form(..., description="Longitude para clima"),
    start: str = Form(..., description="YYYY-MM-DD"),
    end: str = Form(..., description="YYYY-MM-DD"),
    file: UploadFile = File(..., description="CSV com ds,y e opcionalmente colunas adicionais"),
):
    """Treina mesclando regressors externos (clima + feriados) ao CSV enviado.

    - Clima diário (Open-Meteo): tmax, tmin, precip
    - Feriados (BrasilAPI): is_holiday
    """
    try:
        raw_bytes = await file.read()
        text_stream = io.StringIO(raw_bytes.decode("utf-8"))
        try:
            df = pd.read_csv(text_stream)
        except Exception:
            text_stream.seek(0)
            df = pd.read_csv(text_stream, sep=";")

        if "ds" not in df.columns or "y" not in df.columns:
            raise HTTPException(status_code=422, detail="CSV deve conter colunas 'ds' e 'y'.")

        from datetime import date
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)

        # Buscar dados climáticos históricos - MELHORADO
        weather_df = weather_service.get_weather_forecast(latitude, longitude, (end_date - start_date).days + 1)
        
        # Buscar feriados com efeito rebote - MELHORADO
        holidays_df, holiday_insights = holidays_service.create_enhanced_holiday_regressor(
            pd.Timestamp(start_date),
            pd.Timestamp(end_date)
        )
        
        # Buscar features de calendário - NOVO
        calendar_df = calendar_service.create_calendar_features(
            pd.Timestamp(start_date),
            pd.Timestamp(end_date)
        )

        # Mesclar todos os dados
        merged = (
            df.copy()
            .assign(ds=pd.to_datetime(df["ds"]))
            .merge(weather_df, on="ds", how="left")
            .merge(holidays_df, on="ds", how="left")
            .merge(calendar_df, on="ds", how="left")
        )
        
        # Preencher valores NaN
        merged["is_holiday"] = merged["is_holiday"].fillna(0)
        merged["after_holiday"] = merged["after_holiday"].fillna(0)
        merged["is_payday"] = merged["is_payday"].fillna(0)
        merged["month_end"] = merged["month_end"].fillna(0)
        merged["is_monday"] = merged["is_monday"].fillna(0)
        merged["is_friday"] = merged["is_friday"].fillna(0)
        merged["is_school_holiday"] = merged["is_school_holiday"].fillna(0)

        # Regressores melhorados para pronto-socorro
        regressors = [
            "tmax", "tmin", "precip",  # Clima
            "is_holiday", "after_holiday",  # Feriados + efeito rebote
            "is_payday", "month_end",  # Payday + fim de mês
            "is_monday", "is_friday", "is_school_holiday"  # Calendário
        ]

        train_and_persist_model(series_id=series_id, dataframe=merged, regressors=regressors)
        return {
            "status": "ok", 
            "series_id": series_id, 
            "regressors": regressors,
            "improvements": [
                "Efeito rebote pós-feriado (after_holiday)",
                "Flags payday e month_end",
                "Regressores climáticos melhorados",
                "Sazonalidade mais contida (additive)",
                "Changepoint mais conservador (0.01)",
                "Winsorize P1/P99 + 3-sigma"
            ]
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/backtest")
async def backtest_model(
    series_id: str = Form(...),
    file: UploadFile = File(..., description="CSV com ds,y para backtesting"),
    initial_days: int = Form(365, description="Dias iniciais para treinamento"),
    horizon_days: int = Form(30, description="Horizonte de previsão em dias"),
    period_days: int = Form(30, description="Período entre janelas em dias"),
    use_prophet_cv: bool = Form(False, description="Usar Prophet cross_validation nativo"),
):
    """Executa backtesting com validação cruzada"""
    try:
        raw_bytes = await file.read()
        text_stream = io.StringIO(raw_bytes.decode("utf-8"))
        try:
            df = pd.read_csv(text_stream)
        except Exception:
            text_stream.seek(0)
            df = pd.read_csv(text_stream, sep=";")

        if "ds" not in df.columns or "y" not in df.columns:
            raise HTTPException(status_code=422, detail="CSV deve conter colunas 'ds' e 'y'.")

        # Executar backtesting
        if use_prophet_cv:
            print(f"🔄 Usando Prophet cross_validation nativo...")
            results = backtesting_service.prophet_cross_validation(
                df, initial_days, horizon_days, period_days
            )
        else:
            print(f"🔄 Usando validação cruzada manual...")
            results = backtesting_service.rolling_cross_validation(
                df, initial_days, horizon_days, period_days
            )
        
        if not results:
            raise HTTPException(status_code=400, detail="Nenhum resultado de backtesting obtido")
        
        # Calcular métricas médias
        avg_metrics = {
            'smape': np.mean([r.smape for r in results]),
            'mae': np.mean([r.mae for r in results]),
            'rmse': np.mean([r.rmse for r in results]),
            'mape': np.mean([r.mape for r in results])
        }
        
        return {
            "status": "ok",
            "series_id": series_id,
            "method": "prophet_cv" if use_prophet_cv else "rolling_cv",
            "total_tests": len(results),
            "average_metrics": avg_metrics,
            "results": [
                {
                    "test_id": i,
                    "smape": r.smape,
                    "mae": r.mae,
                    "rmse": r.rmse,
                    "mape": r.mape,
                    "date_range": f"{r.dates[0]} a {r.dates[-1]}" if r.dates else ""
                }
                for i, r in enumerate(results)
            ]
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/grid-search")
async def grid_search_parameters(
    series_id: str = Form(...),
    file: UploadFile = File(..., description="CSV com ds,y para grid search"),
    optimization_method: str = Form("random", description="Método: grid, random, bayesian"),
    n_iterations: int = Form(15, description="Número de iterações para random/bayesian"),
    initial_days: int = Form(365, description="Dias iniciais para treinamento"),
    horizon_days: int = Form(30, description="Horizonte de previsão em dias"),
    period_days: int = Form(30, description="Período entre janelas em dias"),
):
    """Executa grid search para otimização de parâmetros"""
    try:
        raw_bytes = await file.read()
        text_stream = io.StringIO(raw_bytes.decode("utf-8"))
        try:
            df = pd.read_csv(text_stream)
        except Exception:
            text_stream.seek(0)
            df = pd.read_csv(text_stream, sep=";")

        if "ds" not in df.columns or "y" not in df.columns:
            raise HTTPException(status_code=422, detail="CSV deve conter colunas 'ds' e 'y'.")

        # Executar otimização baseada no método escolhido
        if optimization_method == "grid":
            results = backtesting_service.grid_search(
                df, None, initial_days, horizon_days, period_days
            )
        elif optimization_method == "random":
            results = backtesting_service.random_search(
                df, n_iterations, initial_days, horizon_days, period_days
            )
        elif optimization_method == "bayesian":
            results = backtesting_service.bayesian_optimization(
                df, n_iterations, initial_days, horizon_days, period_days
            )
        else:
            raise HTTPException(
                status_code=422,
                detail="Método deve ser: grid, random ou bayesian"
            )
        
        if not results:
            raise HTTPException(status_code=400, detail="Nenhum resultado de grid search obtido")
        
        # Pegar os 5 melhores resultados
        best_results = results[:5]
        
        # Obter resumo da otimização
        summary = backtesting_service.get_optimization_summary(results)
        
        return {
            "status": "ok",
            "series_id": series_id,
            "optimization_method": optimization_method,
            "total_combinations": len(results),
            "best_parameters": best_results[0].params,
            "best_metrics": {
                "smape": best_results[0].smape,
                "mae": best_results[0].mae,
                "rmse": best_results[0].rmse,
                "mape": best_results[0].mape
            },
            "optimization_summary": summary,
            "top_5_results": [
                {
                    "rank": i + 1,
                    "parameters": r.params,
                    "smape": r.smape,
                    "mae": r.mae,
                    "rmse": r.rmse,
                    "mape": r.mape
                }
                for i, r in enumerate(best_results)
            ]
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/baselines")
async def evaluate_baselines(
    series_id: str = Form(...),
    file: UploadFile = File(..., description="CSV com ds,y para avaliação de baselines"),
    horizon: int = Form(14, description="Horizonte de previsão em dias"),
    use_cross_validation: bool = Form(False, description="Usar validação cruzada"),
    initial_days: int = Form(365, description="Dias iniciais para treinamento (CV)"),
    horizon_days: int = Form(30, description="Horizonte de previsão em dias (CV)"),
    period_days: int = Form(30, description="Período entre janelas em dias (CV)"),
):
    """Avalia baselines de previsão"""
    try:
        raw_bytes = await file.read()
        text_stream = io.StringIO(raw_bytes.decode("utf-8"))
        try:
            df = pd.read_csv(text_stream)
        except Exception:
            text_stream.seek(0)
            df = pd.read_csv(text_stream, sep=";")

        if "ds" not in df.columns or "y" not in df.columns:
            raise HTTPException(status_code=422, detail="CSV deve conter colunas 'ds' e 'y'.")

        # Preparar dados
        df['ds'] = pd.to_datetime(df['ds'])
        df = df.sort_values('ds').reset_index(drop=True)
        
        # Avaliar baselines
        print(f"🔍 Debug - Avaliando baselines para horizonte {horizon}")
        print(f"🔍 Debug - Dados: {len(df)} linhas, período: {df['ds'].min()} a {df['ds'].max()}")
        
        if use_cross_validation:
            print(f"🔍 Debug - Usando validação cruzada")
            results = baseline_service.compare_all_baselines(
                df, horizon, use_cross_validation=True
            )
        else:
            print(f"🔍 Debug - Usando avaliação simples")
            results = baseline_service.compare_all_baselines(df, horizon)
        
        print(f"🔍 Debug - Resultados obtidos: {len(results) if results else 0}")
        
        if not results:
            raise HTTPException(status_code=400, detail="Nenhum baseline avaliado com sucesso")
        
        best_baseline = baseline_service.get_best_baseline(results)
        
        return {
            "status": "ok",
            "series_id": series_id,
            "horizon": horizon,
            "best_baseline": {
                "method": best_baseline.method,
                "smape": best_baseline.smape,
                "mae": best_baseline.mae,
                "rmse": best_baseline.rmse,
                "mape": best_baseline.mape
            },
            "all_baselines": [
                {
                    "method": r.method,
                    "smape": r.smape,
                    "mae": r.mae,
                    "rmse": r.rmse,
                    "mape": r.mape
                }
                for r in results
            ]
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/metrics")
async def calculate_metrics(
    series_id: str = Form(...),
    file: UploadFile = File(..., description="CSV com ds,y para cálculo de métricas"),
    actual_column: str = Form("y", description="Nome da coluna com valores reais"),
    predicted_column: str = Form("yhat", description="Nome da coluna com valores previstos"),
    seasonal_period: int = Form(7, description="Período sazonal para MASE"),
):
    """Calcula métricas detalhadas (MAPE, RMSE, sMAPE) para avaliação de previsões"""
    try:
        raw_bytes = await file.read()
        text_stream = io.StringIO(raw_bytes.decode("utf-8"))
        try:
            df = pd.read_csv(text_stream)
        except Exception:
            text_stream.seek(0)
            df = pd.read_csv(text_stream, sep=";")

        # Verificar colunas necessárias
        if actual_column not in df.columns:
            raise HTTPException(status_code=422, detail=f"Coluna '{actual_column}' não encontrada no CSV")
        
        if predicted_column not in df.columns:
            raise HTTPException(status_code=422, detail=f"Coluna '{predicted_column}' não encontrada no CSV")

        # Preparar dados
        actual = df[actual_column].dropna().values
        predicted = df[predicted_column].dropna().values
        
        if len(actual) == 0 or len(predicted) == 0:
            raise HTTPException(status_code=400, detail="Dados insuficientes para cálculo de métricas")
        
        # Garantir que os arrays tenham o mesmo tamanho
        min_length = min(len(actual), len(predicted))
        actual = actual[:min_length]
        predicted = predicted[:min_length]
        
        # Calcular métricas
        metrics_result = metrics_service.calculate_all_metrics(
            actual.tolist(), 
            predicted.tolist(), 
            seasonal_period
        )
        
        # Avaliar qualidade
        quality = metrics_service.evaluate_forecast_quality(metrics_result)
        
        # Gerar relatório
        report = metrics_service.generate_metrics_report(metrics_result, series_id)
        
        return {
            "status": "ok",
            "series_id": series_id,
            "metrics": {
                "mape": metrics_result.mape,
                "smape": metrics_result.smape,
                "rmse": metrics_result.rmse,
                "mae": metrics_result.mae,
                "mse": metrics_result.mse,
                "r2": metrics_result.r2,
                "bias": metrics_result.bias,
                "mase": metrics_result.mase
            },
            "quality_assessment": quality,
            "details": metrics_result.details,
            "report": report
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))



