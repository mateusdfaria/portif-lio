import io
import logging

import numpy as np
import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from schemas.forecast import (
    ForecastPoint,
    ForecastResponse,
    ModelsResponse,
    PredictRequest,
    TrainRequest,
)
from services.backtesting_service import backtesting_service
from services.baseline_service import baseline_service
from services.calendar_service import calendar_service
from services.ensemble_service import ensemble_service
from services.holidays_service import holidays_service
from services.hospital_account_service import hospital_account_service
from services.insights_service import insights_service
from services.metrics_service import metrics_service
from services.prophet_service import (
    generate_forecast,
    list_available_models,
    train_and_persist_model,
)
from services.weather_service import weather_service

router = APIRouter(prefix="/forecast", tags=["forecast"])
logger = logging.getLogger("hospicast")


def _ensure_dataframe_size(df: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """Garante que o DataFrame tenha exatamente o tamanho do horizonte."""
    if len(df) >= horizon:
        return df.head(horizon)
    
    # Se não tiver dados suficientes, duplicar o último
    last_row = df.iloc[-1].copy()
    while len(df) < horizon:
        df = pd.concat([df, last_row.to_frame().T], ignore_index=True)
    return df.head(horizon)


def _fill_default_weather_values(df: pd.DataFrame) -> pd.DataFrame:
    """Preenche valores padrão para variáveis climáticas."""
    df["tmax"] = df.get("tmax", 25.0)
    df["tmin"] = df.get("tmin", 15.0)
    df["precip"] = df.get("precip", 0.0)
    df["temp_avg"] = df.get("temp_avg", 20.0)
    df["temp_range"] = df.get("temp_range", 10.0)
    df["thermal_comfort"] = df.get("thermal_comfort", 1)
    df["respiratory_risk"] = df.get("respiratory_risk", 0)
    df["dehydration_risk"] = df.get("dehydration_risk", 0)
    df["accident_risk"] = df.get("accident_risk", 0)
    df["month"] = df.get("month", 1)
    df["is_winter"] = df.get("is_winter", 0)
    df["is_summer"] = df.get("is_summer", 0)
    return df.fillna({
        "tmax": 25.0,
        "tmin": 15.0,
        "precip": 0.0,
        "temp_avg": 20.0,
        "temp_range": 10.0,
        "thermal_comfort": 1,
        "respiratory_risk": 0,
        "dehydration_risk": 0,
        "accident_risk": 0,
        "month": 1,
        "is_winter": 0,
        "is_summer": 0,
    })


def _fill_default_holiday_values(df: pd.DataFrame) -> pd.DataFrame:
    """Preenche valores padrão para variáveis de feriados."""
    df["is_holiday"] = df.get("is_holiday", 0)
    df["is_extraordinary_event"] = df.get("is_extraordinary_event", 0)
    df["event_impact_factor"] = df.get("event_impact_factor", 1.0)
    df["is_holiday_weekend"] = df.get("is_holiday_weekend", 0)
    df["is_holiday_monday"] = df.get("is_holiday_monday", 0)
    return df.fillna({
        "is_holiday": 0,
        "is_extraordinary_event": 0,
        "event_impact_factor": 1.0,
        "is_holiday_weekend": 0,
        "is_holiday_monday": 0,
    })


def _fix_nan_values(df: pd.DataFrame) -> pd.DataFrame:
    """Corrige valores NaN no DataFrame."""
    nan_columns = df.columns[df.isnull().any()].tolist()
    if not nan_columns:
        return df
    
    logger.warning("Colunas com NaN: %s", nan_columns)
    for col in nan_columns:
        logger.debug("%s: %d valores NaN", col, df[col].isnull().sum())
        
        if col in ['is_winter', 'is_summer', 'is_holiday', 'is_extraordinary_event', 
                   'is_holiday_weekend', 'is_holiday_monday']:
            df[col] = df[col].fillna(0)
        elif col in ['thermal_comfort', 'respiratory_risk', 'dehydration_risk', 'accident_risk']:
            df[col] = df[col].fillna(0)
        elif col == 'month':
            df[col] = df[col].fillna(1)
        elif col == 'event_impact_factor':
            df[col] = df[col].fillna(1.0)
        else:
            df[col] = df[col].fillna(0)
    
    return df


def _create_default_regressors(start_date: pd.Timestamp, horizon: int) -> pd.DataFrame:
    """Cria regressores padrão quando não há dados externos."""
    df = pd.DataFrame({
        "ds": pd.date_range(start=start_date, periods=horizon, freq="D")
    })
    df["tmax"] = 25.0
    df["tmin"] = 15.0
    df["precip"] = 0.0
    df["temp_avg"] = 20.0
    df["temp_range"] = 10.0
    df["thermal_comfort"] = 1
    df["respiratory_risk"] = 0
    df["dehydration_risk"] = 0
    df["accident_risk"] = 0
    df["month"] = 1
    df["is_winter"] = 0
    df["is_summer"] = 0
    df["is_holiday"] = 0
    return df


def _prepare_weather_regressors(
    latitude: float,
    longitude: float,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    horizon: int
) -> tuple[pd.DataFrame | None, list]:
    """Prepara regressores climáticos."""
    try:
        logger.info("Buscando dados climáticos para %d dias", horizon)
        weather_df, weather_insights = weather_service.get_enhanced_weather_forecast(
            latitude, longitude, horizon
        )
        logger.info("Dados climáticos aprimorados: %d registros", 
                   len(weather_df) if weather_df is not None else 0)
        logger.info("Insights climáticos: %d encontrados", len(weather_insights))
        return weather_df, weather_insights
    except Exception as e:
        logger.warning("Erro ao buscar dados climáticos: %s", e)
        return None, []


def _prepare_holiday_regressors(
    start_date: pd.Timestamp,
    end_date: pd.Timestamp
) -> tuple[pd.DataFrame | None, list]:
    """Prepara regressores de feriados."""
    try:
        logger.info("Buscando feriados aprimorados para o período")
        holidays_df, holiday_insights = holidays_service.create_enhanced_holiday_regressor(
            start_date, end_date
        )
        logger.info("Insights de feriados: %d encontrados", len(holiday_insights))
        return holidays_df, holiday_insights
    except Exception as e:
        logger.warning("Erro ao buscar feriados: %s", e)
        return None, []


def _build_future_regressors(
    latitude: float,
    longitude: float,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    horizon: int
) -> tuple[pd.DataFrame, list, list]:
    """Constrói DataFrame de regressores futuros com clima e feriados."""
    # Buscar dados externos
    weather_df, weather_insights = _prepare_weather_regressors(
        latitude, longitude, start_date, end_date, horizon
    )
    holidays_df, holiday_insights = _prepare_holiday_regressors(start_date, end_date)
    
    # Criar DataFrame base
    future_regs_df = pd.DataFrame({
        "ds": pd.date_range(start=start_date, periods=horizon, freq="D")
    })
    
    # Adicionar dados climáticos
    if weather_df is not None and not weather_df.empty:
        weather_df = _ensure_dataframe_size(weather_df, horizon)
        future_regs_df = future_regs_df.merge(weather_df, on="ds", how="left")
        future_regs_df = _fill_default_weather_values(future_regs_df)
    else:
        future_regs_df = _fill_default_weather_values(future_regs_df)
    
    # Adicionar feriados
    if holidays_df is not None and not holidays_df.empty:
        holidays_df = _ensure_dataframe_size(holidays_df, horizon)
        future_regs_df = future_regs_df.merge(holidays_df, on="ds", how="left")
        future_regs_df = _fill_default_holiday_values(future_regs_df)
    else:
        future_regs_df = _fill_default_holiday_values(future_regs_df)
    
    # Garantir tamanho correto e corrigir NaN
    future_regs_df = future_regs_df.head(horizon)
    future_regs_df = _fix_nan_values(future_regs_df)
    
    logger.debug("Regressores criados: %s", list(future_regs_df.columns))
    logger.debug("Tamanho do DataFrame: %d linhas, horizonte: %d", len(future_regs_df), horizon)
    
    return future_regs_df, weather_insights, holiday_insights


def _convert_numpy_value(value) -> float | int | None:
    """Converte valores numpy para tipos Python nativos."""
    if pd.isna(value):
        return None
    if hasattr(value, 'item'):
        return value.item()
    if isinstance(value, (np.integer, np.int64, np.int32)):
        return int(value)
    if isinstance(value, (np.floating, np.float64, np.float32)):
        return float(value)
    return float(value) if value is not None else None


def _generate_insights(
    forecast_df: pd.DataFrame,
    weather_insights: list,
    holiday_insights: list
) -> dict:
    """Gera insights derivados da previsão."""
    try:
        all_insights = []
        all_insights.extend(weather_insights)
        all_insights.extend(holiday_insights)
        
        forecast_insights = insights_service.generate_forecast_insights(
            forecast_df=forecast_df,
            weather_insights=weather_insights,
            holiday_insights=holiday_insights
        )
        all_insights.extend(forecast_insights)
        
        formatted_insights = insights_service.format_insights_for_frontend(all_insights)
        logger.info("Total de insights gerados: %d", formatted_insights['total_insights'])
        return formatted_insights
    except Exception as e:
        logger.warning("Erro ao gerar insights: %s", e)
        return {"total_insights": 0, "insights": []}


def _convert_forecast_to_points(forecast_df: pd.DataFrame) -> list[ForecastPoint]:
    """Converte DataFrame de previsão para lista de ForecastPoint."""
    return [
        ForecastPoint(
            ds=str(row.ds),
            yhat=_convert_numpy_value(row.yhat),
            yhat_lower=_convert_numpy_value(row.yhat_lower),
            yhat_upper=_convert_numpy_value(row.yhat_upper),
        )
        for row in forecast_df.itertuples(index=False)
    ]


def decode_file_bytes(raw_bytes: bytes) -> str:
    """Decodifica bytes de arquivo tentando múltiplos encodings.
    
    Tenta em ordem: UTF-8, ISO-8859-1 (Latin-1), Windows-1252.
    Esses são os encodings mais comuns para arquivos CSV brasileiros.
    """
    encodings = ["utf-8", "iso-8859-1", "windows-1252", "latin1"]
    
    for encoding in encodings:
        try:
            return raw_bytes.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    
    # Se nenhum encoding funcionou, tentar UTF-8 com tratamento de erros
    return raw_bytes.decode("utf-8", errors="replace")


def detect_csv_separator(text_content: str) -> str:
    """Detecta o separador do CSV (; ou ,) verificando a primeira linha."""
    # Normalizar quebras de linha
    lines = text_content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    if not lines:
        return ','  # padrão
    
    first_line = lines[0].strip()
    if not first_line:
        # Se primeira linha vazia, tentar segunda
        first_line = lines[1].strip() if len(lines) > 1 else ''
    
    # Contar ocorrências de cada separador
    semicolon_count = first_line.count(';')
    comma_count = first_line.count(',')
    
    # Se tem ponto e vírgula e tem mais ou igual que vírgulas, usar ponto e vírgula
    if semicolon_count > 0 and semicolon_count >= comma_count:
        return ';'
    elif comma_count > 0:
        return ','
    else:
        # Tentar detectar olhando múltiplas linhas
        for line in lines[:5]:  # Verificar primeiras 5 linhas
            if ';' in line:
                return ';'
            if ',' in line:
                return ','
        return ','  # padrão


@router.post("/train")
def train(request: TrainRequest):
    try:
        records: list[dict] = [item.dict() for item in request.data]
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
        # Validar arquivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Arquivo não fornecido")
        
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Arquivo deve ser CSV (.csv)")
        
        # Ler arquivo
        raw_bytes = await file.read()
        if len(raw_bytes) == 0:
            raise HTTPException(status_code=400, detail="Arquivo vazio")
        
        # Decodificar com suporte a múltiplos encodings
        text_content = decode_file_bytes(raw_bytes)
        
        # Detectar separador automaticamente
        sep = detect_csv_separator(text_content)
        
        # Ler CSV com o separador detectado
        text_stream = io.StringIO(text_content)
        dataframe = pd.read_csv(text_stream, sep=sep)

        # Validar colunas
        if "ds" not in dataframe.columns or "y" not in dataframe.columns:
            raise HTTPException(
                status_code=422,
                detail=f"CSV deve conter colunas 'ds' (data) e 'y' (valor). Colunas encontradas: {list(dataframe.columns)}",
            )
        
        # Validar dados
        if len(dataframe) == 0:
            raise HTTPException(status_code=422, detail="CSV não contém dados")
        
        # Converter coluna ds para datetime
        dataframe['ds'] = pd.to_datetime(dataframe['ds'], errors='coerce')
        if dataframe['ds'].isna().any():
            raise HTTPException(status_code=422, detail="Coluna 'ds' contém datas inválidas")
        
        # Validar coluna y
        dataframe['y'] = pd.to_numeric(dataframe['y'], errors='coerce')
        if dataframe['y'].isna().any():
            raise HTTPException(status_code=422, detail="Coluna 'y' contém valores não numéricos")

        # Treinar modelo
        train_and_persist_model(series_id=series_id, dataframe=dataframe, regressors=[])
        return {"status": "ok", "series_id": series_id, "rows": len(dataframe)}
    except HTTPException:
        raise
    except (ValueError, pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        logger.error("Erro ao processar arquivo CSV: %s", exc, exc_info=True)
        raise HTTPException(status_code=400, detail=f"Erro ao processar arquivo: {str(exc)}")
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.exception("Erro inesperado ao treinar modelo")
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(exc)}")


@router.post("/predict-ensemble")
async def predict_ensemble(request: PredictRequest):
    """Previsão usando ensemble Prophet + Naive Semanal"""
    try:
        # Buscar dados históricos para Naive Semanal

        from services.prophet_service import _get_model_path
        
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
    """Gera previsão usando modelo Prophet com regressores externos."""
    try:
        future_regs_df = None
        weather_insights = []
        holiday_insights = []
        
        # Habilitar regressores externos se coordenadas fornecidas
        if request.latitude is not None and request.longitude is not None:
            from datetime import timedelta
            start_date = pd.Timestamp.today().normalize().date()
            end_date = start_date + timedelta(days=request.horizon - 1)
            
            try:
                future_regs_df, weather_insights, holiday_insights = _build_future_regressors(
                    request.latitude,
                    request.longitude,
                    pd.Timestamp(start_date),
                    pd.Timestamp(end_date),
                    request.horizon
                )
            except Exception as e:
                logger.warning("Erro ao buscar dados externos: %s", e)
                future_regs_df = _create_default_regressors(pd.Timestamp(start_date), request.horizon)

        logger.debug("Horizon: %d", request.horizon)
        logger.debug("Future regressors shape: %s", future_regs_df.shape if future_regs_df is not None else 'None')
        if future_regs_df is not None:
            logger.debug("Future regressors columns: %s", list(future_regs_df.columns))

        forecast_df = generate_forecast(
            series_id=request.series_id,
            horizon=request.horizon,
            future_regressors=future_regs_df
        )
        
        # Gerar insights derivados
        formatted_insights = _generate_insights(forecast_df, weather_insights, holiday_insights)
        
        # Converter previsão para pontos
        points = _convert_forecast_to_points(forecast_df)
        
        # Criar resposta com insights
        response = ForecastResponse(series_id=request.series_id, forecast=points)
        response.insights = formatted_insights

        if request.hospital_id or request.session_token:
            if not request.hospital_id or not request.session_token:
                raise HTTPException(
                    status_code=401,
                    detail="Forneça hospital_id e session_token para salvar histórico.",
                )
            if not hospital_account_service.validate_session(request.hospital_id, request.session_token):
                raise HTTPException(status_code=401, detail="Sessão do hospital expirada ou inválida.")

            avg_yhat = float(sum(point.yhat for point in points) / len(points)) if points else None
            hospital_account_service.record_forecast(
                hospital_id=request.hospital_id,
                series_id=request.series_id,
                horizon=request.horizon,
                forecast_payload=response.dict(),
                avg_yhat=avg_yhat,
            )

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
        text_stream = io.StringIO(decode_file_bytes(raw_bytes))
        try:
            df = pd.read_csv(text_stream)
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
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
        text_stream = io.StringIO(decode_file_bytes(raw_bytes))
        try:
            df = pd.read_csv(text_stream)
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
            text_stream.seek(0)
            df = pd.read_csv(text_stream, sep=";")

        if "ds" not in df.columns or "y" not in df.columns:
            raise HTTPException(status_code=422, detail="CSV deve conter colunas 'ds' e 'y'.")

        # Executar backtesting
        if use_prophet_cv:
            logger.info("Usando Prophet cross_validation nativo")
            results = backtesting_service.prophet_cross_validation(
                df, initial_days, horizon_days, period_days
            )
        else:
            logger.info("Usando validação cruzada manual")
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
        text_stream = io.StringIO(decode_file_bytes(raw_bytes))
        try:
            df = pd.read_csv(text_stream)
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
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
        text_stream = io.StringIO(decode_file_bytes(raw_bytes))
        try:
            df = pd.read_csv(text_stream)
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
            text_stream.seek(0)
            df = pd.read_csv(text_stream, sep=";")

        if "ds" not in df.columns or "y" not in df.columns:
            raise HTTPException(status_code=422, detail="CSV deve conter colunas 'ds' e 'y'.")

        # Preparar dados
        df['ds'] = pd.to_datetime(df['ds'])
        df = df.sort_values('ds').reset_index(drop=True)
        
        # Avaliar baselines
        logger.debug("Avaliando baselines para horizonte %d", horizon)
        logger.debug("Dados: %d linhas, período: %s a %s", len(df), df['ds'].min(), df['ds'].max())
        
        if use_cross_validation:
            logger.debug("Usando validação cruzada")
            results = baseline_service.compare_all_baselines(
                df, horizon, use_cross_validation=True
            )
        else:
            logger.debug("Usando avaliação simples")
            results = baseline_service.compare_all_baselines(df, horizon)
        
        logger.debug("Resultados obtidos: %d", len(results) if results else 0)
        
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


@router.post("/compare-predictions")
async def compare_predictions(
    series_id: str = Form(...),
    file: UploadFile = File(..., description="CSV com ds,y (valores reais) para comparar com previsões"),
    start_date: str = Form(None, description="Data inicial (YYYY-MM-DD) - opcional"),
    end_date: str = Form(None, description="Data final (YYYY-MM-DD) - opcional"),
):
    """Compara previsões salvas com valores reais fornecidos"""
    try:
        # Ler arquivo com valores reais
        raw_bytes = await file.read()
        if len(raw_bytes) == 0:
            raise HTTPException(status_code=400, detail="Arquivo vazio")
        
        text_content = decode_file_bytes(raw_bytes)
        sep = detect_csv_separator(text_content)
        text_stream = io.StringIO(text_content)
        actual_df = pd.read_csv(text_stream, sep=sep)
        
        # Validar colunas
        if "ds" not in actual_df.columns or "y" not in actual_df.columns:
            raise HTTPException(
                status_code=422,
                detail=f"CSV deve conter colunas 'ds' (data) e 'y' (valor real). Colunas encontradas: {list(actual_df.columns)}"
            )
        
        # Converter datas e valores
        actual_df['ds'] = pd.to_datetime(actual_df['ds'], errors='coerce')
        actual_df['y'] = pd.to_numeric(actual_df['y'], errors='coerce')
        
        # Filtrar por datas se fornecidas
        if start_date:
            start = pd.to_datetime(start_date)
            actual_df = actual_df[actual_df['ds'] >= start]
        if end_date:
            end = pd.to_datetime(end_date)
            actual_df = actual_df[actual_df['ds'] <= end]
        
        if len(actual_df) == 0:
            raise HTTPException(status_code=422, detail="Nenhum dado encontrado no período especificado")
        
        # Buscar previsões usando a função existente
        from services.prophet_service import _get_model_path
        import joblib
        
        model_path = _get_model_path(series_id)
        if not model_path.exists():
            raise HTTPException(status_code=404, detail=f"Modelo '{series_id}' não encontrado. Treine o modelo primeiro.")
        
        # Carregar modelo
        model = joblib.load(model_path)
        
        # Criar DataFrame futuro com as datas dos valores reais
        future = pd.DataFrame({'ds': actual_df['ds']})
        
        # Adicionar regressores se o modelo tiver
        if hasattr(model, 'extra_regressors') and model.extra_regressors:
            # Para simplificar, vamos usar valores padrão para regressores
            # Em produção, você deveria buscar os valores reais dos regressores
            for regressor_name in model.extra_regressors.keys():
                future[regressor_name] = 0.0
        
        # Gerar previsões
        forecast = model.predict(future)
        
        # Combinar valores reais e previstos
        comparison_df = pd.DataFrame({
            'ds': actual_df['ds'],
            'actual': actual_df['y'],
            'predicted': forecast['yhat'].values,
            'predicted_lower': forecast['yhat_lower'].values if 'yhat_lower' in forecast.columns else None,
            'predicted_upper': forecast['yhat_upper'].values if 'yhat_upper' in forecast.columns else None,
        })
        
        # Calcular métricas
        actual_values = comparison_df['actual'].dropna().values
        predicted_values = comparison_df['predicted'].dropna().values
        
        if len(actual_values) == 0 or len(predicted_values) == 0:
            raise HTTPException(status_code=422, detail="Dados insuficientes para comparação")
        
        min_length = min(len(actual_values), len(predicted_values))
        actual_values = actual_values[:min_length]
        predicted_values = predicted_values[:min_length]
        
        # Calcular métricas usando o serviço existente
        metrics_result = metrics_service.calculate_all_metrics(
            actual_values.tolist(),
            predicted_values.tolist(),
            seasonal_period=7
        )
        
        quality = metrics_service.evaluate_forecast_quality(metrics_result)
        
        # Preparar dados para visualização
        comparison_data = comparison_df.to_dict('records')
        
        return {
            "status": "ok",
            "series_id": series_id,
            "period": {
                "start": str(comparison_df['ds'].min()),
                "end": str(comparison_df['ds'].max()),
                "days": len(comparison_df)
            },
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
            "comparison_data": comparison_data,
            "summary": {
                "total_points": len(comparison_df),
                "avg_actual": float(actual_values.mean()),
                "avg_predicted": float(predicted_values.mean()),
                "avg_error": float((actual_values - predicted_values).mean()),
                "avg_abs_error": float(np.abs(actual_values - predicted_values).mean())
            }
        }
    except HTTPException:
        raise
    except (ValueError, pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        logger.error("Erro ao processar dados para comparação: %s", exc, exc_info=True)
        raise HTTPException(status_code=400, detail=f"Erro ao processar dados: {str(exc)}")
    except Exception as exc:
        logger.exception("Erro inesperado ao comparar previsões")
        raise HTTPException(status_code=500, detail=f"Erro ao comparar previsões: {str(exc)}")


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
        text_stream = io.StringIO(decode_file_bytes(raw_bytes))
        try:
            df = pd.read_csv(text_stream)
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
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



