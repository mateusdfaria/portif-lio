import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

class WeatherService:
    """Serviço para buscar dados climáticos"""
    
    def __init__(self):
        # Usar OpenWeatherMap API (gratuita com limite)
        self.api_key = None  # Pode ser configurado via env
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_weather_forecast(self, latitude: float, longitude: float, days: int = 14) -> Optional[pd.DataFrame]:
        """
        Busca previsão do tempo para os próximos dias
        """
        try:
            if not self.api_key:
                print("⚠️  API key do OpenWeatherMap não configurada. Usando dados simulados.")
                return self._generate_simulated_weather(latitude, longitude, days)
            
            # Buscar previsão do tempo
            url = f"{self.base_url}/forecast"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 previsões por dia (3 horas cada)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Processar dados
            weather_data = []
            for item in data['list']:
                weather_data.append({
                    'ds': pd.to_datetime(item['dt_txt']),
                    'tmax': item['main']['temp_max'],
                    'tmin': item['main']['temp_min'],
                    'precip': item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0)
                })
            
            df = pd.DataFrame(weather_data)
            
            # Agrupar por dia e calcular médias
            df['date'] = df['ds'].dt.date
            daily_weather = df.groupby('date').agg({
                'tmax': 'max',
                'tmin': 'min',
                'precip': 'sum'
            }).reset_index()
            
            daily_weather['ds'] = pd.to_datetime(daily_weather['date'])
            daily_weather = daily_weather.drop('date', axis=1)
            
            return daily_weather.head(days)
            
        except Exception as e:
            print(f"❌ Erro ao buscar dados climáticos: {e}")
            return self._generate_simulated_weather(latitude, longitude, days)
    
    def _generate_simulated_weather(self, latitude: float, longitude: float, days: int) -> pd.DataFrame:
        """
        Gera dados climáticos simulados baseados na localização
        """
        print(f"🌤️  Gerando dados climáticos simulados para {days} dias")
        
        # Determinar estação baseada na latitude
        if latitude < -15:  # Sul do Brasil
            # Inverno: junho-agosto, Verão: dezembro-fevereiro
            base_temp = 20
            temp_variation = 8
        elif latitude < -5:  # Centro do Brasil
            base_temp = 25
            temp_variation = 6
        else:  # Norte do Brasil
            base_temp = 28
            temp_variation = 4
        
        # Gerar dados para os próximos dias
        dates = pd.date_range(start=datetime.now(), periods=days, freq='D')
        weather_data = []
        
        for i, date in enumerate(dates):
            # Variação sazonal
            day_of_year = date.timetuple().tm_yday
            seasonal_factor = np.sin(2 * np.pi * day_of_year / 365)
            
            # Temperatura com variação sazonal e aleatória
            temp_base = base_temp + seasonal_factor * temp_variation
            temp_noise = np.random.normal(0, 2)
            
            tmax = max(temp_base + temp_noise + 3, 15)  # Mínimo 15°C
            tmin = max(temp_base + temp_noise - 3, 10)  # Mínimo 10°C
            
            # Precipitação (mais comum no verão)
            precip_prob = 0.3 + 0.2 * seasonal_factor  # 30-50% chance
            precip = np.random.exponential(5) if np.random.random() < precip_prob else 0
            
            weather_data.append({
                'ds': date,
                'tmax': round(tmax, 1),
                'tmin': round(tmin, 1),
                'precip': round(precip, 1)
            })
        
        return pd.DataFrame(weather_data)
    
    def get_enhanced_weather_forecast(self, latitude: float, longitude: float, days: int = 14) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Busca previsão do tempo aprimorada com insights
        Retorna: (DataFrame com dados climáticos, Lista de insights)
        """
        weather_df = self.get_weather_forecast(latitude, longitude, days)
        insights = []
        
        if weather_df is not None and not weather_df.empty:
            # Analisar padrões climáticos
            insights.extend(self._analyze_weather_patterns(weather_df))
            
            # Adicionar variáveis climáticas derivadas
            weather_df = self._add_derived_weather_variables(weather_df)
        
        return weather_df, insights
    
    def _add_derived_weather_variables(self, weather_df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona variáveis climáticas derivadas que afetam a saúde
        """
        df = weather_df.copy()
        
        # Temperatura média
        df['temp_avg'] = (df['tmax'] + df['tmin']) / 2
        
        # Amplitude térmica (diferença entre máxima e mínima)
        df['temp_range'] = df['tmax'] - df['tmin']
        
        # Índice de conforto térmico (baseado na temperatura média)
        df['thermal_comfort'] = np.where(
            (df['temp_avg'] >= 20) & (df['temp_avg'] <= 26), 1, 0
        )
        
        # Risco de doenças respiratórias (temperaturas baixas + alta amplitude)
        df['respiratory_risk'] = np.where(
            (df['temp_avg'] < 18) | (df['temp_range'] > 12), 1, 0
        )
        
        # Risco de desidratação (temperaturas altas)
        df['dehydration_risk'] = np.where(df['tmax'] > 32, 1, 0)
        
        # Risco de acidentes (chuva intensa)
        df['accident_risk'] = np.where(df['precip'] > 20, 1, 0)
        
        # Estação do ano
        df['month'] = df['ds'].dt.month
        df['is_winter'] = df['month'].isin([6, 7, 8]).astype(int)
        df['is_summer'] = df['month'].isin([12, 1, 2]).astype(int)
        
        # Garantir que não há valores NaN
        df = df.fillna(0)
        
        return df
    
    def _analyze_weather_patterns(self, weather_df: pd.DataFrame) -> List[Dict]:
        """
        Analisa padrões climáticos e gera insights sobre impacto na saúde
        """
        insights = []
        
        # Analisar ondas de calor
        heat_waves = self._detect_heat_waves(weather_df)
        if heat_waves:
            insights.extend(heat_waves)
        
        # Analisar períodos de frio intenso
        cold_periods = self._detect_cold_periods(weather_df)
        if cold_periods:
            insights.extend(cold_periods)
        
        # Analisar períodos de chuva intensa
        heavy_rain = self._detect_heavy_rain(weather_df)
        if heavy_rain:
            insights.extend(heavy_rain)
        
        # Analisar variações térmicas extremas
        thermal_variations = self._detect_thermal_variations(weather_df)
        if thermal_variations:
            insights.extend(thermal_variations)
        
        return insights
    
    def _detect_heat_waves(self, weather_df: pd.DataFrame) -> List[Dict]:
        """
        Detecta ondas de calor (3+ dias consecutivos com tmax > 32°C)
        """
        insights = []
        df = weather_df.copy()
        df['is_hot'] = df['tmax'] > 32
        
        # Encontrar sequências de dias quentes
        hot_sequences = []
        current_sequence = []
        
        for i, row in df.iterrows():
            if row['is_hot']:
                current_sequence.append(i)
            else:
                if len(current_sequence) >= 3:  # 3+ dias consecutivos
                    hot_sequences.append(current_sequence)
                current_sequence = []
        
        # Adicionar última sequência se terminar no final
        if len(current_sequence) >= 3:
            hot_sequences.append(current_sequence)
        
        for sequence in hot_sequences:
            start_date = df.iloc[sequence[0]]['ds']
            end_date = df.iloc[sequence[-1]]['ds']
            max_temp = df.iloc[sequence]['tmax'].max()
            
            insights.append({
                "type": "heat_wave",
                "title": "Onda de Calor Detectada",
                "message": f"Período de {len(sequence)} dias com temperaturas acima de 32°C (máx: {max_temp:.1f}°C). Expectativa de aumento de 15-25% na demanda por desidratação e insolação.",
                "impact": "high",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "expected_increase": "15-25%"
            })
        
        return insights
    
    def _detect_cold_periods(self, weather_df: pd.DataFrame) -> List[Dict]:
        """
        Detecta períodos de frio intenso (3+ dias consecutivos com tmin < 10°C)
        """
        insights = []
        df = weather_df.copy()
        df['is_cold'] = df['tmin'] < 10
        
        # Encontrar sequências de dias frios
        cold_sequences = []
        current_sequence = []
        
        for i, row in df.iterrows():
            if row['is_cold']:
                current_sequence.append(i)
            else:
                if len(current_sequence) >= 3:  # 3+ dias consecutivos
                    cold_sequences.append(current_sequence)
                current_sequence = []
        
        # Adicionar última sequência se terminar no final
        if len(current_sequence) >= 3:
            cold_sequences.append(current_sequence)
        
        for sequence in cold_sequences:
            start_date = df.iloc[sequence[0]]['ds']
            end_date = df.iloc[sequence[-1]]['ds']
            min_temp = df.iloc[sequence]['tmin'].min()
            
            insights.append({
                "type": "cold_period",
                "title": "Período de Frio Intenso",
                "message": f"Período de {len(sequence)} dias com temperaturas mínimas abaixo de 10°C (mín: {min_temp:.1f}°C). Expectativa de aumento de 20-30% na demanda por doenças respiratórias.",
                "impact": "high",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "expected_increase": "20-30%"
            })
        
        return insights
    
    def _detect_heavy_rain(self, weather_df: pd.DataFrame) -> List[Dict]:
        """
        Detecta períodos de chuva intensa (precipitação > 20mm em 1 dia)
        """
        insights = []
        df = weather_df.copy()
        heavy_rain_days = df[df['precip'] > 20]
        
        for _, row in heavy_rain_days.iterrows():
            insights.append({
                "type": "heavy_rain",
                "title": "Chuva Intensa Prevista",
                "message": f"Chuva intensa prevista ({row['precip']:.1f}mm). Expectativa de aumento de 10-20% na demanda por acidentes de trânsito e quedas.",
                "impact": "medium",
                "date": row['ds'].strftime("%Y-%m-%d"),
                "expected_increase": "10-20%"
            })
        
        return insights
    
    def _detect_thermal_variations(self, weather_df: pd.DataFrame) -> List[Dict]:
        """
        Detecta variações térmicas extremas (amplitude > 15°C)
        """
        insights = []
        df = weather_df.copy()
        df['temp_range'] = df['tmax'] - df['tmin']
        extreme_variations = df[df['temp_range'] > 15]
        
        for _, row in extreme_variations.iterrows():
            insights.append({
                "type": "thermal_variation",
                "title": "Variação Térmica Extrema",
                "message": f"Grande variação térmica prevista (amplitude: {row['temp_range']:.1f}°C). Expectativa de aumento de 5-15% na demanda por problemas respiratórios.",
                "impact": "medium",
                "date": row['ds'].strftime("%Y-%m-%d"),
                "expected_increase": "5-15%"
            })
        
        return insights

# Instância global do serviço
weather_service = WeatherService()
