from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from services.city_service import city_service

router = APIRouter(prefix="/cities", tags=["cities"])

@router.get("/search")
async def search_cities(
    q: str = Query(..., description="Termo de busca para o nome da cidade"),
    limit: int = Query(10, ge=1, le=50, description="Número máximo de resultados")
) -> List[Dict]:
    """
    Busca cidades brasileiras por nome
    """
    if len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Termo de busca deve ter pelo menos 2 caracteres")
    
    cities = city_service.search_cities(q.strip(), limit)
    return cities

@router.get("/{city_id}")
async def get_city_info(city_id: str) -> Dict:
    """
    Busca informações completas de uma cidade específica
    """
    city_info = city_service.get_city_info(city_id)
    
    if not city_info:
        raise HTTPException(status_code=404, detail="Cidade não encontrada")
    
    return city_info

@router.get("/{city_id}/coordinates")
async def get_city_coordinates(city_id: str) -> Dict:
    """
    Busca apenas as coordenadas de uma cidade
    """
    coordinates = city_service.get_city_coordinates(city_id)
    
    if not coordinates:
        raise HTTPException(status_code=404, detail="Coordenadas não encontradas para esta cidade")
    
    return coordinates

