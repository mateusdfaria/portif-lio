import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

class AlertLevel(Enum):
    """Níveis de alerta"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """Tipos de alerta"""
    OCCUPANCY_HIGH = "occupancy_high"
    EMERGENCY_OVERLOAD = "emergency_overload"
    ICU_OVERLOAD = "icu_overload"
    WAIT_TIME_HIGH = "wait_time_high"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    TREND_INCREASING = "trend_increasing"
    STAFF_SHORTAGE = "staff_shortage"
    EQUIPMENT_ISSUE = "equipment_issue"

@dataclass
class Alert:
    """Estrutura de um alerta"""
    id: str
    hospital_id: str
    hospital_name: str
    alert_type: AlertType
    level: AlertLevel
    title: str
    message: str
    timestamp: str
    value: float
    threshold: float
    unit: str
    is_active: bool
    acknowledged: bool
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[str]
    resolved: bool
    resolved_at: Optional[str]
    metadata: Dict

class AlertsService:
    """Serviço para gerenciar alertas hospitalares"""
    
    def __init__(self):
        self.alerts = []
        self.alert_rules = self._load_alert_rules()
        self.next_alert_id = 1
    
    def _load_alert_rules(self) -> Dict:
        """Carrega regras de alerta configuráveis"""
        return {
            AlertType.OCCUPANCY_HIGH: {
                "threshold": 85.0,
                "unit": "%",
                "level": AlertLevel.HIGH,
                "title": "Taxa de Ocupação Alta",
                "message_template": "Taxa de ocupação geral está em {value}%, acima do limite de {threshold}%"
            },
            AlertType.EMERGENCY_OVERLOAD: {
                "threshold": 90.0,
                "unit": "%",
                "level": AlertLevel.CRITICAL,
                "title": "Emergência Sobrecarregada",
                "message_template": "Taxa de ocupação da emergência está em {value}%, acima do limite crítico de {threshold}%"
            },
            AlertType.ICU_OVERLOAD: {
                "threshold": 95.0,
                "unit": "%",
                "level": AlertLevel.CRITICAL,
                "title": "UTI Sobrecarregada",
                "message_template": "Taxa de ocupação da UTI está em {value}%, acima do limite crítico de {threshold}%"
            },
            AlertType.WAIT_TIME_HIGH: {
                "threshold": 120.0,
                "unit": "min",
                "level": AlertLevel.MEDIUM,
                "title": "Tempo de Espera Alto",
                "message_template": "Tempo médio de espera está em {value} minutos, acima do limite de {threshold} minutos"
            },
            AlertType.CAPACITY_EXCEEDED: {
                "threshold": 100.0,
                "unit": "%",
                "level": AlertLevel.CRITICAL,
                "title": "Capacidade Excedida",
                "message_template": "Capacidade hospitalar foi excedida em {value}%, acima do limite de {threshold}%"
            },
            AlertType.TREND_INCREASING: {
                "threshold": 10.0,
                "unit": "%",
                "level": AlertLevel.MEDIUM,
                "title": "Tendência de Aumento",
                "message_template": "Tendência de aumento de {value}% na ocupação nos últimos 7 dias"
            },
            AlertType.STAFF_SHORTAGE: {
                "threshold": 80.0,
                "unit": "%",
                "level": AlertLevel.HIGH,
                "title": "Escassez de Funcionários",
                "message_template": "Taxa de funcionários disponíveis está em {value}%, abaixo do limite de {threshold}%"
            },
            AlertType.EQUIPMENT_ISSUE: {
                "threshold": 90.0,
                "unit": "%",
                "level": AlertLevel.MEDIUM,
                "title": "Problema com Equipamentos",
                "message_template": "Taxa de equipamentos funcionais está em {value}%, abaixo do limite de {threshold}%"
            }
        }
    
    def check_hospital_alerts(self, hospital_id: str, hospital_name: str, 
                            metrics: Dict, historical_data: List[Dict] = None) -> List[Alert]:
        """Verifica alertas para um hospital baseado nas métricas"""
        new_alerts = []
        
        # Verificar alertas de ocupação
        if 'occupancy_rate' in metrics:
            occupancy_rate = metrics['occupancy_rate'] * 100
            if occupancy_rate >= self.alert_rules[AlertType.OCCUPANCY_HIGH]['threshold']:
                alert = self._create_alert(
                    hospital_id, hospital_name, AlertType.OCCUPANCY_HIGH,
                    occupancy_rate, self.alert_rules[AlertType.OCCUPANCY_HIGH]
                )
                new_alerts.append(alert)
        
        # Verificar alertas de emergência
        if 'emergency_occupancy' in metrics:
            emergency_occupancy = metrics['emergency_occupancy'] * 100
            if emergency_occupancy >= self.alert_rules[AlertType.EMERGENCY_OVERLOAD]['threshold']:
                alert = self._create_alert(
                    hospital_id, hospital_name, AlertType.EMERGENCY_OVERLOAD,
                    emergency_occupancy, self.alert_rules[AlertType.EMERGENCY_OVERLOAD]
                )
                new_alerts.append(alert)
        
        # Verificar alertas de UTI
        if 'icu_occupancy' in metrics:
            icu_occupancy = metrics['icu_occupancy'] * 100
            if icu_occupancy >= self.alert_rules[AlertType.ICU_OVERLOAD]['threshold']:
                alert = self._create_alert(
                    hospital_id, hospital_name, AlertType.ICU_OVERLOAD,
                    icu_occupancy, self.alert_rules[AlertType.ICU_OVERLOAD]
                )
                new_alerts.append(alert)
        
        # Verificar alertas de tempo de espera
        if 'avg_wait_time' in metrics:
            wait_time = metrics['avg_wait_time']
            if wait_time >= self.alert_rules[AlertType.WAIT_TIME_HIGH]['threshold']:
                alert = self._create_alert(
                    hospital_id, hospital_name, AlertType.WAIT_TIME_HIGH,
                    wait_time, self.alert_rules[AlertType.WAIT_TIME_HIGH]
                )
                new_alerts.append(alert)
        
        # Verificar alertas de capacidade excedida
        if 'occupancy_rate' in metrics:
            occupancy_rate = metrics['occupancy_rate'] * 100
            if occupancy_rate >= self.alert_rules[AlertType.CAPACITY_EXCEEDED]['threshold']:
                alert = self._create_alert(
                    hospital_id, hospital_name, AlertType.CAPACITY_EXCEEDED,
                    occupancy_rate, self.alert_rules[AlertType.CAPACITY_EXCEEDED]
                )
                new_alerts.append(alert)
        
        # Verificar tendências se dados históricos estiverem disponíveis
        if historical_data and len(historical_data) >= 14:
            trend_alert = self._check_trend_alerts(hospital_id, hospital_name, historical_data)
            if trend_alert:
                new_alerts.append(trend_alert)
        
        # Adicionar novos alertas à lista
        for alert in new_alerts:
            self.alerts.append(alert)
        
        return new_alerts
    
    def _create_alert(self, hospital_id: str, hospital_name: str, alert_type: AlertType,
                     value: float, rule: Dict) -> Alert:
        """Cria um novo alerta"""
        alert_id = f"alert_{self.next_alert_id}"
        self.next_alert_id += 1
        
        message = rule['message_template'].format(
            value=round(value, 1),
            threshold=rule['threshold']
        )
        
        return Alert(
            id=alert_id,
            hospital_id=hospital_id,
            hospital_name=hospital_name,
            alert_type=alert_type,
            level=rule['level'],
            title=rule['title'],
            message=message,
            timestamp=datetime.now().isoformat(),
            value=value,
            threshold=rule['threshold'],
            unit=rule['unit'],
            is_active=True,
            acknowledged=False,
            acknowledged_by=None,
            acknowledged_at=None,
            resolved=False,
            resolved_at=None,
            metadata={}
        )
    
    def _check_trend_alerts(self, hospital_id: str, hospital_name: str, 
                           historical_data: List[Dict]) -> Optional[Alert]:
        """Verifica alertas de tendência"""
        if len(historical_data) < 14:
            return None
        
        # Calcular tendência dos últimos 7 dias vs anteriores
        recent_data = historical_data[-7:]
        previous_data = historical_data[-14:-7]
        
        recent_avg = np.mean([d.get('occupancy_rate', 0) for d in recent_data]) * 100
        previous_avg = np.mean([d.get('occupancy_rate', 0) for d in previous_data]) * 100
        
        if previous_avg > 0:
            trend_percentage = ((recent_avg - previous_avg) / previous_avg) * 100
            
            if trend_percentage >= self.alert_rules[AlertType.TREND_INCREASING]['threshold']:
                rule = self.alert_rules[AlertType.TREND_INCREASING]
                message = rule['message_template'].format(value=round(trend_percentage, 1))
                
                return Alert(
                    id=f"alert_{self.next_alert_id}",
                    hospital_id=hospital_id,
                    hospital_name=hospital_name,
                    alert_type=AlertType.TREND_INCREASING,
                    level=rule['level'],
                    title=rule['title'],
                    message=message,
                    timestamp=datetime.now().isoformat(),
                    value=trend_percentage,
                    threshold=rule['threshold'],
                    unit=rule['unit'],
                    is_active=True,
                    acknowledged=False,
                    acknowledged_by=None,
                    acknowledged_at=None,
                    resolved=False,
                    resolved_at=None,
                    metadata={
                        'recent_avg': recent_avg,
                        'previous_avg': previous_avg,
                        'trend_percentage': trend_percentage
                    }
                )
        
        return None
    
    def get_active_alerts(self, hospital_id: Optional[str] = None, 
                         level: Optional[AlertLevel] = None) -> List[Alert]:
        """Retorna alertas ativos com filtros opcionais"""
        filtered_alerts = [alert for alert in self.alerts if alert.is_active and not alert.resolved]
        
        if hospital_id:
            filtered_alerts = [alert for alert in filtered_alerts if alert.hospital_id == hospital_id]
        
        if level:
            filtered_alerts = [alert for alert in filtered_alerts if alert.level == level]
        
        # Ordenar por timestamp (mais recentes primeiro)
        filtered_alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered_alerts
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Reconhece um alerta"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now().isoformat()
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve um alerta"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now().isoformat()
                alert.is_active = False
                return True
        return False
    
    def get_alert_statistics(self, hospital_id: Optional[str] = None, 
                           days: int = 7) -> Dict:
        """Retorna estatísticas de alertas"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()
        
        filtered_alerts = [
            alert for alert in self.alerts 
            if alert.timestamp >= cutoff_str
        ]
        
        if hospital_id:
            filtered_alerts = [alert for alert in filtered_alerts if alert.hospital_id == hospital_id]
        
        # Contar por nível
        level_counts = {}
        for level in AlertLevel:
            level_counts[level.value] = len([
                alert for alert in filtered_alerts if alert.level == level
            ])
        
        # Contar por tipo
        type_counts = {}
        for alert_type in AlertType:
            type_counts[alert_type.value] = len([
                alert for alert in filtered_alerts if alert.alert_type == alert_type
            ])
        
        # Contar por status
        active_count = len([alert for alert in filtered_alerts if alert.is_active and not alert.resolved])
        acknowledged_count = len([alert for alert in filtered_alerts if alert.acknowledged])
        resolved_count = len([alert for alert in filtered_alerts if alert.resolved])
        
        return {
            "period_days": days,
            "total_alerts": len(filtered_alerts),
            "active_alerts": active_count,
            "acknowledged_alerts": acknowledged_count,
            "resolved_alerts": resolved_count,
            "by_level": level_counts,
            "by_type": type_counts,
            "hospital_id": hospital_id
        }
    
    def get_hospital_alert_summary(self, hospital_id: str) -> Dict:
        """Retorna resumo de alertas de um hospital"""
        hospital_alerts = [alert for alert in self.alerts if alert.hospital_id == hospital_id]
        
        if not hospital_alerts:
            return {
                "hospital_id": hospital_id,
                "total_alerts": 0,
                "active_alerts": 0,
                "critical_alerts": 0,
                "high_alerts": 0,
                "medium_alerts": 0,
                "low_alerts": 0,
                "latest_alert": None
            }
        
        active_alerts = [alert for alert in hospital_alerts if alert.is_active and not alert.resolved]
        critical_alerts = [alert for alert in active_alerts if alert.level == AlertLevel.CRITICAL]
        high_alerts = [alert for alert in active_alerts if alert.level == AlertLevel.HIGH]
        medium_alerts = [alert for alert in active_alerts if alert.level == AlertLevel.MEDIUM]
        low_alerts = [alert for alert in active_alerts if alert.level == AlertLevel.LOW]
        
        # Pegar o alerta mais recente
        latest_alert = max(hospital_alerts, key=lambda x: x.timestamp) if hospital_alerts else None
        
        return {
            "hospital_id": hospital_id,
            "hospital_name": hospital_alerts[0].hospital_name if hospital_alerts else "",
            "total_alerts": len(hospital_alerts),
            "active_alerts": len(active_alerts),
            "critical_alerts": len(critical_alerts),
            "high_alerts": len(high_alerts),
            "medium_alerts": len(medium_alerts),
            "low_alerts": len(low_alerts),
            "latest_alert": {
                "id": latest_alert.id,
                "title": latest_alert.title,
                "level": latest_alert.level.value,
                "timestamp": latest_alert.timestamp
            } if latest_alert else None
        }
    
    def update_alert_rules(self, new_rules: Dict) -> bool:
        """Atualiza regras de alerta"""
        try:
            for alert_type_str, rule in new_rules.items():
                alert_type = AlertType(alert_type_str)
                self.alert_rules[alert_type].update(rule)
            return True
        except Exception:
            return False

# Instância global do serviço
alerts_service = AlertsService()
