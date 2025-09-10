import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class BaselineResult:
    """Resultado de um baseline"""
    method: str
    predictions: List[float]
    actuals: List[float]
    dates: List[str]
    smape: float
    mae: float
    rmse: float
    mape: float

class BaselineService:
    """Serviço para baselines de previsão"""
    
    def __init__(self):
        pass
    
    def calculate_smape(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calcula sMAPE (Symmetric Mean Absolute Percentage Error)"""
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        denominator = (np.abs(actual) + np.abs(predicted)) / 2
        denominator = np.where(denominator == 0, 1, denominator)
        
        smape = np.mean(np.abs(actual - predicted) / denominator) * 100
        return float(smape)
    
    def calculate_mae(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calcula MAE (Mean Absolute Error)"""
        return float(np.mean(np.abs(actual - predicted)))
    
    def calculate_rmse(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calcula RMSE (Root Mean Square Error)"""
        return float(np.sqrt(np.mean((actual - predicted) ** 2)))
    
    def calculate_mape(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calcula MAPE (Mean Absolute Percentage Error)"""
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        actual = np.where(actual == 0, 1e-8, actual)
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        return float(mape)
    
    def naive_forecast(self, df: pd.DataFrame, horizon: int) -> List[float]:
        """Baseline Naive: usa o último valor observado"""
        if len(df) == 0:
            return [0.0] * horizon
        
        last_value = df['y'].iloc[-1]
        return [last_value] * horizon
    
    def seasonal_naive_forecast(self, df: pd.DataFrame, horizon: int, season_length: int = 7) -> List[float]:
        """Baseline Sazonal-Naive: usa valores da mesma época do ano anterior"""
        if len(df) < season_length:
            # Se não tiver dados suficientes, usar naive
            return self.naive_forecast(df, horizon)
        
        predictions = []
        
        for i in range(horizon):
            # Pegar valor de 'season_length' dias atrás
            if len(df) > season_length + i:
                pred_value = df['y'].iloc[-(season_length + i)]
            else:
                # Se não tiver dados suficientes, usar o último valor
                pred_value = df['y'].iloc[-1]
            
            predictions.append(pred_value)
        
        return predictions
    
    def moving_average_forecast(self, df: pd.DataFrame, horizon: int, window: int = 7) -> List[float]:
        """Baseline Média Móvel: usa média dos últimos 'window' dias"""
        if len(df) < window:
            # Se não tiver dados suficientes, usar naive
            return self.naive_forecast(df, horizon)
        
        last_window_avg = df['y'].tail(window).mean()
        return [last_window_avg] * horizon
    
    def linear_trend_forecast(self, df: pd.DataFrame, horizon: int) -> List[float]:
        """Baseline Tendência Linear: extrapola tendência linear"""
        if len(df) < 2:
            return self.naive_forecast(df, horizon)
        
        # Calcular tendência usando os últimos 30 dias ou todos os dados se menor
        lookback = min(30, len(df))
        recent_data = df['y'].tail(lookback).values
        
        # Regressão linear simples
        x = np.arange(len(recent_data))
        y = recent_data
        
        # Calcular coeficientes
        n = len(x)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x * x)
        
        # Evitar divisão por zero
        if n * sum_x2 - sum_x * sum_x == 0:
            return self.naive_forecast(df, horizon)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Fazer previsões
        predictions = []
        for i in range(1, horizon + 1):
            pred_value = slope * (len(recent_data) + i - 1) + intercept
            predictions.append(max(0, pred_value))  # Evitar valores negativos
        
        return predictions
    
    def evaluate_baseline(
        self, 
        df: pd.DataFrame, 
        method: str, 
        horizon: int,
        test_start_idx: int = None
    ) -> BaselineResult:
        """Avalia um baseline específico"""
        
        if test_start_idx is None:
            test_start_idx = len(df) - horizon
        
        # Dados de treinamento e teste
        train_data = df.iloc[:test_start_idx].copy()
        test_data = df.iloc[test_start_idx:test_start_idx + horizon].copy()
        
        if len(test_data) == 0:
            raise ValueError("Dados de teste insuficientes")
        
        # Fazer previsão baseada no método
        if method == 'naive':
            predictions = self.naive_forecast(train_data, horizon)
        elif method == 'seasonal_naive':
            predictions = self.seasonal_naive_forecast(train_data, horizon)
        elif method == 'moving_average':
            predictions = self.moving_average_forecast(train_data, horizon)
        elif method == 'linear_trend':
            predictions = self.linear_trend_forecast(train_data, horizon)
        elif method == 'exponential_smoothing':
            predictions = self.exponential_smoothing_forecast(train_data, horizon)
        elif method == 'seasonal_decomposition':
            predictions = self.seasonal_decomposition_forecast(train_data, horizon)
        else:
            raise ValueError(f"Método '{method}' não suportado")
        
        # Garantir que temos o número correto de previsões
        predictions = predictions[:len(test_data)]
        
        # Calcular métricas
        actual = test_data['y'].values
        predicted = np.array(predictions)
        
        metrics = {
            'smape': self.calculate_smape(actual, predicted),
            'mae': self.calculate_mae(actual, predicted),
            'rmse': self.calculate_rmse(actual, predicted),
            'mape': self.calculate_mape(actual, predicted)
        }
        
        return BaselineResult(
            method=method,
            predictions=predictions if isinstance(predictions, list) else predictions.tolist(),
            actuals=actual.tolist(),
            dates=[d.strftime('%Y-%m-%d') for d in test_data['ds']],
            smape=metrics['smape'],
            mae=metrics['mae'],
            rmse=metrics['rmse'],
            mape=metrics['mape']
        )
    
    def exponential_smoothing_forecast(self, df: pd.DataFrame, horizon: int, alpha: float = 0.3) -> List[float]:
        """Baseline Suavização Exponencial: usa média ponderada com decaimento exponencial"""
        if len(df) == 0:
            return [0.0] * horizon
        
        # Calcular suavização exponencial
        values = df['y'].values
        smoothed = [values[0]]  # Primeiro valor
        
        for i in range(1, len(values)):
            smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[i-1])
        
        # Usar o último valor suavizado para todas as previsões
        last_smoothed = smoothed[-1]
        return [last_smoothed] * horizon
    
    def seasonal_decomposition_forecast(self, df: pd.DataFrame, horizon: int, season_length: int = 7) -> List[float]:
        """Baseline Decomposição Sazonal: separa tendência e sazonalidade"""
        if len(df) < season_length * 2:
            return self.naive_forecast(df, horizon)
        
        values = df['y'].values
        
        # Decomposição simples: tendência + sazonalidade
        # Calcular tendência usando média móvel
        trend_window = min(season_length, len(values) // 2)
        trend = []
        for i in range(len(values)):
            start = max(0, i - trend_window // 2)
            end = min(len(values), i + trend_window // 2 + 1)
            trend.append(np.mean(values[start:end]))
        
        # Calcular sazonalidade
        seasonal = values - np.array(trend)
        
        # Média sazonal para cada posição no ciclo
        seasonal_pattern = []
        for i in range(season_length):
            seasonal_values = []
            for j in range(i, len(seasonal), season_length):
                seasonal_values.append(seasonal[j])
            seasonal_pattern.append(np.mean(seasonal_values) if seasonal_values else 0)
        
        # Fazer previsões
        predictions = []
        last_trend = trend[-1]
        
        for i in range(horizon):
            # Extrapolar tendência (simples)
            trend_pred = last_trend
            seasonal_pred = seasonal_pattern[i % season_length]
            predictions.append(max(0, trend_pred + seasonal_pred))
        
        return predictions
    
    def rolling_cross_validation_baselines(
        self, 
        df: pd.DataFrame, 
        initial_days: int = 365,
        horizon_days: int = 30,
        period_days: int = 30
    ) -> Dict[str, List[float]]:
        """Validação cruzada para baselines"""
        
        df['ds'] = pd.to_datetime(df['ds'])
        df = df.sort_values('ds').reset_index(drop=True)
        
        # Converter dias para timestamps
        initial_delta = timedelta(days=initial_days)
        horizon_delta = timedelta(days=horizon_days)
        period_delta = timedelta(days=period_days)
        
        start_date = df['ds'].min()
        end_date = df['ds'].max()
        
        methods = ['naive', 'seasonal_naive', 'moving_average', 'linear_trend', 'exponential_smoothing']
        all_smape = {method: [] for method in methods}
        
        current_date = start_date + initial_delta
        
        while current_date + horizon_delta <= end_date:
            try:
                # Dados de treinamento e teste
                train_end = current_date
                test_start = current_date
                test_end = current_date + horizon_delta
                
                train_data = df[df['ds'] < train_end].copy()
                test_data = df[(df['ds'] >= test_start) & (df['ds'] < test_end)].copy()
                
                if len(train_data) < 30 or len(test_data) == 0:
                    current_date += period_delta
                    continue
                
                # Avaliar cada método
                for method in methods:
                    try:
                        result = self.evaluate_baseline(
                            pd.concat([train_data, test_data]), 
                            method, 
                            len(test_data),
                            len(train_data)
                        )
                        all_smape[method].append(result.smape)
                    except Exception as e:
                        print(f"⚠️  Erro no método {method}: {e}")
                
                current_date += period_delta
                
            except Exception as e:
                print(f"❌ Erro na validação cruzada: {e}")
                current_date += period_delta
        
        return all_smape
    
    def compare_all_baselines(
        self, 
        df: pd.DataFrame, 
        horizon: int,
        test_start_idx: int = None,
        use_cross_validation: bool = False
    ) -> List[BaselineResult]:
        """Compara todos os baselines disponíveis"""
        
        if use_cross_validation:
            # Usar validação cruzada
            cv_results = self.rolling_cross_validation_baselines(df)
            
            results = []
            for method, smape_values in cv_results.items():
                if smape_values:
                    avg_smape = np.mean(smape_values)
                    std_smape = np.std(smape_values)
                    
                    # Criar resultado agregado
                    result = BaselineResult(
                        method=method,
                        predictions=[],
                        actuals=[],
                        dates=[],
                        smape=avg_smape,
                        mae=0,  # Não calculado na CV
                        rmse=0,  # Não calculado na CV
                        mape=0   # Não calculado na CV
                    )
                    results.append(result)
                    print(f"✅ {method}: sMAPE = {avg_smape:.2f} ± {std_smape:.2f} (CV)")
            
            # Ordenar por sMAPE (menor é melhor)
            results.sort(key=lambda x: x.smape)
            return results
        
        else:
            # Avaliação simples
            methods = ['naive', 'seasonal_naive', 'moving_average', 'linear_trend', 'exponential_smoothing', 'seasonal_decomposition']
            results = []
            
            print(f"🔍 Avaliando {len(methods)} baselines...")
            
            for method in methods:
                try:
                    result = self.evaluate_baseline(df, method, horizon, test_start_idx)
                    results.append(result)
                    print(f"✅ {method}: sMAPE = {result.smape:.2f}, MAE = {result.mae:.2f}")
                except Exception as e:
                    print(f"❌ Erro no baseline {method}: {e}")
            
            # Ordenar por sMAPE (menor é melhor)
            results.sort(key=lambda x: x.smape)
            
            return results
    
    def get_best_baseline(self, results: List[BaselineResult]) -> BaselineResult:
        """Retorna o melhor baseline baseado no sMAPE"""
        if not results:
            return None
        
        return min(results, key=lambda x: x.smape)

# Instância global do serviço
baseline_service = BaselineService()
