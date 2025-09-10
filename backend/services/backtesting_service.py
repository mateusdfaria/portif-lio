import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

@dataclass
class BacktestResult:
    """Resultado de um teste de backtesting"""
    params: Dict
    smape: float
    mae: float
    rmse: float
    mape: float
    predictions: List[float]
    actuals: List[float]
    dates: List[str]

class BacktestingService:
    """Serviço para backtesting e validação cruzada"""
    
    def __init__(self):
        self.metrics = ['smape', 'mae', 'rmse', 'mape']
    
    def calculate_smape(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calcula sMAPE (Symmetric Mean Absolute Percentage Error)"""
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        # Evitar divisão por zero
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
        
        # Evitar divisão por zero
        actual = np.where(actual == 0, 1e-8, actual)
        
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        return float(mape)
    
    def calculate_metrics(self, actual: List[float], predicted: List[float]) -> Dict[str, float]:
        """Calcula todas as métricas de erro"""
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        return {
            'smape': self.calculate_smape(actual, predicted),
            'mae': self.calculate_mae(actual, predicted),
            'rmse': self.calculate_rmse(actual, predicted),
            'mape': self.calculate_mape(actual, predicted)
        }
    
    def prepare_data_for_prophet(self, df: pd.DataFrame, regressors: List[str] = None) -> pd.DataFrame:
        """Prepara dados para o Prophet"""
        df_prep = df.copy()
        df_prep['ds'] = pd.to_datetime(df_prep['ds'])
        df_prep = df_prep.sort_values('ds').reset_index(drop=True)
        
        # Adicionar features de calendário
        df_prep['year'] = df_prep['ds'].dt.year
        df_prep['month'] = df_prep['ds'].dt.month
        df_prep['day_of_week'] = df_prep['ds'].dt.dayofweek
        df_prep['is_weekend'] = (df_prep['day_of_week'] >= 5).astype(int)
        df_prep['is_winter'] = df_prep['month'].isin([5, 6, 7, 8, 9]).astype(int)
        
        # Calcular cap baseado no P95
        y_values = df_prep['y'].values
        p95 = np.percentile(y_values, 95)
        cap_value = max(p95, y_values.max() * 1.1)
        df_prep['cap'] = cap_value
        df_prep['floor'] = 0
        
        return df_prep
    
    def train_prophet_model(self, df: pd.DataFrame, params: Dict) -> Prophet:
        """Treina modelo Prophet com parâmetros específicos"""
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode=params.get('seasonality_mode', 'additive'),
            changepoint_prior_scale=params.get('changepoint_prior_scale', 0.02),
            seasonality_prior_scale=params.get('seasonality_prior_scale', 5),
            growth=params.get('growth', 'linear'),
            changepoint_range=params.get('changepoint_range', 0.8),
            n_changepoints=params.get('n_changepoints', 25),
        )
        
        # Adicionar regressores de calendário
        calendar_regressors = ["is_weekend", "is_winter", "day_of_week"]
        for regressor in calendar_regressors:
            if regressor in df.columns:
                model.add_regressor(regressor, standardize=True)
        
        # Adicionar regressores externos se fornecidos
        external_regressors = params.get('regressors', [])
        for regressor in external_regressors:
            if regressor in df.columns:
                model.add_regressor(regressor, standardize=True)
        
        model.fit(df)
        return model
    
    def rolling_cross_validation(
        self, 
        df: pd.DataFrame, 
        initial_days: int = 365,
        horizon_days: int = 30,
        period_days: int = 30,
        params: Dict = None
    ) -> List[BacktestResult]:
        """Validação cruzada com janelas rolantes"""
        
        if params is None:
            params = {
                'seasonality_mode': 'additive',
                'changepoint_prior_scale': 0.02,
                'seasonality_prior_scale': 5,
                'regressors': []
            }
        
        df_prep = self.prepare_data_for_prophet(df, params.get('regressors', []))
        
        # Converter dias para timestamps
        initial_delta = timedelta(days=initial_days)
        horizon_delta = timedelta(days=horizon_days)
        period_delta = timedelta(days=period_days)
        
        start_date = df_prep['ds'].min()
        end_date = df_prep['ds'].max()
        
        results = []
        current_date = start_date + initial_delta
        
        while current_date + horizon_delta <= end_date:
            try:
                # Dados de treinamento
                train_end = current_date
                train_data = df_prep[df_prep['ds'] < train_end].copy()
                
                if len(train_data) < 30:  # Mínimo de 30 dias para treinar
                    current_date += period_delta
                    continue
                
                # Dados de teste
                test_start = current_date
                test_end = current_date + horizon_delta
                test_data = df_prep[
                    (df_prep['ds'] >= test_start) & (df_prep['ds'] < test_end)
                ].copy()
                
                if len(test_data) == 0:
                    current_date += period_delta
                    continue
                
                # Treinar modelo
                model = self.train_prophet_model(train_data, params)
                
                # Fazer previsão
                future = model.make_future_dataframe(periods=len(test_data))
                
                # Adicionar features de calendário para o futuro
                future['year'] = future['ds'].dt.year
                future['month'] = future['ds'].dt.month
                future['day_of_week'] = future['ds'].dt.dayofweek
                future['is_weekend'] = (future['day_of_week'] >= 5).astype(int)
                future['is_winter'] = future['month'].isin([5, 6, 7, 8, 9]).astype(int)
                
                # Adicionar cap e floor
                future['cap'] = train_data['cap'].iloc[-1]
                future['floor'] = 0
                
                # Adicionar regressores externos se existirem
                for regressor in params.get('regressors', []):
                    if regressor in train_data.columns:
                        # Usar último valor conhecido para o futuro
                        last_value = train_data[regressor].iloc[-1]
                        future[regressor] = last_value
                
                forecast = model.predict(future)
                
                # Pegar apenas as previsões do período de teste
                forecast_test = forecast[forecast['ds'] >= test_start].tail(len(test_data))
                
                if len(forecast_test) != len(test_data):
                    current_date += period_delta
                    continue
                
                # Calcular métricas
                actual = test_data['y'].values
                predicted = forecast_test['yhat'].values
                
                metrics = self.calculate_metrics(actual, predicted)
                
                result = BacktestResult(
                    params=params.copy(),
                    smape=metrics['smape'],
                    mae=metrics['mae'],
                    rmse=metrics['rmse'],
                    mape=metrics['mape'],
                    predictions=predicted.tolist(),
                    actuals=actual.tolist(),
                    dates=[d.strftime('%Y-%m-%d') for d in test_data['ds']]
                )
                
                results.append(result)
                print(f"✅ Backtest {len(results)}: {test_start.strftime('%Y-%m-%d')} a {test_end.strftime('%Y-%m-%d')} - sMAPE: {metrics['smape']:.2f}")
                
            except Exception as e:
                print(f"❌ Erro no backtest {current_date}: {e}")
            
            current_date += period_delta
        
        return results
    
    def grid_search(
        self, 
        df: pd.DataFrame,
        param_grid: Dict = None,
        initial_days: int = 365,
        horizon_days: int = 30,
        period_days: int = 30,
        max_combinations: int = 20
    ) -> List[BacktestResult]:
        """Grid search aprimorado para otimização de parâmetros"""
        
        if param_grid is None:
            # Grid mais inteligente baseado no tipo de dados
            y_values = df['y'].values
            y_range = y_values.max() - y_values.min()
            y_mean = y_values.mean()
            
            # Detectar se é dados cumulativos ou diários
            is_cumulative = y_range > y_mean * 2
            
            if is_cumulative:
                # Para dados cumulativos, usar growth logistic
                param_grid = {
                    'seasonality_mode': ['additive', 'multiplicative'],
                    'changepoint_prior_scale': [0.01, 0.02, 0.05],
                    'seasonality_prior_scale': [3, 5, 8],
                    'growth': ['logistic'],
                    'changepoint_range': [0.7, 0.8, 0.9],
                    'n_changepoints': [15, 25, 35]
                }
            else:
                # Para dados diários (como pronto socorro), usar growth linear
                param_grid = {
                    'seasonality_mode': ['additive'],
                    'changepoint_prior_scale': [0.01, 0.02, 0.03],
                    'seasonality_prior_scale': [2, 5, 10],
                    'growth': ['linear'],
                    'changepoint_range': [0.8, 0.9],
                    'n_changepoints': [20, 30]
                }
        
        # Gerar todas as combinações de parâmetros
        import itertools
        
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(itertools.product(*param_values))
        
        all_results = []
        
        print(f"🔍 Iniciando grid search com {len(param_combinations)} combinações...")
        
        for i, combination in enumerate(param_combinations):
            params = dict(zip(param_names, combination))
            
            print(f"📊 Testando combinação {i+1}/{len(param_combinations)}: {params}")
            
            try:
                results = self.rolling_cross_validation(
                    df, initial_days, horizon_days, period_days, params
                )
                
                if results:
                    # Calcular métricas médias para esta combinação
                    avg_smape = np.mean([r.smape for r in results])
                    avg_mae = np.mean([r.mae for r in results])
                    
                    # Criar resultado agregado
                    aggregated_result = BacktestResult(
                        params=params,
                        smape=avg_smape,
                        mae=avg_mae,
                        rmse=np.mean([r.rmse for r in results]),
                        mape=np.mean([r.mape for r in results]),
                        predictions=[],
                        actuals=[],
                        dates=[]
                    )
                    
                    all_results.append(aggregated_result)
                    print(f"✅ Combinação {i+1} - sMAPE médio: {avg_smape:.2f}")
                else:
                    print(f"⚠️  Combinação {i+1} - Sem resultados válidos")
                    
            except Exception as e:
                print(f"❌ Erro na combinação {i+1}: {e}")
        
        # Ordenar por sMAPE (menor é melhor)
        all_results.sort(key=lambda x: x.smape)
        
        return all_results
    
    def random_search(
        self, 
        df: pd.DataFrame,
        n_iterations: int = 15,
        initial_days: int = 365,
        horizon_days: int = 30,
        period_days: int = 30
    ) -> List[BacktestResult]:
        """Busca aleatória para otimização mais eficiente"""
        
        # Definir espaços de parâmetros
        param_spaces = {
            'seasonality_mode': ['additive', 'multiplicative'],
            'changepoint_prior_scale': [0.005, 0.01, 0.02, 0.05, 0.1],
            'seasonality_prior_scale': [1, 2, 5, 10, 15],
            'growth': ['linear', 'logistic'],
            'changepoint_range': [0.6, 0.7, 0.8, 0.9],
            'n_changepoints': [10, 15, 20, 25, 30, 35]
        }
        
        import random
        
        all_results = []
        
        print(f"🎲 Iniciando busca aleatória com {n_iterations} iterações...")
        
        for i in range(n_iterations):
            # Gerar parâmetros aleatórios
            params = {}
            for param_name, param_values in param_spaces.items():
                params[param_name] = random.choice(param_values)
            
            print(f"📊 Iteração {i+1}/{n_iterations}: {params}")
            
            try:
                results = self.rolling_cross_validation(
                    df, initial_days, horizon_days, period_days, params
                )
                
                if results:
                    # Calcular métricas médias para esta combinação
                    avg_smape = np.mean([r.smape for r in results])
                    avg_mae = np.mean([r.mae for r in results])
                    
                    # Criar resultado agregado
                    aggregated_result = BacktestResult(
                        params=params,
                        smape=avg_smape,
                        mae=avg_mae,
                        rmse=np.mean([r.rmse for r in results]),
                        mape=np.mean([r.mape for r in results]),
                        predictions=[],
                        actuals=[],
                        dates=[]
                    )
                    
                    all_results.append(aggregated_result)
                    print(f"✅ Iteração {i+1} - sMAPE médio: {avg_smape:.2f}")
                else:
                    print(f"⚠️  Iteração {i+1} - Sem resultados válidos")
                    
            except Exception as e:
                print(f"❌ Erro na iteração {i+1}: {e}")
        
        # Ordenar por sMAPE (menor é melhor)
        all_results.sort(key=lambda x: x.smape)
        
        return all_results
    
    def bayesian_optimization(
        self, 
        df: pd.DataFrame,
        n_iterations: int = 20,
        initial_days: int = 365,
        horizon_days: int = 30,
        period_days: int = 30
    ) -> List[BacktestResult]:
        """Otimização bayesiana para busca mais inteligente"""
        
        # Implementação simplificada de otimização bayesiana
        # Usando busca em grade com priorização baseada em resultados anteriores
        
        param_spaces = {
            'seasonality_mode': ['additive', 'multiplicative'],
            'changepoint_prior_scale': [0.005, 0.01, 0.02, 0.05, 0.1],
            'seasonality_prior_scale': [1, 2, 5, 10, 15],
            'growth': ['linear', 'logistic'],
            'changepoint_range': [0.6, 0.7, 0.8, 0.9],
            'n_changepoints': [10, 15, 20, 25, 30, 35]
        }
        
        all_results = []
        best_smape = float('inf')
        
        print(f"🧠 Iniciando otimização bayesiana com {n_iterations} iterações...")
        
        for i in range(n_iterations):
            # Priorizar parâmetros próximos aos melhores encontrados
            if i < 5 or len(all_results) < 3:
                # Primeiras iterações: busca aleatória
                params = {}
                for param_name, param_values in param_spaces.items():
                    params[param_name] = random.choice(param_values)
            else:
                # Iterações posteriores: buscar próximo aos melhores
                best_result = min(all_results, key=lambda x: x.smape)
                params = best_result.params.copy()
                
                # Perturbar um parâmetro aleatório
                param_to_change = random.choice(list(param_spaces.keys()))
                params[param_to_change] = random.choice(param_spaces[param_to_change])
            
            print(f"📊 Iteração {i+1}/{n_iterations}: {params}")
            
            try:
                results = self.rolling_cross_validation(
                    df, initial_days, horizon_days, period_days, params
                )
                
                if results:
                    avg_smape = np.mean([r.smape for r in results])
                    
                    aggregated_result = BacktestResult(
                        params=params,
                        smape=avg_smape,
                        mae=np.mean([r.mae for r in results]),
                        rmse=np.mean([r.rmse for r in results]),
                        mape=np.mean([r.mape for r in results]),
                        predictions=[],
                        actuals=[],
                        dates=[]
                    )
                    
                    all_results.append(aggregated_result)
                    
                    if avg_smape < best_smape:
                        best_smape = avg_smape
                        print(f"🎯 Novo melhor! sMAPE: {avg_smape:.2f}")
                    else:
                        print(f"✅ Iteração {i+1} - sMAPE: {avg_smape:.2f}")
                else:
                    print(f"⚠️  Iteração {i+1} - Sem resultados válidos")
                    
            except Exception as e:
                print(f"❌ Erro na iteração {i+1}: {e}")
        
        # Ordenar por sMAPE (menor é melhor)
        all_results.sort(key=lambda x: x.smape)
        
        return all_results
    
    def get_best_parameters(self, results: List[BacktestResult], metric: str = 'smape') -> Dict:
        """Retorna os melhores parâmetros baseado na métrica especificada"""
        if not results:
            return {}
        
        best_result = min(results, key=lambda x: getattr(x, metric))
        return best_result.params
    
    def get_optimization_summary(self, results: List[BacktestResult]) -> Dict:
        """Retorna um resumo da otimização"""
        if not results:
            return {}
        
        best_result = results[0]  # Já ordenado por sMAPE
        worst_result = results[-1]
        
        return {
            'best_params': best_result.params,
            'best_smape': best_result.smape,
            'best_mae': best_result.mae,
            'best_rmse': best_result.rmse,
            'worst_smape': worst_result.smape,
            'improvement': worst_result.smape - best_result.smape,
            'total_combinations_tested': len(results),
            'top_3_params': [r.params for r in results[:3]],
            'top_3_smape': [r.smape for r in results[:3]]
        }

# Instância global do serviço
backtesting_service = BacktestingService()
