"""Testes TDD para serviços de previsão.

Seguindo TDD:
1. Escrever teste primeiro (Red)
2. Implementar código mínimo (Green)
3. Refatorar (Refactor)
"""

import pandas as pd
import pytest
from datetime import datetime, timedelta

from services.prophet_service import train_and_persist_model, generate_forecast, _get_model_path
from pathlib import Path
import joblib


@pytest.fixture
def sample_dataframe():
    """Cria DataFrame de exemplo para testes."""
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    values = [100 + i * 2 + (i % 7) * 10 for i in range(30)]
    return pd.DataFrame({'ds': dates, 'y': values})


def test_train_model_creates_model_file(sample_dataframe):
    """Teste: Treinar modelo deve criar arquivo de modelo."""
    # Arrange
    series_id = "test_series_tdd"
    model_path = _get_model_path(series_id)
    
    # Limpar modelo existente se houver
    if model_path.exists():
        model_path.unlink()
    
    # Act
    train_and_persist_model(
        series_id=series_id,
        dataframe=sample_dataframe,
        regressors=[]
    )
    
    # Assert
    assert model_path.exists(), "Arquivo de modelo deve ser criado"
    
    # Cleanup
    if model_path.exists():
        model_path.unlink()


def test_generate_forecast_returns_dataframe(sample_dataframe):
    """Teste: Gerar previsão deve retornar DataFrame."""
    # Arrange
    series_id = "test_forecast_tdd"
    model_path = _get_model_path(series_id)
    
    # Limpar modelo existente se houver
    if model_path.exists():
        model_path.unlink()
    
    # Treinar modelo primeiro
    train_and_persist_model(
        series_id=series_id,
        dataframe=sample_dataframe,
        regressors=[]
    )
    
    # Act
    forecast = generate_forecast(series_id=series_id, horizon=7)
    
    # Assert
    assert isinstance(forecast, pd.DataFrame), "Previsão deve ser DataFrame"
    assert len(forecast) == 7, "Previsão deve ter 7 dias"
    assert 'ds' in forecast.columns, "DataFrame deve ter coluna 'ds'"
    assert 'yhat' in forecast.columns, "DataFrame deve ter coluna 'yhat'"
    
    # Cleanup
    if model_path.exists():
        model_path.unlink()


def test_forecast_has_confidence_intervals(sample_dataframe):
    """Teste: Previsão deve ter intervalos de confiança."""
    # Arrange
    series_id = "test_intervals_tdd"
    model_path = _get_model_path(series_id)
    
    # Limpar modelo existente se houver
    if model_path.exists():
        model_path.unlink()
    
    # Treinar modelo
    train_and_persist_model(
        series_id=series_id,
        dataframe=sample_dataframe,
        regressors=[]
    )
    
    # Act
    forecast = generate_forecast(series_id=series_id, horizon=7)
    
    # Assert
    assert 'yhat_lower' in forecast.columns, "Deve ter intervalo inferior"
    assert 'yhat_upper' in forecast.columns, "Deve ter intervalo superior"
    assert all(forecast['yhat_lower'] <= forecast['yhat']), "Limite inferior deve ser <= previsão"
    assert all(forecast['yhat'] <= forecast['yhat_upper']), "Previsão deve ser <= limite superior"
    
    # Cleanup
    if model_path.exists():
        model_path.unlink()


def test_train_model_with_regressors(sample_dataframe):
    """Teste: Treinar modelo com regressores deve funcionar."""
    # Arrange
    series_id = "test_regressors_tdd"
    model_path = _get_model_path(series_id)
    
    # Limpar modelo existente se houver
    if model_path.exists():
        model_path.unlink()
    
    # Adicionar regressor ao DataFrame
    df_with_regressor = sample_dataframe.copy()
    df_with_regressor['regressor1'] = [i % 2 for i in range(len(df_with_regressor))]
    
    # Act
    train_and_persist_model(
        series_id=series_id,
        dataframe=df_with_regressor,
        regressors=['regressor1']
    )
    
    # Assert
    assert model_path.exists(), "Modelo com regressores deve ser criado"
    
    # Verificar que modelo carrega corretamente
    model = joblib.load(model_path)
    assert model is not None, "Modelo deve ser carregável"
    
    # Cleanup
    if model_path.exists():
        model_path.unlink()

