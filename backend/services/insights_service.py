import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class InsightsService:
    """Serviço para gerar insights derivados das previsões"""
    
    def __init__(self):
        pass
    
    def generate_forecast_insights(self, 
                                 forecast_df: pd.DataFrame, 
                                 historical_df: Optional[pd.DataFrame] = None,
                                 weather_insights: List[Dict] = None,
                                 holiday_insights: List[Dict] = None) -> List[Dict]:
        """
        Gera insights derivados das previsões
        """
        insights = []
        
        if forecast_df is None or forecast_df.empty:
            return insights
        
        # Insights de tendência
        trend_insights = self._analyze_trends(forecast_df)
        insights.extend(trend_insights)
        
        # Insights de sazonalidade
        seasonal_insights = self._analyze_seasonality(forecast_df)
        insights.extend(seasonal_insights)
        
        # Insights de picos e vales
        peak_insights = self._analyze_peaks_and_valleys(forecast_df)
        insights.extend(peak_insights)
        
        # Insights comparativos com histórico
        if historical_df is not None and not historical_df.empty:
            comparison_insights = self._compare_with_historical(forecast_df, historical_df)
            insights.extend(comparison_insights)
        
        # Combinar insights de clima e feriados
        if weather_insights:
            insights.extend(weather_insights)
        
        if holiday_insights:
            insights.extend(holiday_insights)
        
        # Insights de capacidade
        capacity_insights = self._analyze_capacity_requirements(forecast_df)
        insights.extend(capacity_insights)
        
        # Ordenar insights por impacto
        insights.sort(key=lambda x: self._get_impact_priority(x.get('impact', 'low')), reverse=True)
        
        return insights
    
    def _analyze_trends(self, forecast_df: pd.DataFrame) -> List[Dict]:
        """
        Analisa tendências nas previsões
        """
        insights = []
        
        if len(forecast_df) < 7:  # Precisa de pelo menos uma semana
            return insights
        
        # Calcular tendência semanal
        weekly_avg = forecast_df['yhat'].rolling(window=7, min_periods=1).mean()
        trend_slope = np.polyfit(range(len(weekly_avg)), weekly_avg, 1)[0]
        
        # Calcular tendência mensal se houver dados suficientes
        if len(forecast_df) >= 30:
            monthly_avg = forecast_df['yhat'].rolling(window=30, min_periods=1).mean()
            monthly_trend = np.polyfit(range(len(monthly_avg)), monthly_avg, 1)[0]
            
            if abs(monthly_trend) > 0.5:  # Tendência significativa
                trend_direction = "crescente" if monthly_trend > 0 else "decrescente"
                trend_strength = abs(monthly_trend)
                
                insights.append({
                    "type": "trend_analysis",
                    "title": f"Tendência {trend_direction.title()} Detectada",
                    "message": f"Tendência {trend_direction} de {trend_strength:.1f} atendimentos/dia. Expectativa de {'aumento' if monthly_trend > 0 else 'redução'} na demanda ao longo do período.",
                    "impact": "high" if trend_strength > 2 else "medium",
                    "trend_direction": trend_direction,
                    "trend_strength": trend_strength
                })
        
        return insights
    
    def _analyze_seasonality(self, forecast_df: pd.DataFrame) -> List[Dict]:
        """
        Analisa padrões sazonais nas previsões
        """
        insights = []
        
        if len(forecast_df) < 14:  # Precisa de pelo menos 2 semanas
            return insights
        
        # Analisar padrão semanal
        forecast_df['day_of_week'] = forecast_df['ds'].dt.dayofweek
        weekly_pattern = forecast_df.groupby('day_of_week')['yhat'].mean()
        
        # Identificar dias de maior/menor demanda
        max_day = weekly_pattern.idxmax()
        min_day = weekly_pattern.idxmin()
        max_value = weekly_pattern.max()
        min_value = weekly_pattern.min()
        
        day_names = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        if max_value - min_value > 10:  # Diferença significativa
            insights.append({
                "type": "weekly_pattern",
                "title": "Padrão Semanal Identificado",
                "message": f"Maior demanda prevista nas {day_names[max_day]}s ({max_value:.0f} atendimentos) e menor nas {day_names[min_day]}s ({min_value:.0f} atendimentos). Diferença de {max_value - min_value:.0f} atendimentos.",
                "impact": "medium",
                "peak_day": day_names[max_day],
                "low_day": day_names[min_day],
                "difference": max_value - min_value
            })
        
        return insights
    
    def _analyze_peaks_and_valleys(self, forecast_df: pd.DataFrame) -> List[Dict]:
        """
        Analisa picos e vales nas previsões
        """
        insights = []
        
        if len(forecast_df) < 7:
            return insights
        
        # Encontrar picos (valores acima de 1.2x da média)
        mean_demand = forecast_df['yhat'].mean()
        threshold_high = mean_demand * 1.2
        threshold_low = mean_demand * 0.8
        
        peaks = forecast_df[forecast_df['yhat'] > threshold_high]
        valleys = forecast_df[forecast_df['yhat'] < threshold_low]
        
        # Analisar picos
        if not peaks.empty:
            max_peak = peaks.loc[peaks['yhat'].idxmax()]
            peak_date = max_peak['ds']
            peak_value = max_peak['yhat']
            increase_percent = ((peak_value - mean_demand) / mean_demand) * 100
            
            insights.append({
                "type": "demand_peak",
                "title": "Pico de Demanda Identificado",
                "message": f"Pico de demanda previsto em {peak_date.strftime('%d/%m/%Y')} com {peak_value:.0f} atendimentos (+{increase_percent:.0f}% acima da média). Prepare recursos adicionais.",
                "impact": "high",
                "date": peak_date.strftime("%Y-%m-%d"),
                "value": peak_value,
                "increase_percent": increase_percent
            })
        
        # Analisar vales
        if not valleys.empty:
            min_valley = valleys.loc[valleys['yhat'].idxmin()]
            valley_date = min_valley['ds']
            valley_value = min_valley['yhat']
            decrease_percent = ((mean_demand - valley_value) / mean_demand) * 100
            
            insights.append({
                "type": "demand_valley",
                "title": "Vale de Demanda Identificado",
                "message": f"Menor demanda prevista em {valley_date.strftime('%d/%m/%Y')} com {valley_value:.0f} atendimentos (-{decrease_percent:.0f}% abaixo da média). Oportunidade para manutenção preventiva.",
                "impact": "medium",
                "date": valley_date.strftime("%Y-%m-%d"),
                "value": valley_value,
                "decrease_percent": decrease_percent
            })
        
        return insights
    
    def _compare_with_historical(self, forecast_df: pd.DataFrame, historical_df: pd.DataFrame) -> List[Dict]:
        """
        Compara previsões com dados históricos
        """
        insights = []
        
        if historical_df.empty:
            return insights
        
        # Calcular métricas históricas
        hist_mean = historical_df['y'].mean()
        hist_std = historical_df['y'].std()
        hist_max = historical_df['y'].max()
        
        # Calcular métricas da previsão
        forecast_mean = forecast_df['yhat'].mean()
        forecast_max = forecast_df['yhat'].max()
        
        # Comparar com histórico
        if forecast_mean > hist_mean * 1.1:  # 10% acima da média histórica
            increase_percent = ((forecast_mean - hist_mean) / hist_mean) * 100
            insights.append({
                "type": "historical_comparison",
                "title": "Demanda Acima da Média Histórica",
                "message": f"Previsão indica demanda {increase_percent:.0f}% acima da média histórica ({hist_mean:.0f} vs {forecast_mean:.0f} atendimentos/dia). Considere aumentar a capacidade.",
                "impact": "high",
                "historical_mean": hist_mean,
                "forecast_mean": forecast_mean,
                "increase_percent": increase_percent
            })
        
        # Verificar se vai superar recorde histórico
        if forecast_max > hist_max:
            insights.append({
                "type": "record_breaking",
                "title": "Possível Novo Recorde de Demanda",
                "message": f"Previsão indica possível novo recorde de {forecast_max:.0f} atendimentos (atual: {hist_max:.0f}). Prepare-se para demanda excepcional.",
                "impact": "high",
                "current_record": hist_max,
                "predicted_record": forecast_max
            })
        
        return insights
    
    def _analyze_capacity_requirements(self, forecast_df: pd.DataFrame) -> List[Dict]:
        """
        Analisa requisitos de capacidade baseados nas previsões
        """
        insights = []
        
        if forecast_df.empty:
            return insights
        
        # Calcular métricas de capacidade
        max_demand = forecast_df['yhat'].max()
        mean_demand = forecast_df['yhat'].mean()
        p95_demand = forecast_df['yhat'].quantile(0.95)
        
        # Estimar capacidade necessária (assumindo 80% de ocupação ideal)
        required_capacity = max_demand / 0.8
        
        insights.append({
            "type": "capacity_planning",
            "title": "Análise de Capacidade",
            "message": f"Demanda máxima prevista: {max_demand:.0f} atendimentos. Capacidade recomendada: {required_capacity:.0f} leitos (80% ocupação). P95: {p95_demand:.0f} atendimentos.",
            "impact": "medium",
            "max_demand": max_demand,
            "recommended_capacity": required_capacity,
            "p95_demand": p95_demand
        })
        
        # Alertas de capacidade
        if max_demand > mean_demand * 1.5:  # 50% acima da média
            insights.append({
                "type": "capacity_alert",
                "title": "Alerta de Capacidade",
                "message": f"Picos de demanda podem exceder 50% da média. Considere protocolos de contingência e escalonamento de equipes.",
                "impact": "high",
                "peak_ratio": max_demand / mean_demand
            })
        
        return insights
    
    def _get_impact_priority(self, impact: str) -> int:
        """
        Retorna prioridade numérica para ordenação dos insights
        """
        priority_map = {
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return priority_map.get(impact, 1)
    
    def format_insights_for_frontend(self, insights: List[Dict]) -> Dict:
        """
        Formata insights para exibição no frontend
        """
        if not insights:
            return {
                "total_insights": 0,
                "high_impact": 0,
                "medium_impact": 0,
                "low_impact": 0,
                "insights": []
            }
        
        # Contar por impacto
        impact_counts = {"high": 0, "medium": 0, "low": 0}
        for insight in insights:
            impact = insight.get("impact", "low")
            impact_counts[impact] += 1
        
        return {
            "total_insights": len(insights),
            "high_impact": impact_counts["high"],
            "medium_impact": impact_counts["medium"],
            "low_impact": impact_counts["low"],
            "insights": insights[:10]  # Limitar a 10 insights mais importantes
        }

# Instância global do serviço
insights_service = InsightsService()

