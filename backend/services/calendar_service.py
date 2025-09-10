import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import calendar

class CalendarService:
    """Serviço para criar regressores de calendário específicos para pronto-socorro"""
    
    def __init__(self):
        pass
    
    def create_calendar_features(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Cria features de calendário específicas para pronto-socorro:
        - is_payday: dias 01-05 do mês (pagamento de salários)
        - month_end: últimos 2 dias do mês (fim de mês)
        - is_weekend: fim de semana
        - day_of_week: dia da semana (0=segunda, 6=domingo)
        """
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        features = []
        
        for date in dates:
            # Payday: dias 01-05 do mês (quando salários são pagos)
            is_payday = 1 if 1 <= date.day <= 5 else 0
            
            # Month end: últimos 2 dias do mês
            last_day_of_month = calendar.monthrange(date.year, date.month)[1]
            month_end = 1 if date.day >= (last_day_of_month - 1) else 0
            
            # Features básicas
            is_weekend = 1 if date.dayofweek >= 5 else 0
            day_of_week = date.dayofweek  # 0=segunda, 6=domingo
            
            # Features específicas para pronto-socorro
            is_monday = 1 if date.dayofweek == 0 else 0  # Segunda-feira (pico comum)
            is_friday = 1 if date.dayofweek == 4 else 0  # Sexta-feira (fim de semana)
            
            # Sazonalidade brasileira (inverno: maio-setembro)
            is_winter = 1 if date.month in [5, 6, 7, 8, 9] else 0
            
            # Período de férias escolares (dezembro-fevereiro)
            is_school_holiday = 1 if date.month in [12, 1, 2] else 0
            
            features.append({
                'ds': date,
                'is_payday': is_payday,
                'month_end': month_end,
                'is_weekend': is_weekend,
                'day_of_week': day_of_week,
                'is_monday': is_monday,
                'is_friday': is_friday,
                'is_winter': is_winter,
                'is_school_holiday': is_school_holiday,
                'month': date.month,
                'day_of_month': date.day,
                'quarter': (date.month - 1) // 3 + 1
            })
        
        return pd.DataFrame(features)
    
    def get_calendar_insights(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Gera insights sobre padrões de calendário
        """
        insights = []
        
        # Contar dias de payday
        payday_count = 0
        month_end_count = 0
        weekend_count = 0
        
        current = start_date
        while current <= end_date:
            if 1 <= current.day <= 5:
                payday_count += 1
            
            last_day = calendar.monthrange(current.year, current.month)[1]
            if current.day >= (last_day - 1):
                month_end_count += 1
            
            if current.dayofweek >= 5:
                weekend_count += 1
            
            current += timedelta(days=1)
        
        total_days = (end_date - start_date).days + 1
        
        insights.append({
            "type": "calendar_patterns",
            "title": "Padrões de Calendário",
            "description": f"Período analisado: {total_days} dias",
            "details": {
                "payday_days": payday_count,
                "month_end_days": month_end_count,
                "weekend_days": weekend_count,
                "payday_percentage": round((payday_count / total_days) * 100, 1),
                "month_end_percentage": round((month_end_count / total_days) * 100, 1),
                "weekend_percentage": round((weekend_count / total_days) * 100, 1)
            }
        })
        
        return insights

# Instância global do serviço
calendar_service = CalendarService()
