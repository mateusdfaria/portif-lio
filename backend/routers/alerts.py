from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from services.alerts_service import alerts_service, AlertLevel, AlertType
from services.hospital_service import hospital_service
from datetime import datetime, timedelta

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/")
def get_alerts(
    hospital_id: Optional[str] = Query(None, description="Filtrar por hospital"),
    level: Optional[str] = Query(None, description="Filtrar por nível (low, medium, high, critical)"),
    active_only: bool = Query(True, description="Mostrar apenas alertas ativos")
):
    """Lista alertas com filtros opcionais"""
    try:
        alert_level = None
        if level:
            try:
                alert_level = AlertLevel(level)
            except ValueError:
                raise HTTPException(status_code=400, detail="Nível de alerta inválido")
        
        alerts = alerts_service.get_active_alerts(hospital_id, alert_level)
        
        if not active_only:
            # Incluir todos os alertas se não for apenas ativos
            all_alerts = alerts_service.alerts
            if hospital_id:
                all_alerts = [alert for alert in all_alerts if alert.hospital_id == hospital_id]
            if alert_level:
                all_alerts = [alert for alert in all_alerts if alert.level == alert_level]
            alerts = all_alerts
        
        return {
            "status": "ok",
            "count": len(alerts),
            "alerts": [
                {
                    "id": alert.id,
                    "hospital_id": alert.hospital_id,
                    "hospital_name": alert.hospital_name,
                    "alert_type": alert.alert_type.value,
                    "level": alert.level.value,
                    "title": alert.title,
                    "message": alert.message,
                    "timestamp": alert.timestamp,
                    "value": alert.value,
                    "threshold": alert.threshold,
                    "unit": alert.unit,
                    "is_active": alert.is_active,
                    "acknowledged": alert.acknowledged,
                    "acknowledged_by": alert.acknowledged_by,
                    "acknowledged_at": alert.acknowledged_at,
                    "resolved": alert.resolved,
                    "resolved_at": alert.resolved_at,
                    "metadata": alert.metadata
                }
                for alert in alerts
            ]
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/statistics")
def get_alert_statistics(
    hospital_id: Optional[str] = Query(None, description="Filtrar por hospital"),
    days: int = Query(7, description="Período em dias")
):
    """Retorna estatísticas de alertas"""
    try:
        stats = alerts_service.get_alert_statistics(hospital_id, days)
        return {
            "status": "ok",
            **stats
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/hospital/{hospital_id}/summary")
def get_hospital_alert_summary(hospital_id: str):
    """Retorna resumo de alertas de um hospital"""
    try:
        summary = alerts_service.get_hospital_alert_summary(hospital_id)
        return {
            "status": "ok",
            **summary
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str = Query(..., description="Usuário que reconheceu o alerta")
):
    """Reconhece um alerta"""
    try:
        success = alerts_service.acknowledge_alert(alert_id, acknowledged_by)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
        
        return {
            "status": "ok",
            "message": "Alerta reconhecido com sucesso",
            "alert_id": alert_id,
            "acknowledged_by": acknowledged_by,
            "acknowledged_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: str):
    """Resolve um alerta"""
    try:
        success = alerts_service.resolve_alert(alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
        
        return {
            "status": "ok",
            "message": "Alerta resolvido com sucesso",
            "alert_id": alert_id,
            "resolved_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/check/{hospital_id}")
def check_hospital_alerts(
    hospital_id: str,
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    """Verifica alertas para um hospital baseado nas métricas"""
    try:
        # Verificar se o hospital existe
        hospital = hospital_service.get_hospital_by_id(hospital_id)
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital não encontrado")
        
        # Obter KPIs do hospital
        kpis = hospital_service.get_hospital_kpis(hospital_id, start_date, end_date)
        if not kpis:
            raise HTTPException(status_code=400, detail="Dados do hospital indisponíveis")
        
        # Obter métricas históricas
        metrics = hospital_service.generate_hospital_metrics(hospital_id, start_date, end_date)
        
        # Preparar dados para verificação de alertas
        current_metrics = {
            'occupancy_rate': kpis['kpis']['avg_occupancy_rate'] / 100,
            'emergency_occupancy': kpis['kpis']['avg_emergency_occupancy'] / 100,
            'icu_occupancy': kpis['kpis']['avg_icu_occupancy'] / 100,
            'avg_wait_time': kpis['kpis']['avg_wait_time']
        }
        
        historical_data = [
            {
                'occupancy_rate': m.occupancy_rate,
                'emergency_occupancy': m.emergency_occupancy,
                'icu_occupancy': m.icu_occupancy,
                'avg_wait_time': m.avg_wait_time
            }
            for m in metrics
        ]
        
        # Verificar alertas
        new_alerts = alerts_service.check_hospital_alerts(
            hospital_id, hospital.name, current_metrics, historical_data
        )
        
        return {
            "status": "ok",
            "hospital_id": hospital_id,
            "hospital_name": hospital.name,
            "period": f"{start_date} a {end_date}",
            "new_alerts_count": len(new_alerts),
            "new_alerts": [
                {
                    "id": alert.id,
                    "alert_type": alert.alert_type.value,
                    "level": alert.level.value,
                    "title": alert.title,
                    "message": alert.message,
                    "value": alert.value,
                    "threshold": alert.threshold,
                    "unit": alert.unit,
                    "timestamp": alert.timestamp
                }
                for alert in new_alerts
            ]
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/rules")
def get_alert_rules():
    """Retorna regras de alerta configuradas"""
    try:
        rules = {}
        for alert_type, rule in alerts_service.alert_rules.items():
            rules[alert_type.value] = {
                "threshold": rule["threshold"],
                "unit": rule["unit"],
                "level": rule["level"].value,
                "title": rule["title"],
                "message_template": rule["message_template"]
            }
        
        return {
            "status": "ok",
            "rules": rules
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.put("/rules")
def update_alert_rules(new_rules: dict):
    """Atualiza regras de alerta"""
    try:
        success = alerts_service.update_alert_rules(new_rules)
        
        if not success:
            raise HTTPException(status_code=400, detail="Erro ao atualizar regras")
        
        return {
            "status": "ok",
            "message": "Regras de alerta atualizadas com sucesso",
            "updated_rules": len(new_rules)
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/dashboard")
def get_alerts_dashboard():
    """Retorna dados para dashboard de alertas"""
    try:
        # Estatísticas gerais
        stats = alerts_service.get_alert_statistics()
        
        # Alertas ativos por hospital
        hospitals = hospital_service.get_hospitals()
        hospital_summaries = []
        
        for hospital in hospitals:
            summary = alerts_service.get_hospital_alert_summary(hospital.id)
            hospital_summaries.append(summary)
        
        # Alertas críticos e altos
        critical_alerts = alerts_service.get_active_alerts(level=AlertLevel.CRITICAL)
        high_alerts = alerts_service.get_active_alerts(level=AlertLevel.HIGH)
        
        return {
            "status": "ok",
            "statistics": stats,
            "hospital_summaries": hospital_summaries,
            "critical_alerts": [
                {
                    "id": alert.id,
                    "hospital_name": alert.hospital_name,
                    "title": alert.title,
                    "message": alert.message,
                    "timestamp": alert.timestamp,
                    "value": alert.value,
                    "unit": alert.unit
                }
                for alert in critical_alerts
            ],
            "high_alerts": [
                {
                    "id": alert.id,
                    "hospital_name": alert.hospital_name,
                    "title": alert.title,
                    "message": alert.message,
                    "timestamp": alert.timestamp,
                    "value": alert.value,
                    "unit": alert.unit
                }
                for alert in high_alerts
            ]
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
