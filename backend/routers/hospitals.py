from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from services.hospital_service import hospital_service

router = APIRouter(prefix="/hospitals", tags=["hospitals"])

@router.get("/")
def get_hospitals(
    city: Optional[str] = Query(None, description="Filtrar por cidade"),
    state: Optional[str] = Query(None, description="Filtrar por estado"),
    region: Optional[str] = Query(None, description="Filtrar por região"),
    is_public: Optional[bool] = Query(None, description="Filtrar por tipo (público/privado)")
):
    """Lista hospitais com filtros opcionais"""
    try:
        hospitals = hospital_service.get_hospitals(city, state, region, is_public)
        
        return {
            "status": "ok",
            "count": len(hospitals),
            "hospitals": [
                {
                    "id": h.id,
                    "name": h.name,
                    "city": h.city,
                    "state": h.state,
                    "region": h.region,
                    "latitude": h.latitude,
                    "longitude": h.longitude,
                    "capacity": h.capacity,
                    "specialties": h.specialties,
                    "emergency_capacity": h.emergency_capacity,
                    "icu_capacity": h.icu_capacity,
                    "is_public": h.is_public
                }
                for h in hospitals
            ]
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/search")
def search_hospitals(
    q: str = Query(..., description="Termo de busca"),
    limit: int = Query(10, description="Limite de resultados")
):
    """Busca hospitais por nome ou cidade"""
    try:
        hospitals = hospital_service.search_hospitals(q, limit)
        
        return {
            "status": "ok",
            "query": q,
            "count": len(hospitals),
            "hospitals": [
                {
                    "id": h.id,
                    "name": h.name,
                    "city": h.city,
                    "state": h.state,
                    "region": h.region,
                    "latitude": h.latitude,
                    "longitude": h.longitude,
                    "capacity": h.capacity,
                    "specialties": h.specialties,
                    "emergency_capacity": h.emergency_capacity,
                    "icu_capacity": h.icu_capacity,
                    "is_public": h.is_public
                }
                for h in hospitals
            ]
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/{hospital_id}")
def get_hospital(hospital_id: str):
    """Retorna detalhes de um hospital específico"""
    try:
        hospital = hospital_service.get_hospital_by_id(hospital_id)
        
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital não encontrado")
        
        return {
            "status": "ok",
            "hospital": {
                "id": hospital.id,
                "name": hospital.name,
                "city": hospital.city,
                "state": hospital.state,
                "region": hospital.region,
                "latitude": hospital.latitude,
                "longitude": hospital.longitude,
                "capacity": hospital.capacity,
                "specialties": hospital.specialties,
                "emergency_capacity": hospital.emergency_capacity,
                "icu_capacity": hospital.icu_capacity,
                "is_public": hospital.is_public,
                "created_at": hospital.created_at
            }
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/{hospital_id}/coordinates")
def get_hospital_coordinates(hospital_id: str):
    """Retorna coordenadas de um hospital"""
    try:
        coordinates = hospital_service.get_hospital_coordinates(hospital_id)
        
        if not coordinates:
            raise HTTPException(status_code=404, detail="Hospital não encontrado")
        
        return {
            "status": "ok",
            "hospital_id": hospital_id,
            "coordinates": coordinates
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/{hospital_id}/kpis")
def get_hospital_kpis(
    hospital_id: str,
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    """Retorna KPIs de um hospital para um período"""
    try:
        kpis = hospital_service.get_hospital_kpis(hospital_id, start_date, end_date)
        
        if not kpis:
            raise HTTPException(status_code=404, detail="Hospital não encontrado ou dados indisponíveis")
        
        return {
            "status": "ok",
            **kpis
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/{hospital_id}/metrics")
def get_hospital_metrics(
    hospital_id: str,
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    """Retorna métricas detalhadas de um hospital para um período"""
    try:
        metrics = hospital_service.generate_hospital_metrics(hospital_id, start_date, end_date)
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Hospital não encontrado ou dados indisponíveis")
        
        return {
            "status": "ok",
            "hospital_id": hospital_id,
            "period": f"{start_date} a {end_date}",
            "count": len(metrics),
            "metrics": [
                {
                    "date": m.date,
                    "occupancy_rate": m.occupancy_rate,
                    "emergency_occupancy": m.emergency_occupancy,
                    "icu_occupancy": m.icu_occupancy,
                    "avg_wait_time": m.avg_wait_time,
                    "total_patients": m.total_patients,
                    "emergency_patients": m.emergency_patients,
                    "icu_patients": m.icu_patients,
                    "discharges": m.discharges,
                    "admissions": m.admissions
                }
                for m in metrics
            ]
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/region/{region}/summary")
def get_regional_summary(
    region: str,
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    """Retorna resumo regional de hospitais"""
    try:
        summary = hospital_service.get_regional_summary(region, start_date, end_date)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Região não encontrada ou dados indisponíveis")
        
        return {
            "status": "ok",
            **summary
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
