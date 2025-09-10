import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import requests
import numpy as np

class HolidaysService:
    """Serviço para buscar feriados brasileiros e eventos extraordinários"""
    
    def __init__(self):
        self.brasil_api_url = "https://brasilapi.com.br/api/feriados/v1"
        self.extraordinary_events = self._load_extraordinary_events()
    
    def get_holidays(self, year: int) -> List[Dict]:
        """
        Busca feriados brasileiros para um ano específico
        """
        try:
            # Tentar usar BrasilAPI
            response = requests.get(f"{self.brasil_api_url}/{year}", timeout=10)
            if response.status_code == 200:
                holidays = response.json()
                return [{"date": h["date"], "name": h["name"]} for h in holidays]
        except Exception as e:
            print(f"⚠️  Erro ao buscar feriados da BrasilAPI: {e}")
        
        # Fallback: feriados fixos brasileiros
        return self._get_fixed_holidays(year)
    
    def _get_fixed_holidays(self, year: int) -> List[Dict]:
        """
        Lista de feriados fixos brasileiros
        """
        fixed_holidays = [
            {"date": f"{year}-01-01", "name": "Confraternização Universal"},
            {"date": f"{year}-04-21", "name": "Tiradentes"},
            {"date": f"{year}-05-01", "name": "Dia do Trabalhador"},
            {"date": f"{year}-09-07", "name": "Independência do Brasil"},
            {"date": f"{year}-10-12", "name": "Nossa Senhora Aparecida"},
            {"date": f"{year}-11-02", "name": "Finados"},
            {"date": f"{year}-11-15", "name": "Proclamação da República"},
            {"date": f"{year}-12-25", "name": "Natal"},
        ]
        
        # Adicionar feriados móveis (aproximação)
        easter = self._calculate_easter(year)
        good_friday = easter - timedelta(days=2)
        carnival = easter - timedelta(days=47)
        corpus_christi = easter + timedelta(days=60)
        
        mobile_holidays = [
            {"date": carnival.strftime(f"{year}-%m-%d"), "name": "Carnaval"},
            {"date": good_friday.strftime(f"{year}-%m-%d"), "name": "Sexta-feira Santa"},
            {"date": corpus_christi.strftime(f"{year}-%m-%d"), "name": "Corpus Christi"},
        ]
        
        return fixed_holidays + mobile_holidays
    
    def _calculate_easter(self, year: int) -> datetime:
        """
        Calcula a data da Páscoa usando o algoritmo de Gauss
        """
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        
        return datetime(year, month, day)
    
    def create_holiday_regressor(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Cria um DataFrame com regressor de feriados para um período
        """
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        holiday_data = []
        
        # Buscar feriados para os anos no período
        years = list(range(start_date.year, end_date.year + 1))
        all_holidays = []
        
        for year in years:
            all_holidays.extend(self.get_holidays(year))
        
        # Converter para DataFrame
        holiday_df = pd.DataFrame(all_holidays)
        if not holiday_df.empty:
            holiday_df['date'] = pd.to_datetime(holiday_df['date'])
        
        # Criar regressor
        for date in dates:
            is_holiday = 0
            if not holiday_df.empty:
                is_holiday = 1 if date.date() in holiday_df['date'].dt.date.values else 0
            
            holiday_data.append({
                'ds': date,
                'is_holiday': is_holiday
            })
        
        return pd.DataFrame(holiday_data)
    
    def _load_extraordinary_events(self) -> List[Dict]:
        """
        Carrega eventos extraordinários que afetam a demanda hospitalar
        """
        return [
            # Pandemia COVID-19
            {
                "name": "Pandemia COVID-19",
                "start_date": "2020-03-01",
                "end_date": "2022-12-31",
                "impact_factor": 1.5,  # 50% de aumento
                "description": "Pandemia de COVID-19 - aumento significativo na demanda"
            },
            # Greves de saúde
            {
                "name": "Greve Geral Saúde",
                "start_date": "2023-06-01",
                "end_date": "2023-06-15",
                "impact_factor": 0.7,  # 30% de redução
                "description": "Greve geral dos profissionais de saúde"
            },
            # Eventos de massa (Carnaval, Copa do Mundo, etc.)
            {
                "name": "Carnaval 2024",
                "start_date": "2024-02-10",
                "end_date": "2024-02-14",
                "impact_factor": 1.3,  # 30% de aumento
                "description": "Carnaval - aumento de acidentes e intoxicações"
            },
            {
                "name": "Copa do Mundo 2022",
                "start_date": "2022-11-20",
                "end_date": "2022-12-18",
                "impact_factor": 1.2,  # 20% de aumento
                "description": "Copa do Mundo - aumento de acidentes domésticos"
            },
            # Inverno rigoroso
            {
                "name": "Inverno Rigoroso 2023",
                "start_date": "2023-06-01",
                "end_date": "2023-08-31",
                "impact_factor": 1.15,  # 15% de aumento
                "description": "Inverno com temperaturas muito baixas - aumento de doenças respiratórias"
            }
        ]
    
    def get_extraordinary_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Retorna eventos extraordinários que ocorrem no período especificado
        """
        events_in_period = []
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        for event in self.extraordinary_events:
            if (event["start_date"] <= end_str and event["end_date"] >= start_str):
                events_in_period.append(event)
        
        return events_in_period
    
    def create_enhanced_holiday_regressor(self, start_date: datetime, end_date: datetime) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Cria um DataFrame aprimorado com regressores de feriados e eventos extraordinários
        Retorna: (DataFrame com regressores, Lista de insights)
        """
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        regressor_data = []
        insights = []
        
        # Buscar feriados
        years = list(range(start_date.year, end_date.year + 1))
        all_holidays = []
        
        for year in years:
            all_holidays.extend(self.get_holidays(year))
        
        # Converter para DataFrame
        holiday_df = pd.DataFrame(all_holidays)
        if not holiday_df.empty:
            holiday_df['date'] = pd.to_datetime(holiday_df['date'])
        
        # Buscar eventos extraordinários
        extraordinary_events = self.get_extraordinary_events(start_date, end_date)
        
        # Analisar feriados prolongados
        holiday_analysis = self._analyze_holiday_patterns(all_holidays, start_date, end_date)
        insights.extend(holiday_analysis)
        
        # Analisar eventos extraordinários
        event_insights = self._analyze_extraordinary_events(extraordinary_events, start_date, end_date)
        insights.extend(event_insights)
        
        # Criar regressores
        for date in dates:
            is_holiday = 0
            is_extraordinary_event = 0
            event_impact = 1.0
            
            # Verificar se é feriado
            if not holiday_df.empty:
                is_holiday = 1 if date.date() in holiday_df['date'].dt.date.values else 0
            
            # Verificar eventos extraordinários
            for event in extraordinary_events:
                event_start = datetime.strptime(event["start_date"], "%Y-%m-%d").date()
                event_end = datetime.strptime(event["end_date"], "%Y-%m-%d").date()
                
                if event_start <= date.date() <= event_end:
                    is_extraordinary_event = 1
                    event_impact = event["impact_factor"]
                    break
            
            regressor_data.append({
                'ds': date,
                'is_holiday': is_holiday,
                'is_extraordinary_event': is_extraordinary_event,
                'event_impact_factor': event_impact,
                'is_holiday_weekend': 1 if is_holiday and date.weekday() >= 5 else 0,
                'is_holiday_monday': 1 if is_holiday and date.weekday() == 0 else 0
            })
        
        return pd.DataFrame(regressor_data), insights
    
    def _analyze_holiday_patterns(self, holidays: List[Dict], start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Analisa padrões de feriados e gera insights
        """
        insights = []
        
        # Verificar feriados prolongados (sexta + segunda)
        for holiday in holidays:
            holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d")
            
            if start_date <= holiday_date <= end_date:
                # Verificar se forma ponte
                if holiday_date.weekday() == 4:  # Sexta-feira
                    monday_after = holiday_date + timedelta(days=3)
                    if monday_after <= end_date:
                        insights.append({
                            "type": "holiday_bridge",
                            "title": "Feriado Prolongado Detectado",
                            "message": f"Feriado de {holiday['name']} forma ponte (sexta + segunda). Expectativa de aumento de 15-25% na demanda.",
                            "impact": "high",
                            "date": holiday_date.strftime("%Y-%m-%d"),
                            "expected_increase": "15-25%"
                        })
                
                # Verificar feriados em dias úteis
                elif holiday_date.weekday() < 5:  # Dia útil
                    insights.append({
                        "type": "weekday_holiday",
                        "title": "Feriado em Dia Útil",
                        "message": f"Feriado de {holiday['name']} em dia útil. Expectativa de redução de 30-40% na demanda.",
                        "impact": "medium",
                        "date": holiday_date.strftime("%Y-%m-%d"),
                        "expected_change": "redução de 30-40%"
                    })
        
        return insights
    
    def _analyze_extraordinary_events(self, events: List[Dict], start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Analisa eventos extraordinários e gera insights
        """
        insights = []
        
        for event in events:
            event_start = datetime.strptime(event["start_date"], "%Y-%m-%d")
            event_end = datetime.strptime(event["end_date"], "%Y-%m-%d")
            
            # Verificar se o evento está no período de previsão
            if event_start <= end_date and event_end >= start_date:
                impact_type = "aumento" if event["impact_factor"] > 1 else "redução"
                impact_percent = abs((event["impact_factor"] - 1) * 100)
                
                insights.append({
                    "type": "extraordinary_event",
                    "title": f"Evento Extraordinário: {event['name']}",
                    "message": f"{event['description']}. Expectativa de {impact_type} de {impact_percent:.0f}% na demanda.",
                    "impact": "high" if abs(event["impact_factor"] - 1) > 0.2 else "medium",
                    "start_date": event["start_date"],
                    "end_date": event["end_date"],
                    "expected_change": f"{impact_type} de {impact_percent:.0f}%"
                })
        
        return insights

# Instância global do serviço
holidays_service = HolidaysService()