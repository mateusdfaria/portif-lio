import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MetricsResult:
    """Resultado de cálculo de métricas"""
    mape: float
    rmse: float
    smape: float
    mae: float
    mse: float
    r2: float
    bias: float
    mase: float
    details: Dict

class MetricsService:
    """Serviço para cálculo de métricas de avaliação de previsões"""
    
    def __init__(self):
        self.metrics = ['mape', 'rmse', 'smape', 'mae', 'mse', 'r2', 'bias', 'mase']
    
    def calculate_mape(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """
        Calcula MAPE (Mean Absolute Percentage Error)
        MAPE = (1/n) * Σ|actual - predicted| / |actual| * 100
        """
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        # Evitar divisão por zero
        mask = actual != 0
        if not np.any(mask):
            return 0.0
        
        actual_masked = actual[mask]
        predicted_masked = predicted[mask]
        
        mape = np.mean(np.abs((actual_masked - predicted_masked) / actual_masked)) * 100
        return float(mape)
    
    def calculate_smape(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """
        Calcula sMAPE (Symmetric Mean Absolute Percentage Error)
        sMAPE = (1/n) * Σ|actual - predicted| / ((|actual| + |predicted|) / 2) * 100
        """
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        # Evitar divisão por zero
        denominator = (np.abs(actual) + np.abs(predicted)) / 2
        denominator = np.where(denominator == 0, 1e-8, denominator)
        
        smape = np.mean(np.abs(actual - predicted) / denominator) * 100
        return float(smape)
    
    def calculate_rmse(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """
        Calcula RMSE (Root Mean Square Error)
        RMSE = sqrt(mean((actual - predicted)²))
        """
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        mse = np.mean((actual - predicted) ** 2)
        rmse = np.sqrt(mse)
        return float(rmse)
    
    def calculate_mae(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """
        Calcula MAE (Mean Absolute Error)
        MAE = mean(|actual - predicted|)
        """
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        mae = np.mean(np.abs(actual - predicted))
        return float(mae)
    
    def calculate_mse(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """
        Calcula MSE (Mean Square Error)
        MSE = mean((actual - predicted)²)
        """
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        mse = np.mean((actual - predicted) ** 2)
        return float(mse)
    
    def calculate_r2(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """
        Calcula R² (Coefficient of Determination)
        R² = 1 - (SS_res / SS_tot)
        """
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        
        if ss_tot == 0:
            return 0.0
        
        r2 = 1 - (ss_res / ss_tot)
        return float(r2)
    
    def calculate_bias(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """
        Calcula Bias (Mean Error)
        Bias = mean(predicted - actual)
        """
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        bias = np.mean(predicted - actual)
        return float(bias)
    
    def calculate_mase(self, actual: np.ndarray, predicted: np.ndarray, 
                      seasonal_period: int = 7) -> float:
        """
        Calcula MASE (Mean Absolute Scaled Error)
        MASE = MAE / MAE_naive_seasonal
        """
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        if len(actual) <= seasonal_period:
            return float('inf')
        
        # MAE do modelo
        mae_model = self.calculate_mae(actual, predicted)
        
        # MAE do modelo naive sazonal
        naive_errors = []
        for i in range(seasonal_period, len(actual)):
            naive_pred = actual[i - seasonal_period]
            naive_errors.append(abs(actual[i] - naive_pred))
        
        if len(naive_errors) == 0:
            return float('inf')
        
        mae_naive = np.mean(naive_errors)
        
        if mae_naive == 0:
            return float('inf')
        
        mase = mae_model / mae_naive
        return float(mase)
    
    def calculate_all_metrics(self, actual: List[float], predicted: List[float], 
                            seasonal_period: int = 7) -> MetricsResult:
        """
        Calcula todas as métricas de avaliação
        """
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        # Validar entradas
        if len(actual) != len(predicted):
            raise ValueError("Arrays de actual e predicted devem ter o mesmo tamanho")
        
        if len(actual) == 0:
            raise ValueError("Arrays não podem estar vazios")
        
        # Calcular métricas
        mape = self.calculate_mape(actual, predicted)
        smape = self.calculate_smape(actual, predicted)
        rmse = self.calculate_rmse(actual, predicted)
        mae = self.calculate_mae(actual, predicted)
        mse = self.calculate_mse(actual, predicted)
        r2 = self.calculate_r2(actual, predicted)
        bias = self.calculate_bias(actual, predicted)
        mase = self.calculate_mase(actual, predicted, seasonal_period)
        
        # Detalhes adicionais
        details = {
            'n_samples': len(actual),
            'actual_mean': float(np.mean(actual)),
            'actual_std': float(np.std(actual)),
            'predicted_mean': float(np.mean(predicted)),
            'predicted_std': float(np.std(predicted)),
            'actual_min': float(np.min(actual)),
            'actual_max': float(np.max(actual)),
            'predicted_min': float(np.min(predicted)),
            'predicted_max': float(np.max(predicted)),
            'correlation': float(np.corrcoef(actual, predicted)[0, 1]) if len(actual) > 1 else 0.0,
            'seasonal_period': seasonal_period
        }
        
        return MetricsResult(
            mape=mape,
            rmse=rmse,
            smape=smape,
            mae=mae,
            mse=mse,
            r2=r2,
            bias=bias,
            mase=mase,
            details=details
        )
    
    def evaluate_forecast_quality(self, metrics: MetricsResult) -> Dict[str, str]:
        """
        Avalia a qualidade da previsão baseada nas métricas
        """
        quality = {}
        
        # Avaliar MAPE
        if metrics.mape < 10:
            quality['mape'] = 'Excelente'
        elif metrics.mape < 20:
            quality['mape'] = 'Boa'
        elif metrics.mape < 50:
            quality['mape'] = 'Aceitável'
        else:
            quality['mape'] = 'Ruim'
        
        # Avaliar sMAPE
        if metrics.smape < 10:
            quality['smape'] = 'Excelente'
        elif metrics.smape < 20:
            quality['smape'] = 'Boa'
        elif metrics.smape < 50:
            quality['smape'] = 'Aceitável'
        else:
            quality['smape'] = 'Ruim'
        
        # Avaliar R²
        if metrics.r2 > 0.9:
            quality['r2'] = 'Excelente'
        elif metrics.r2 > 0.7:
            quality['r2'] = 'Boa'
        elif metrics.r2 > 0.5:
            quality['r2'] = 'Aceitável'
        else:
            quality['r2'] = 'Ruim'
        
        # Avaliar MASE
        if metrics.mase < 0.5:
            quality['mase'] = 'Excelente'
        elif metrics.mase < 1.0:
            quality['mase'] = 'Boa'
        elif metrics.mase < 1.5:
            quality['mase'] = 'Aceitável'
        else:
            quality['mase'] = 'Ruim'
        
        return quality
    
    def compare_models(self, results: List[Tuple[str, MetricsResult]]) -> Dict:
        """
        Compara múltiplos modelos baseado nas métricas
        """
        if not results:
            return {}
        
        comparison = {}
        
        # Encontrar melhor modelo para cada métrica
        for metric_name in ['mape', 'smape', 'rmse', 'mae', 'r2']:
            if metric_name == 'r2':
                # Para R², maior é melhor
                best_model = max(results, key=lambda x: getattr(x[1], metric_name))
            else:
                # Para outras métricas, menor é melhor
                best_model = min(results, key=lambda x: getattr(x[1], metric_name))
            
            comparison[f'best_{metric_name}'] = {
                'model': best_model[0],
                'value': getattr(best_model[1], metric_name)
            }
        
        # Calcular ranking geral (baseado em sMAPE)
        sorted_results = sorted(results, key=lambda x: x[1].smape)
        comparison['ranking'] = [
            {
                'model': model_name,
                'smape': metrics.smape,
                'mape': metrics.mape,
                'rmse': metrics.rmse,
                'r2': metrics.r2
            }
            for model_name, metrics in sorted_results
        ]
        
        return comparison
    
    def generate_metrics_report(self, metrics: MetricsResult, model_name: str = "Modelo") -> str:
        """
        Gera relatório textual das métricas
        """
        quality = self.evaluate_forecast_quality(metrics)
        
        report = f"""
📊 RELATÓRIO DE MÉTRICAS - {model_name.upper()}
{'='*50}

📈 MÉTRICAS PRINCIPAIS:
• MAPE (Mean Absolute Percentage Error): {metrics.mape:.2f}% - {quality['mape']}
• sMAPE (Symmetric MAPE): {metrics.smape:.2f}% - {quality['smape']}
• RMSE (Root Mean Square Error): {metrics.rmse:.2f} - {quality['rmse'] if 'rmse' in quality else 'N/A'}
• MAE (Mean Absolute Error): {metrics.mae:.2f}
• R² (Coefficient of Determination): {metrics.r2:.3f} - {quality['r2']}

📊 MÉTRICAS ADICIONAIS:
• MSE (Mean Square Error): {metrics.mse:.2f}
• Bias (Mean Error): {metrics.bias:.2f}
• MASE (Mean Absolute Scaled Error): {metrics.mase:.2f} - {quality['mase']}

📋 DETALHES ESTATÍSTICOS:
• Amostras: {metrics.details['n_samples']}
• Média dos valores reais: {metrics.details['actual_mean']:.2f}
• Desvio padrão dos valores reais: {metrics.details['actual_std']:.2f}
• Média das previsões: {metrics.details['predicted_mean']:.2f}
• Desvio padrão das previsões: {metrics.details['predicted_std']:.2f}
• Correlação: {metrics.details['correlation']:.3f}

🎯 INTERPRETAÇÃO:
• MAPE < 10%: Excelente | 10-20%: Bom | 20-50%: Aceitável | >50%: Ruim
• sMAPE < 10%: Excelente | 10-20%: Bom | 20-50%: Aceitável | >50%: Ruim
• R² > 0.9: Excelente | 0.7-0.9: Bom | 0.5-0.7: Aceitável | <0.5: Ruim
• MASE < 0.5: Excelente | 0.5-1.0: Bom | 1.0-1.5: Aceitável | >1.5: Ruim
"""
        
        return report

# Instância global do serviço
metrics_service = MetricsService()
