from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict
from services.hybrid_hospital_service import hybrid_hospital_service
from services.real_data_service import real_data_service
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/real-data", tags=["real-data"])

@router.get("/hospitals")
def get_real_hospitals(
    uf: Optional[str] = Query(None, description="Filtrar por UF"),
    municipio: Optional[str] = Query(None, description="Filtrar por município"),
    use_real_data: bool = Query(True, description="Usar dados reais ou simulados")
):
    """Lista hospitais com dados reais do CNES"""
    try:
        # Configurar se deve usar dados reais
        hybrid_hospital_service.use_real_data = use_real_data
        
        hospitals = hybrid_hospital_service.get_hospitals(
            city=municipio, 
            state=uf
        )
        
        return {
            "status": "ok",
            "data_source": "real" if use_real_data else "simulated",
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
                    "is_public": h.is_public,
                    "data_source": "real" if h.id.startswith('real_') else "simulated"
                }
                for h in hospitals
            ]
        }
    except Exception as exc:
        logger.error(f"Erro ao buscar hospitais reais: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/hospitals/{hospital_id}/enhanced-kpis")
def get_enhanced_hospital_kpis(
    hospital_id: str,
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    """Retorna KPIs enriquecidos com dados externos"""
    try:
        kpis = hybrid_hospital_service.get_enhanced_hospital_kpis(
            hospital_id, start_date, end_date
        )
        
        if not kpis:
            raise HTTPException(status_code=404, detail="Hospital não encontrado ou dados indisponíveis")
        
        return {
            "status": "ok",
            **kpis
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao buscar KPIs enriquecidos: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/weather/{latitude}/{longitude}")
def get_weather_data(
    latitude: float,
    longitude: float,
    date: str = Query(None, description="Data específica (YYYY-MM-DD)")
):
    """Busca dados meteorológicos para coordenadas específicas"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        weather_data = real_data_service.get_weather_data(latitude, longitude, date)
        
        return {
            "status": "ok",
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "date": date,
            "weather": weather_data
        }
    except Exception as exc:
        logger.error(f"Erro ao buscar dados meteorológicos: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/covid/{uf}")
def get_covid_data(
    uf: str,
    background_tasks: BackgroundTasks = None
):
    """Busca dados de COVID-19 por UF"""
    try:
        covid_data = real_data_service.get_covid_data(uf)
        
        # Atualizar cache em background
        if background_tasks:
            background_tasks.add_task(
                real_data_service._make_request,
                f"https://brasilapi.com.br/api/covid19/v1",
                {"uf": uf}
            )
        
        return {
            "status": "ok",
            "uf": uf,
            "covid_data": covid_data
        }
    except Exception as exc:
        logger.error(f"Erro ao buscar dados de COVID-19: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/holidays/{year}")
def get_holidays_data(
    year: int,
    uf: Optional[str] = Query(None, description="Filtrar por UF")
):
    """Busca dados de feriados por ano"""
    try:
        holidays = real_data_service.get_holiday_data(uf or "BR", year)
        
        return {
            "status": "ok",
            "year": year,
            "uf": uf or "BR",
            "holidays": holidays
        }
    except Exception as exc:
        logger.error(f"Erro ao buscar dados de feriados: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/region/{region}/enhanced-summary")
def get_enhanced_regional_summary(
    region: str,
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    """Retorna resumo regional enriquecido com dados externos"""
    try:
        summary = hybrid_hospital_service.get_regional_summary_with_real_data(
            region, start_date, end_date
        )
        
        if not summary:
            raise HTTPException(status_code=404, detail="Região não encontrada ou dados indisponíveis")
        
        return {
            "status": "ok",
            **summary
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao buscar resumo regional enriquecido: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/data-sources/status")
def get_data_sources_status():
    """Verifica status das APIs de dados externos"""
    try:
        status = {
            "cnes_api": False,
            "sih_api": False,
            "weather_api": False,
            "brasil_api": False,
            "overall_status": "unknown"
        }
        
        # Testar CNES
        try:
            test_data = real_data_service._make_request(
                "https://cnes.datasus.gov.br/services/estabelecimentos",
                {"limit": 1}
            )
            status["cnes_api"] = test_data is not None
        except:
            status["cnes_api"] = False
        
        # Testar SIH
        try:
            test_data = real_data_service._make_request(
                "https://sih.datasus.gov.br/services/ocupacao",
                {"limit": 1}
            )
            status["sih_api"] = test_data is not None
        except:
            status["sih_api"] = False
        
        # Testar BrasilAPI
        try:
            test_data = real_data_service._make_request(
                "https://brasilapi.com.br/api/feriados/v1/2024"
            )
            status["brasil_api"] = test_data is not None
        except:
            status["brasil_api"] = False
        
        # Testar OpenWeatherMap
        try:
            test_data = real_data_service._make_request(
                "https://api.openweathermap.org/data/2.5/weather",
                {"lat": -26.3044, "lon": -48.8456, "appid": "test"}
            )
            status["weather_api"] = True  # API existe, mas precisa de chave válida
        except:
            status["weather_api"] = False
        
        # Determinar status geral
        available_apis = sum(status.values())
        if available_apis >= 3:
            status["overall_status"] = "excellent"
        elif available_apis >= 2:
            status["overall_status"] = "good"
        elif available_apis >= 1:
            status["overall_status"] = "limited"
        else:
            status["overall_status"] = "offline"
        
        return {
            "status": "ok",
            "data_sources": status,
            "recommendation": {
                "excellent": "Todas as APIs estão funcionando. Dados reais disponíveis.",
                "good": "Maioria das APIs funcionando. Alguns dados podem ser simulados.",
                "limited": "Poucas APIs funcionando. Principalmente dados simulados.",
                "offline": "APIs externas indisponíveis. Usando apenas dados simulados."
            }[status["overall_status"]]
        }
        
    except Exception as exc:
        logger.error(f"Erro ao verificar status das APIs: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/config/use-real-data")
def toggle_real_data_usage(
    use_real_data: bool = Query(..., description="Usar dados reais ou simulados")
):
    """Alterna entre uso de dados reais e simulados"""
    try:
        hybrid_hospital_service.use_real_data = use_real_data
        
        return {
            "status": "ok",
            "message": f"Dados {'reais' if use_real_data else 'simulados'} ativados",
            "use_real_data": use_real_data
        }
    except Exception as exc:
        logger.error(f"Erro ao alterar configuração: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/cache/clear")
def clear_cache():
    """Limpa cache de dados externos"""
    try:
        real_data_service.cache.clear()
        hybrid_hospital_service.real_hospitals_cache.clear()
        hybrid_hospital_service.last_cache_update = None
        
        return {
            "status": "ok",
            "message": "Cache limpo com sucesso"
        }
    except Exception as exc:
        logger.error(f"Erro ao limpar cache: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
