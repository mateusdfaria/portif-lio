from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import joblib
import pandas as pd
import numpy as np

try:
    from prophet import Prophet  # type: ignore
except Exception:  # pragma: no cover - fallback for older envs
    try:  # pragma: no cover
        from fbprophet import Prophet  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Prophet não está instalado.") from exc


def _get_models_dir() -> Path:
    base_dir = Path(__file__).resolve().parents[1]
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def _get_model_path(series_id: str) -> Path:
    return _get_models_dir() / f"{series_id}.joblib"


def _prepare_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()
    if "ds" not in df.columns or "y" not in df.columns:
        raise ValueError("DataFrame deve conter colunas 'ds' e 'y'.")
    df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
    if df["ds"].isna().any():
        raise ValueError("Coluna 'ds' possui datas inválidas.")
    
    # Converter y para numérico
    df["y"] = pd.to_numeric(df["y"], errors="coerce")
    if df["y"].isna().any():
        raise ValueError("Coluna 'y' possui valores não numéricos.")
    
    # Detectar se os dados são cumulativos e converter para valores diários
    y_series = df["y"].astype(float)
    
    # Verificar se é cumulativo (monótono crescente com diferenças positivas)
    is_monotonic_increasing = y_series.is_monotonic_increasing
    differences = y_series.diff().dropna()
    
    # Critérios mais rigorosos para detectar dados cumulativos
    if is_monotonic_increasing and len(differences) > 0:
        # Calcular estatísticas das diferenças
        median_diff = differences.median()
        mean_diff = differences.mean()
        positive_diff_ratio = (differences > 0).sum() / len(differences)
        
        # Critérios para detectar dados cumulativos:
        # 1. Mediana positiva
        # 2. Pelo menos 80% das diferenças são positivas
        # 3. Mediana > 1% do valor máximo
        is_cumulative = (
            median_diff > 0 and 
            positive_diff_ratio > 0.8 and 
            median_diff > (y_series.max() * 0.01)
        )
        
        if is_cumulative:
            print(f"⚠️  Dados detectados como cumulativos. Convertendo para valores diários...")
            print(f"   Diferença mediana: {median_diff:.2f}")
            print(f"   Diferença média: {mean_diff:.2f}")
            print(f"   % diferenças positivas: {positive_diff_ratio:.1%}")
            
            # Converter para valores diários usando diferença
            daily_values = y_series.diff().fillna(y_series.iloc[0])
            
            # Tratar valores negativos (pode acontecer em casos de ajustes)
            # Se houver valores negativos, substituir por 0
            negative_count = (daily_values < 0).sum()
            if negative_count > 0:
                print(f"   ⚠️  {negative_count} valores negativos encontrados. Substituindo por 0.")
                daily_values = daily_values.clip(lower=0)
            
            # Se muitos valores ficaram zero, usar o valor original
            zero_ratio = (daily_values == 0).sum() / len(daily_values)
            if zero_ratio > 0.3:  # Mais de 30% zeros
                print(f"   ⚠️  {zero_ratio:.1%} valores zero após conversão. Mantendo dados originais.")
            else:
                df["y"] = daily_values
                print(f"   ✅ Conversão concluída. Valores diários calculados.")
                print(f"   📊 Estatísticas pós-conversão: min={daily_values.min():.2f}, max={daily_values.max():.2f}, média={daily_values.mean():.2f}")
    
    # Limpeza de outliers usando Winsorization (P1-P99) - MELHORADO
    print(f"🔍 Limpeza de outliers...")
    original_count = len(df)
    y_values = df["y"].values
    
    # Calcular percentis
    p1 = np.percentile(y_values, 1)
    p99 = np.percentile(y_values, 99)
    
    # Calcular limites usando 3-sigma também
    mean_val = np.mean(y_values)
    std_val = np.std(y_values)
    sigma_lower = mean_val - 3 * std_val
    sigma_upper = mean_val + 3 * std_val
    
    # Usar o método mais conservador (P1/P99 ou 3-sigma)
    final_lower = max(p1, sigma_lower)
    final_upper = min(p99, sigma_upper)
    
    # Winsorize outliers
    df["y"] = df["y"].clip(lower=final_lower, upper=final_upper)
    
    outliers_removed = original_count - len(df[df["y"] != y_values])
    if outliers_removed > 0:
        print(f"   ⚠️  {outliers_removed} outliers removidos (P1={p1:.2f}, P99={p99:.2f}, 3σ={sigma_lower:.2f}-{sigma_upper:.2f})")
        print(f"   📊 Limites finais: {final_lower:.2f} - {final_upper:.2f}")
    
    # Adicionar features de calendário úteis
    df["year"] = df["ds"].dt.year
    df["month"] = df["ds"].dt.month
    df["day_of_week"] = df["ds"].dt.dayofweek
    df["day_of_year"] = df["ds"].dt.dayofyear
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    
    # Adicionar sazonalidade de inverno (maio-setembro no Brasil)
    df["is_winter"] = df["month"].isin([5, 6, 7, 8, 9]).astype(int)
    
    print(f"✅ Dados preparados: {len(df)} registros, período: {df['ds'].min()} a {df['ds'].max()}")
    
    df = df.sort_values("ds").reset_index(drop=True)
    return df


def train_and_persist_model(series_id: str, dataframe: pd.DataFrame, regressors: List[str]) -> None:
    df = _prepare_dataframe(dataframe)

    # Calcular cap baseado no P95 histórico
    y_values = df['y'].values
    p95 = np.percentile(y_values, 95)
    p99 = np.percentile(y_values, 99)
    max_val = y_values.max()
    
    # Cap mais conservador: P99 ou 1.5x do máximo, o que for maior
    cap_value = max(p99, max_val * 1.5)
    
    # Floor baseado no P5 para evitar valores muito baixos
    p5 = np.percentile(y_values, 5)
    floor_value = max(0, p5 * 0.5)  # 50% do P5, mas nunca negativo
    
    print(f"📊 Estatísticas dos dados:")
    print(f"   P5: {p5:.2f}")
    print(f"   P95: {p95:.2f}")
    print(f"   P99: {p99:.2f}")
    print(f"   Máximo histórico: {max_val:.2f}")
    print(f"   Cap definido: {cap_value:.2f}")
    print(f"   Floor definido: {floor_value:.2f}")
    
    # Adicionar coluna cap e floor para growth logistic
    df['cap'] = cap_value
    df['floor'] = floor_value

    # Detectar tipo de dados e escolher growth apropriado
    y_values = df['y'].values
    y_range = y_values.max() - y_values.min()
    y_mean = y_values.mean()
    
    # Para dados de pronto socorro (valores diários), usar growth linear
    # Growth logistic é melhor para dados cumulativos ou com limites claros
    use_logistic = y_range > y_mean * 2  # Se a variação for muito grande
    
    # Configuração otimizada para pronto-socorro
    if use_logistic:
        print(f"📊 Usando growth logistic (variação alta: {y_range:.2f})")
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode="additive",  # Evita "inflar" picos
            changepoint_prior_scale=0.01,  # Mais conservador para frear mudanças bruscas
            seasonality_prior_scale=5,
            growth="logistic",
            changepoint_range=0.8,
            n_changepoints=25,
        )
    else:
        print(f"📊 Usando growth linear (dados diários normais: variação {y_range:.2f})")
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode="additive",  # Evita "inflar" picos
            changepoint_prior_scale=0.01,  # Mais conservador para frear mudanças bruscas
            seasonality_prior_scale=5,
            growth="linear",  # Melhor para dados diários como pronto socorro
            changepoint_range=0.8,
            n_changepoints=25,
        )

    # Adicionar regressores externos (clima, feriados, etc.)
    external_regressors = []
    for regressor_name in regressors:
        if regressor_name in df.columns:
            # Verificar se há valores NaN no regressor
            if df[regressor_name].isnull().any():
                print(f"⚠️  Valores NaN encontrados em {regressor_name}, preenchendo com 0")
                df[regressor_name] = df[regressor_name].fillna(0)
            model.add_regressor(regressor_name, standardize=True)
            external_regressors.append(regressor_name)
            print(f"✅ Regressor externo adicionado: {regressor_name}")
    
    # Adicionar regressores de calendário automaticamente - MELHORADO
    calendar_regressors = ["is_weekend", "is_winter", "day_of_week", "is_payday", "month_end", 
                          "is_monday", "is_friday", "is_school_holiday"]
    for regressor_name in calendar_regressors:
        if regressor_name in df.columns:
            model.add_regressor(regressor_name, standardize=True)
            print(f"✅ Regressor de calendário adicionado: {regressor_name}")
    
    # Adicionar regressores climáticos avançados se disponíveis - MELHORADO
    climate_regressors = ["tmax", "tmin", "precip", "temp_avg", "temp_range", 
                         "thermal_comfort", "respiratory_risk", "dehydration_risk", "accident_risk"]
    for regressor_name in climate_regressors:
        if regressor_name in df.columns:
            if df[regressor_name].isnull().any():
                df[regressor_name] = df[regressor_name].fillna(0)
            model.add_regressor(regressor_name, standardize=True)
            print(f"✅ Regressor climático adicionado: {regressor_name}")
    
    # Adicionar regressores de feriados avançados se disponíveis - MELHORADO
    holiday_regressors = ["is_holiday", "is_extraordinary_event", "after_holiday", "event_impact_factor", 
                         "is_holiday_weekend", "is_holiday_monday"]
    for regressor_name in holiday_regressors:
        if regressor_name in df.columns:
            if df[regressor_name].isnull().any():
                df[regressor_name] = df[regressor_name].fillna(0)
            model.add_regressor(regressor_name, standardize=True)
            print(f"✅ Regressor de feriados adicionado: {regressor_name}")
    
    print(f"📊 Total de regressores adicionados: {len(external_regressors) + len(calendar_regressors) + len([r for r in climate_regressors if r in df.columns]) + len([r for r in holiday_regressors if r in df.columns])}")

    # Verificar se CmdStan está disponível antes de treinar
    try:
        import cmdstanpy
        print("✅ CmdStan disponível")
    except ImportError:
        print("⚠️  CmdStan não está disponível. Tentando continuar mesmo assim...")
    
    print(f"🔄 Iniciando treinamento do modelo Prophet...")
    try:
        model.fit(df)
        print(f"✅ Modelo treinado com sucesso!")
    except Exception as e:
        import traceback
        error_msg = f"Erro ao treinar modelo Prophet: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg) from e

    model_path = _get_model_path(series_id)
    joblib.dump(model, model_path)


def generate_forecast(series_id: str, horizon: int, future_regressors: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    model_path = _get_model_path(series_id)
    if not model_path.exists():
        raise FileNotFoundError(f"Modelo '{series_id}' não encontrado.")
    
    model: Prophet = joblib.load(model_path)
    future = model.make_future_dataframe(periods=horizon)
    
    # Adicionar features de calendário para o futuro
    future["year"] = future["ds"].dt.year
    future["month"] = future["ds"].dt.month
    future["day_of_week"] = future["ds"].dt.dayofweek
    future["day_of_year"] = future["ds"].dt.dayofyear
    future["is_weekend"] = (future["day_of_week"] >= 5).astype(int)
    future["is_winter"] = future["month"].isin([5, 6, 7, 8, 9]).astype(int)
    
    # Adicionar cap e floor apenas se o modelo usar growth logistic
    if hasattr(model, 'growth') and model.growth == 'logistic':
        # Usar o mesmo cap do treinamento (salvo no modelo)
        if hasattr(model, 'cap') and model.cap is not None:
            future['cap'] = model.cap
            future['floor'] = 0
        else:
            # Fallback: usar cap padrão baseado no horizonte
            try:
                # Cap padrão baseado no horizonte (mais conservador)
                cap_value = 50 + (horizon * 2)  # Cap dinâmico baseado no horizonte
                future['cap'] = cap_value
                future['floor'] = 0
                print(f"📊 Cap padrão para previsão: {cap_value:.2f}")
            except Exception as e:
                print(f"⚠️  Erro ao definir cap: {e}")
                future['cap'] = 100
                future['floor'] = 0
    else:
        print(f"📊 Usando growth linear - sem cap/floor")
    
    # Se o modelo tem regressores mas não foram fornecidos, criar valores padrão
    if future_regressors is None and hasattr(model, 'extra_regressors') and model.extra_regressors:
        # Preencher somente as últimas linhas (horizonte futuro)
        future_tail_idx = future.index[-horizon:]
        # Criar regressores padrão para o futuro
        for regressor in model.extra_regressors:
            if regressor not in future.columns:
                future[regressor] = np.nan
            if regressor == 'tmax':
                future.loc[future_tail_idx, 'tmax'] = 25.0  # temperatura máxima média
            elif regressor == 'tmin':
                future.loc[future_tail_idx, 'tmin'] = 15.0  # temperatura mínima média
            elif regressor == 'precip':
                future.loc[future_tail_idx, 'precip'] = 0.0  # sem precipitação
            elif regressor == 'is_holiday':
                future.loc[future_tail_idx, 'is_holiday'] = 0  # não é feriado
    
    elif future_regressors is not None:
        print(f"🔍 Debug - Future regressors received: {future_regressors.shape}")
        print(f"🔍 Debug - Future regressors columns: {list(future_regressors.columns)}")
        print(f"🔍 Debug - Horizon: {horizon}")
        
        # Verificar e corrigir valores NaN nos regressores futuros
        print(f"🔍 Verificando NaN nos regressores futuros:")
        nan_columns = future_regressors.columns[future_regressors.isnull().any()].tolist()
        if nan_columns:
            print(f"⚠️  Colunas com NaN nos regressores futuros: {nan_columns}")
            for col in nan_columns:
                print(f"   {col}: {future_regressors[col].isnull().sum()} valores NaN")
                future_regressors[col] = future_regressors[col].fillna(0)
        
        # Garantir que os regressores tenham o tamanho correto
        for col in future_regressors.columns:
            if col in {"tmax", "tmin", "precip", "is_holiday", "is_weekend", "is_winter", "day_of_week"}:
                values = future_regressors[col].values
                print(f"🔍 Debug - Regressor {col}: {len(values)} values, horizon: {horizon}")
                # Normalizar para ter exatamente 'horizon' valores
                if len(values) < horizon:
                    last_value = values[-1] if len(values) > 0 else 0.0
                    values = np.concatenate([values, np.full(horizon - len(values), last_value)])
                elif len(values) > horizon:
                    values = values[-horizon:]
                # Garantir a coluna e atribuir apenas no futuro (últimas linhas)
                if col not in future.columns:
                    future[col] = np.nan
                future_tail_idx = future.index[-horizon:]
                future.loc[future_tail_idx, col] = values
                print(f"🔍 Debug - Final regressor {col} length on tail: {len(values)}")
    
    forecast = model.predict(future)
    forecast_result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(horizon)
    
    # Validar e corrigir previsões negativas ou irreais
    print(f"🔍 Validando previsões...")
    
    # Garantir que yhat não seja negativo
    negative_count = (forecast_result['yhat'] < 0).sum()
    if negative_count > 0:
        print(f"⚠️  {negative_count} previsões negativas encontradas. Corrigindo para 0.")
        forecast_result['yhat'] = forecast_result['yhat'].clip(lower=0)
    
    # Garantir que yhat_lower não seja negativo
    if 'yhat_lower' in forecast_result.columns:
        negative_lower = (forecast_result['yhat_lower'] < 0).sum()
        if negative_lower > 0:
            print(f"⚠️  {negative_lower} limites inferiores negativos. Corrigindo para 0.")
            forecast_result['yhat_lower'] = forecast_result['yhat_lower'].clip(lower=0)
    
    # Garantir que yhat_upper não seja negativo
    if 'yhat_upper' in forecast_result.columns:
        negative_upper = (forecast_result['yhat_upper'] < 0).sum()
        if negative_upper > 0:
            print(f"⚠️  {negative_upper} limites superiores negativos. Corrigindo para 0.")
            forecast_result['yhat_upper'] = forecast_result['yhat_upper'].clip(lower=0)
    
    # Converter para números inteiros (arredondamento)
    print(f"🔢 Convertendo previsões para números inteiros...")
    forecast_result['yhat'] = forecast_result['yhat'].round().astype(int)
    forecast_result['yhat_lower'] = forecast_result['yhat_lower'].round().astype(int)
    forecast_result['yhat_upper'] = forecast_result['yhat_upper'].round().astype(int)
    
    # Garantir que os valores sejam não-negativos após conversão
    forecast_result['yhat'] = forecast_result['yhat'].clip(lower=0)
    forecast_result['yhat_lower'] = forecast_result['yhat_lower'].clip(lower=0)
    forecast_result['yhat_upper'] = forecast_result['yhat_upper'].clip(lower=0)
    
    # Estatísticas das previsões
    print(f"📊 Estatísticas das previsões (números inteiros):")
    print(f"   Mínimo: {forecast_result['yhat'].min()}")
    print(f"   Máximo: {forecast_result['yhat'].max()}")
    print(f"   Média: {forecast_result['yhat'].mean():.1f}")
    
    return forecast_result


def list_available_models() -> List[str]:
    models_dir = _get_models_dir()
    return [path.stem for path in models_dir.glob("*.joblib")]



