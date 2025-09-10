from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from services.joinville_sus_service import joinville_sus_service
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/joinville-sus", tags=["joinville-sus"])

@router.get("/hospitals")
def get_joinville_hospitals():
    """Retorna todos os hospitais públicos de Joinville"""
    try:
        hospitals = joinville_sus_service.get_all_hospitals()
        
        return {
            "status": "ok",
            "municipio": "Joinville",
            "uf": "SC",
            "count": len(hospitals),
            "hospitals": [
                {
                    "cnes": h.cnes,
                    "nome": h.nome,
                    "endereco": h.endereco,
                    "telefone": h.telefone,
                    "tipo_gestao": h.tipo_gestao,
                    "capacidade_total": h.capacidade_total,
                    "capacidade_uti": h.capacidade_uti,
                    "capacidade_emergencia": h.capacidade_emergencia,
                    "especialidades": h.especialidades,
                    "latitude": h.latitude,
                    "longitude": h.longitude,
                    "municipio": h.municipio,
                    "uf": h.uf
                }
                for h in hospitals
            ]
        }
    except Exception as exc:
        logger.error(f"Erro ao buscar hospitais de Joinville: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/hospitals/{cnes}")
def get_hospital_info(cnes: str):
    """Retorna informações de um hospital específico"""
    try:
        hospital = joinville_sus_service.get_hospital_by_cnes(cnes)
        
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital não encontrado")
        
        return {
            "status": "ok",
            "hospital": {
                "cnes": hospital.cnes,
                "nome": hospital.nome,
                "endereco": hospital.endereco,
                "telefone": hospital.telefone,
                "tipo_gestao": hospital.tipo_gestao,
                "capacidade_total": hospital.capacidade_total,
                "capacidade_uti": hospital.capacidade_uti,
                "capacidade_emergencia": hospital.capacidade_emergencia,
                "especialidades": hospital.especialidades,
                "latitude": hospital.latitude,
                "longitude": hospital.longitude,
                "municipio": hospital.municipio,
                "uf": hospital.uf
            }
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao buscar informações do hospital: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/hospitals/{cnes}/sus-data")
def get_hospital_sus_data(
    cnes: str,
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    """Retorna dados SUS de um hospital específico"""
    try:
        data = joinville_sus_service.get_sus_data(cnes, start_date, end_date)
        
        if not data:
            raise HTTPException(status_code=404, detail="Dados SUS não disponíveis para o período")
        
        hospital = joinville_sus_service.get_hospital_by_cnes(cnes)
        hospital_name = hospital.nome if hospital else "Hospital Desconhecido"
        
        return {
            "status": "ok",
            "hospital_name": hospital_name,
            "cnes": cnes,
            "period": f"{start_date} a {end_date}",
            "count": len(data),
            "data": [
                {
                    "date": d.data,
                    "ocupacao_leitos": d.ocupacao_leitos,
                    "ocupacao_uti": d.ocupacao_uti,
                    "ocupacao_emergencia": d.ocupacao_emergencia,
                    "pacientes_internados": d.pacientes_internados,
                    "pacientes_uti": d.pacientes_uti,
                    "pacientes_emergencia": d.pacientes_emergencia,
                    "admissoes_dia": d.admissoes_dia,
                    "altas_dia": d.altas_dia,
                    "procedimentos_realizados": d.procedimentos_realizados,
                    "tempo_espera_medio": d.tempo_espera_medio,
                    "taxa_ocupacao": d.taxa_ocupacao
                }
                for d in data
            ]
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao buscar dados SUS: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/hospitals/{cnes}/sus-kpis")
def get_hospital_sus_kpis(
    cnes: str,
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    """Retorna KPIs SUS de um hospital específico"""
    try:
        kpis = joinville_sus_service.get_sus_kpis(cnes, start_date, end_date)
        
        if not kpis:
            raise HTTPException(status_code=404, detail="KPIs SUS não disponíveis para o período")
        
        return {
            "status": "ok",
            **kpis
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao buscar KPIs SUS: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/summary")
def get_joinville_summary(
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    """Retorna resumo de todos os hospitais públicos de Joinville"""
    try:
        summary = joinville_sus_service.get_joinville_summary(start_date, end_date)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Resumo não disponível para o período")
        
        return {
            "status": "ok",
            **summary
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao gerar resumo: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/capacity")
def get_joinville_capacity():
    """Retorna informações de capacidade de todos os hospitais"""
    try:
        hospitals = joinville_sus_service.get_all_hospitals()
        
        total_capacity = sum(h.capacidade_total for h in hospitals)
        total_uti = sum(h.capacidade_uti for h in hospitals)
        total_emergency = sum(h.capacidade_emergencia for h in hospitals)
        
        return {
            "status": "ok",
            "municipio": "Joinville",
            "uf": "SC",
            "hospitals_count": len(hospitals),
            "total_capacity": {
                "total_leitos": total_capacity,
                "total_uti": total_uti,
                "total_emergencia": total_emergency
            },
            "hospitals": [
                {
                    "nome": h.nome,
                    "cnes": h.cnes,
                    "tipo_gestao": h.tipo_gestao,
                    "capacidade_total": h.capacidade_total,
                    "capacidade_uti": h.capacidade_uti,
                    "capacidade_emergencia": h.capacidade_emergencia,
                    "especialidades_count": len(h.especialidades)
                }
                for h in hospitals
            ]
        }
    except Exception as exc:
        logger.error(f"Erro ao buscar capacidade: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/specialties")
def get_joinville_specialties():
    """Retorna todas as especialidades disponíveis em Joinville"""
    try:
        hospitals = joinville_sus_service.get_all_hospitals()
        
        all_specialties = set()
        for hospital in hospitals:
            all_specialties.update(hospital.especialidades)
        
        specialties_by_hospital = {}
        for hospital in hospitals:
            specialties_by_hospital[hospital.nome] = hospital.especialidades
        
        return {
            "status": "ok",
            "municipio": "Joinville",
            "uf": "SC",
            "total_specialties": len(all_specialties),
            "all_specialties": sorted(list(all_specialties)),
            "specialties_by_hospital": specialties_by_hospital
        }
    except Exception as exc:
        logger.error(f"Erro ao buscar especialidades: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/alerts")
def get_joinville_alerts(
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    """Retorna alertas de todos os hospitais públicos de Joinville"""
    try:
        hospitals = joinville_sus_service.get_all_hospitals()
        all_alerts = []
        
        for hospital in hospitals:
            data = joinville_sus_service.get_sus_data(hospital.cnes, start_date, end_date)
            
            for d in data:
                # Alertas de ocupação
                if d.ocupacao_leitos > 0.9:
                    all_alerts.append({
                        "hospital": hospital.nome,
                        "cnes": hospital.cnes,
                        "date": d.data,
                        "type": "high_occupancy",
                        "level": "critical",
                        "message": f"Ocupação crítica: {d.ocupacao_leitos*100:.1f}%",
                        "value": d.ocupacao_leitos * 100,
                        "threshold": 90
                    })
                elif d.ocupacao_leitos > 0.8:
                    all_alerts.append({
                        "hospital": hospital.nome,
                        "cnes": hospital.cnes,
                        "date": d.data,
                        "type": "high_occupancy",
                        "level": "warning",
                        "message": f"Ocupação alta: {d.ocupacao_leitos*100:.1f}%",
                        "value": d.ocupacao_leitos * 100,
                        "threshold": 80
                    })
                
                # Alertas de UTI
                if d.ocupacao_uti > 0.95:
                    all_alerts.append({
                        "hospital": hospital.nome,
                        "cnes": hospital.cnes,
                        "date": d.data,
                        "type": "uti_full",
                        "level": "critical",
                        "message": f"UTI quase lotada: {d.ocupacao_uti*100:.1f}%",
                        "value": d.ocupacao_uti * 100,
                        "threshold": 95
                    })
                
                # Alertas de emergência
                if d.ocupacao_emergencia > 1.0:
                    all_alerts.append({
                        "hospital": hospital.nome,
                        "cnes": hospital.cnes,
                        "date": d.data,
                        "type": "emergency_overflow",
                        "level": "critical",
                        "message": f"Emergência superlotada: {d.ocupacao_emergencia*100:.1f}%",
                        "value": d.ocupacao_emergencia * 100,
                        "threshold": 100
                    })
                
                # Alertas de tempo de espera
                if d.tempo_espera_medio > 90:
                    all_alerts.append({
                        "hospital": hospital.nome,
                        "cnes": hospital.cnes,
                        "date": d.data,
                        "type": "long_wait_time",
                        "level": "warning",
                        "message": f"Tempo de espera alto: {d.tempo_espera_medio:.1f} min",
                        "value": d.tempo_espera_medio,
                        "threshold": 90
                    })
        
        # Ordenar alertas por data
        all_alerts.sort(key=lambda x: x['date'], reverse=True)
        
        return {
            "status": "ok",
            "municipio": "Joinville",
            "uf": "SC",
            "period": f"{start_date} a {end_date}",
            "total_alerts": len(all_alerts),
            "alerts_by_level": {
                "critical": len([a for a in all_alerts if a['level'] == 'critical']),
                "warning": len([a for a in all_alerts if a['level'] == 'warning'])
            },
            "alerts_by_hospital": {
                hospital.nome: len([a for a in all_alerts if a['hospital'] == hospital.nome])
                for hospital in hospitals
            },
            "alerts": all_alerts
        }
        
    except Exception as exc:
        logger.error(f"Erro ao gerar alertas: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
