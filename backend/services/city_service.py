import requests
import json
from typing import List, Dict, Optional
import pandas as pd

class CityService:
    """Serviço para buscar dados de cidades brasileiras"""
    
    def __init__(self):
        self.ibge_base_url = "https://servicodados.ibge.gov.br/api/v1"
        self.openweather_api_key = None  # Pode ser configurado via env
    
    def search_cities(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Busca cidades brasileiras por nome usando API do IBGE
        """
        try:
            print(f"🔍 Buscando cidades com query: '{query}'")
            
            # Lista de cidades brasileiras principais para teste
            major_cities = [
                {"id": "4209102", "nome": "Joinville", "uf": "SC", "estado": "Santa Catarina", "regiao": "Sul", "latitude": -26.3044, "longitude": -48.8464},
                {"id": "3550308", "nome": "São Paulo", "uf": "SP", "estado": "São Paulo", "regiao": "Sudeste", "latitude": -23.5505, "longitude": -46.6333},
                {"id": "3304557", "nome": "Rio de Janeiro", "uf": "RJ", "estado": "Rio de Janeiro", "regiao": "Sudeste", "latitude": -22.9068, "longitude": -43.1729},
                {"id": "2927408", "nome": "Salvador", "uf": "BA", "estado": "Bahia", "regiao": "Nordeste", "latitude": -12.9777, "longitude": -38.5016},
                {"id": "2304400", "nome": "Fortaleza", "uf": "CE", "estado": "Ceará", "regiao": "Nordeste", "latitude": -3.7172, "longitude": -38.5434},
                {"id": "1302603", "nome": "Manaus", "uf": "AM", "estado": "Amazonas", "regiao": "Norte", "latitude": -3.1190, "longitude": -60.0217},
                {"id": "4314902", "nome": "Porto Alegre", "uf": "RS", "estado": "Rio Grande do Sul", "regiao": "Sul", "latitude": -30.0346, "longitude": -51.2177},
                {"id": "4106902", "nome": "Curitiba", "uf": "PR", "estado": "Paraná", "regiao": "Sul", "latitude": -25.4244, "longitude": -49.2654},
                {"id": "5208707", "nome": "Goiânia", "uf": "GO", "estado": "Goiás", "regiao": "Centro-Oeste", "latitude": -16.6864, "longitude": -49.2643},
                {"id": "2611606", "nome": "Recife", "uf": "PE", "estado": "Pernambuco", "regiao": "Nordeste", "latitude": -8.0476, "longitude": -34.8770},
                {"id": "1501402", "nome": "Belém", "uf": "PA", "estado": "Pará", "regiao": "Norte", "latitude": -1.4558, "longitude": -48.5044},
                {"id": "2111300", "nome": "São Luís", "uf": "MA", "estado": "Maranhão", "regiao": "Nordeste", "latitude": -2.5387, "longitude": -44.2825},
                {"id": "2704302", "nome": "Maceió", "uf": "AL", "estado": "Alagoas", "regiao": "Nordeste", "latitude": -9.5713, "longitude": -35.7813},
                {"id": "2507507", "nome": "João Pessoa", "uf": "PB", "estado": "Paraíba", "regiao": "Nordeste", "latitude": -7.1195, "longitude": -34.8450},
                {"id": "2408102", "nome": "Natal", "uf": "RN", "estado": "Rio Grande do Norte", "regiao": "Nordeste", "latitude": -5.7945, "longitude": -35.2110},
                {"id": "2800308", "nome": "Aracaju", "uf": "SE", "estado": "Sergipe", "regiao": "Nordeste", "latitude": -10.9472, "longitude": -37.0731},
                {"id": "3205309", "nome": "Vitória", "uf": "ES", "estado": "Espírito Santo", "regiao": "Sudeste", "latitude": -20.3155, "longitude": -40.3128},
                {"id": "5002704", "nome": "Campo Grande", "uf": "MS", "estado": "Mato Grosso do Sul", "regiao": "Centro-Oeste", "latitude": -20.4697, "longitude": -54.6201},
                {"id": "5103403", "nome": "Cuiabá", "uf": "MT", "estado": "Mato Grosso", "regiao": "Centro-Oeste", "latitude": -15.6014, "longitude": -56.0979},
                {"id": "1100205", "nome": "Porto Velho", "uf": "RO", "estado": "Rondônia", "regiao": "Norte", "latitude": -8.7612, "longitude": -63.9020},
                {"id": "1400100", "nome": "Boa Vista", "uf": "RR", "estado": "Roraima", "regiao": "Norte", "latitude": 2.8235, "longitude": -60.6758},
                {"id": "1200401", "nome": "Rio Branco", "uf": "AC", "estado": "Acre", "regiao": "Norte", "latitude": -9.9754, "longitude": -67.8243},
                {"id": "1600303", "nome": "Macapá", "uf": "AP", "estado": "Amapá", "regiao": "Norte", "latitude": 0.0389, "longitude": -51.0664},
                {"id": "1721000", "nome": "Palmas", "uf": "TO", "estado": "Tocantins", "regiao": "Norte", "latitude": -10.1689, "longitude": -48.3317},
                {"id": "5300108", "nome": "Brasília", "uf": "DF", "estado": "Distrito Federal", "regiao": "Centro-Oeste", "latitude": -15.7801, "longitude": -47.9292}
            ]
            
            # Filtrar por query
            filtered_cities = []
            query_lower = query.lower()
            
            for city in major_cities:
                if query_lower in city['nome'].lower():
                    filtered_cities.append({
                        'id': city['id'],
                        'nome': city['nome'],
                        'uf': city['uf'],
                        'estado': city['estado'],
                        'regiao': city['regiao']
                    })
                    
                    if len(filtered_cities) >= limit:
                        break
            
            print(f"✅ Encontradas {len(filtered_cities)} cidades")
            return filtered_cities
            
        except Exception as e:
            print(f"❌ Erro ao buscar cidades: {e}")
            return []
    
    def get_city_coordinates(self, city_id: str) -> Optional[Dict]:
        """
        Busca coordenadas de uma cidade específica
        """
        try:
            # Lista de cidades com coordenadas
            major_cities = [
                {"id": "4209102", "nome": "Joinville", "uf": "SC", "estado": "Santa Catarina", "regiao": "Sul", "latitude": -26.3044, "longitude": -48.8464},
                {"id": "3550308", "nome": "São Paulo", "uf": "SP", "estado": "São Paulo", "regiao": "Sudeste", "latitude": -23.5505, "longitude": -46.6333},
                {"id": "3304557", "nome": "Rio de Janeiro", "uf": "RJ", "estado": "Rio de Janeiro", "regiao": "Sudeste", "latitude": -22.9068, "longitude": -43.1729},
                {"id": "2927408", "nome": "Salvador", "uf": "BA", "estado": "Bahia", "regiao": "Nordeste", "latitude": -12.9777, "longitude": -38.5016},
                {"id": "2304400", "nome": "Fortaleza", "uf": "CE", "estado": "Ceará", "regiao": "Nordeste", "latitude": -3.7172, "longitude": -38.5434},
                {"id": "1302603", "nome": "Manaus", "uf": "AM", "estado": "Amazonas", "regiao": "Norte", "latitude": -3.1190, "longitude": -60.0217},
                {"id": "4314902", "nome": "Porto Alegre", "uf": "RS", "estado": "Rio Grande do Sul", "regiao": "Sul", "latitude": -30.0346, "longitude": -51.2177},
                {"id": "4106902", "nome": "Curitiba", "uf": "PR", "estado": "Paraná", "regiao": "Sul", "latitude": -25.4244, "longitude": -49.2654},
                {"id": "5208707", "nome": "Goiânia", "uf": "GO", "estado": "Goiás", "regiao": "Centro-Oeste", "latitude": -16.6864, "longitude": -49.2643},
                {"id": "2611606", "nome": "Recife", "uf": "PE", "estado": "Pernambuco", "regiao": "Nordeste", "latitude": -8.0476, "longitude": -34.8770},
                {"id": "1501402", "nome": "Belém", "uf": "PA", "estado": "Pará", "regiao": "Norte", "latitude": -1.4558, "longitude": -48.5044},
                {"id": "2111300", "nome": "São Luís", "uf": "MA", "estado": "Maranhão", "regiao": "Nordeste", "latitude": -2.5387, "longitude": -44.2825},
                {"id": "2704302", "nome": "Maceió", "uf": "AL", "estado": "Alagoas", "regiao": "Nordeste", "latitude": -9.5713, "longitude": -35.7813},
                {"id": "2507507", "nome": "João Pessoa", "uf": "PB", "estado": "Paraíba", "regiao": "Nordeste", "latitude": -7.1195, "longitude": -34.8450},
                {"id": "2408102", "nome": "Natal", "uf": "RN", "estado": "Rio Grande do Norte", "regiao": "Nordeste", "latitude": -5.7945, "longitude": -35.2110},
                {"id": "2800308", "nome": "Aracaju", "uf": "SE", "estado": "Sergipe", "regiao": "Nordeste", "latitude": -10.9472, "longitude": -37.0731},
                {"id": "3205309", "nome": "Vitória", "uf": "ES", "estado": "Espírito Santo", "regiao": "Sudeste", "latitude": -20.3155, "longitude": -40.3128},
                {"id": "5002704", "nome": "Campo Grande", "uf": "MS", "estado": "Mato Grosso do Sul", "regiao": "Centro-Oeste", "latitude": -20.4697, "longitude": -54.6201},
                {"id": "5103403", "nome": "Cuiabá", "uf": "MT", "estado": "Mato Grosso", "regiao": "Centro-Oeste", "latitude": -15.6014, "longitude": -56.0979},
                {"id": "1100205", "nome": "Porto Velho", "uf": "RO", "estado": "Rondônia", "regiao": "Norte", "latitude": -8.7612, "longitude": -63.9020},
                {"id": "1400100", "nome": "Boa Vista", "uf": "RR", "estado": "Roraima", "regiao": "Norte", "latitude": 2.8235, "longitude": -60.6758},
                {"id": "1200401", "nome": "Rio Branco", "uf": "AC", "estado": "Acre", "regiao": "Norte", "latitude": -9.9754, "longitude": -67.8243},
                {"id": "1600303", "nome": "Macapá", "uf": "AP", "estado": "Amapá", "regiao": "Norte", "latitude": 0.0389, "longitude": -51.0664},
                {"id": "1721000", "nome": "Palmas", "uf": "TO", "estado": "Tocantins", "regiao": "Norte", "latitude": -10.1689, "longitude": -48.3317},
                {"id": "5300108", "nome": "Brasília", "uf": "DF", "estado": "Distrito Federal", "regiao": "Centro-Oeste", "latitude": -15.7801, "longitude": -47.9292}
            ]
            
            # Buscar cidade por ID
            for city in major_cities:
                if city['id'] == city_id:
                    return {
                        'latitude': city['latitude'],
                        'longitude': city['longitude']
                    }
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar coordenadas da cidade {city_id}: {e}")
            return None
    
    def get_city_info(self, city_id: str) -> Optional[Dict]:
        """
        Busca informações completas de uma cidade
        """
        try:
            url = f"{self.ibge_base_url}/localidades/municipios/{city_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            city_data = response.json()
            
            return {
                'id': city_data['id'],
                'nome': city_data['nome'],
                'uf': city_data['microrregiao']['mesorregiao']['UF']['sigla'],
                'estado': city_data['microrregiao']['mesorregiao']['UF']['nome'],
                'regiao': city_data['microrregiao']['mesorregiao']['UF']['regiao']['nome'],
                'latitude': city_data['centroide']['latitude'],
                'longitude': city_data['centroide']['longitude']
            }
            
        except Exception as e:
            print(f"Erro ao buscar informações da cidade {city_id}: {e}")
            return None

# Instância global do serviço
city_service = CityService()
