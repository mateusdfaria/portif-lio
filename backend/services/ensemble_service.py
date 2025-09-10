import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from services.prophet_service import generate_forecast
from services.metrics_service import metrics_service

class EnsembleService:
    """Serviço para criar ensemble Prophet + NaiveSemanal"""
    
    def __init__(self):
        self.prophet_weight = 0.7  # Peso do Prophet
        self.naive_weight = 0.3    # Peso do Naive Semanal
    
    def naive_weekly_forecast(self, historical_data: pd.DataFrame, horizon: int) -> pd.DataFrame:
        """
        Implementa Naive Semanal: usa o valor do mesmo dia da semana anterior
        """
        if len(historical_data) < 7:
            # Se não há dados suficientes, usar média simples
            mean_val = historical_data['y'].mean()
            naive_forecast = pd.DataFrame({
                'ds': pd.date_range(start=historical_data['ds'].max() + timedelta(days=1), periods=horizon, freq='D'),
                'yhat': [mean_val] * horizon,
                'yhat_lower': [mean_val * 0.8] * horizon,
                'yhat_upper': [mean_val * 1.2] * horizon
            })
            return naive_forecast
        
        # Criar forecast usando Naive Semanal
        last_date = historical_data['ds'].max()
        forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=horizon, freq='D')
        
        naive_values = []
        naive_lower = []
        naive_upper = []
        
        for date in forecast_dates:
            # Encontrar o mesmo dia da semana na semana anterior
            target_weekday = date.dayofweek
            target_date = date - timedelta(weeks=1)
            
            # Procurar pelo valor mais próximo do mesmo dia da semana
            same_weekday_data = historical_data[historical_data['ds'].dt.dayofweek == target_weekday]
            
            if len(same_weekday_data) > 0:
                # Usar o valor mais recente do mesmo dia da semana
                naive_val = same_weekday_data['y'].iloc[-1]
                
                # Calcular intervalos de confiança simples (±20%)
                naive_lower_val = naive_val * 0.8
                naive_upper_val = naive_val * 1.2
            else:
                # Fallback: usar média geral
                naive_val = historical_data['y'].mean()
                naive_lower_val = naive_val * 0.8
                naive_upper_val = naive_val * 1.2
            
            naive_values.append(naive_val)
            naive_lower.append(naive_lower_val)
            naive_upper.append(naive_upper_val)
        
        return pd.DataFrame({
            'ds': forecast_dates,
            'yhat': naive_values,
            'yhat_lower': naive_lower,
            'yhat_upper': naive_upper
        })
    
    def create_ensemble_forecast(self, series_id: str, historical_data: pd.DataFrame, 
                                horizon: int, future_regressors: pd.DataFrame = None) -> Dict:
        """
        Cria forecast ensemble combinando Prophet e Naive Semanal
        """
        print(f"🎯 Criando ensemble Prophet + Naive Semanal...")
        
        # 1. Forecast Prophet
        print(f"📊 Gerando forecast Prophet...")
        prophet_forecast = generate_forecast(series_id, horizon, future_regressors)
        
        # 2. Forecast Naive Semanal
        print(f"📊 Gerando forecast Naive Semanal...")
        naive_forecast = self.naive_weekly_forecast(historical_data, horizon)
        
        # 3. Combinar forecasts
        print(f"🔄 Combinando forecasts (Prophet: {self.prophet_weight}, Naive: {self.naive_weight})...")
        
        ensemble_forecast = prophet_forecast.copy()
        
        # Combinar valores principais
        ensemble_forecast['yhat'] = (
            self.prophet_weight * prophet_forecast['yhat'] + 
            self.naive_weight * naive_forecast['yhat']
        )
        
        # Combinar intervalos de confiança (mais conservador)
        ensemble_forecast['yhat_lower'] = np.minimum(
            prophet_forecast['yhat_lower'], 
            naive_forecast['yhat_lower']
        )
        ensemble_forecast['yhat_upper'] = np.maximum(
            prophet_forecast['yhat_upper'], 
            naive_forecast['yhat_upper']
        )
        
        # Garantir que os valores sejam inteiros
        ensemble_forecast['yhat'] = ensemble_forecast['yhat'].round().astype(int)
        ensemble_forecast['yhat_lower'] = ensemble_forecast['yhat_lower'].round().astype(int)
        ensemble_forecast['yhat_upper'] = ensemble_forecast['yhat_upper'].round().astype(int)
        
        # Garantir valores não-negativos
        ensemble_forecast['yhat'] = ensemble_forecast['yhat'].clip(lower=0)
        ensemble_forecast['yhat_lower'] = ensemble_forecast['yhat_lower'].clip(lower=0)
        ensemble_forecast['yhat_upper'] = ensemble_forecast['yhat_upper'].clip(lower=0)
        
        # Calcular métricas de comparação
        prophet_mean = prophet_forecast['yhat'].mean()
        naive_mean = naive_forecast['yhat'].mean()
        ensemble_mean = ensemble_forecast['yhat'].mean()
        
        print(f"📊 Estatísticas do Ensemble:")
        print(f"   Prophet médio: {prophet_mean:.1f}")
        print(f"   Naive médio: {naive_mean:.1f}")
        print(f"   Ensemble médio: {ensemble_mean:.1f}")
        
        return {
            'ensemble_forecast': ensemble_forecast,
            'prophet_forecast': prophet_forecast,
            'naive_forecast': naive_forecast,
            'weights': {
                'prophet': self.prophet_weight,
                'naive': self.naive_weight
            },
            'statistics': {
                'prophet_mean': prophet_mean,
                'naive_mean': naive_mean,
                'ensemble_mean': ensemble_mean
            }
        }
    
    def evaluate_ensemble_performance(self, historical_data: pd.DataFrame, 
                                    test_periods: int = 30) -> Dict:
        """
        Avalia performance do ensemble usando backtesting
        """
        print(f"🔍 Avaliando performance do ensemble...")
        
        if len(historical_data) < test_periods + 7:
            print(f"⚠️  Dados insuficientes para avaliação (mínimo: {test_periods + 7} dias)")
            return {'error': 'Dados insuficientes'}
        
        # Dividir dados em treino e teste
        train_data = historical_data.iloc[:-test_periods].copy()
        test_data = historical_data.iloc[-test_periods:].copy()
        
        # Criar ensemble para período de teste
        ensemble_result = self.create_ensemble_forecast(
            'ensemble_test', train_data, test_periods
        )
        
        # Calcular métricas
        ensemble_forecast = ensemble_result['ensemble_forecast']
        prophet_forecast = ensemble_result['prophet_forecast']
        naive_forecast = ensemble_result['naive_forecast']
        
        # Métricas para cada método
        ensemble_metrics = metrics_service.calculate_all_metrics(
            test_data['y'].values, ensemble_forecast['yhat'].values
        )
        
        prophet_metrics = metrics_service.calculate_all_metrics(
            test_data['y'].values, prophet_forecast['yhat'].values
        )
        
        naive_metrics = metrics_service.calculate_all_metrics(
            test_data['y'].values, naive_forecast['yhat'].values
        )
        
        return {
            'ensemble_metrics': ensemble_metrics,
            'prophet_metrics': prophet_metrics,
            'naive_metrics': naive_metrics,
            'improvement_over_prophet': {
                'mape': prophet_metrics['mape'] - ensemble_metrics['mape'],
                'rmse': prophet_metrics['rmse'] - ensemble_metrics['rmse'],
                'smape': prophet_metrics['smape'] - ensemble_metrics['smape']
            },
            'improvement_over_naive': {
                'mape': naive_metrics['mape'] - ensemble_metrics['mape'],
                'rmse': naive_metrics['rmse'] - ensemble_metrics['rmse'],
                'smape': naive_metrics['smape'] - ensemble_metrics['smape']
            }
        }

# Instância global do serviço
ensemble_service = EnsembleService()
