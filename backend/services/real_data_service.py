import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from urllib.parse import urlencode

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RealHospitalData:
    """Dados reais de hospital"""
    cnes: str
    nome: str
    cidade: str
    uf: str
    latitude: float
    longitude: float
    tipo_unidade: str
    gestao: str
    capacidade_leitos: int
    leitos_uti: int
    leitos_emergencia: int
    especialidades: List[str]
    telefone: str
    endereco: str
    cep: str

@dataclass
class RealOccupancyData:
    """Dados reais de ocupação"""
    cnes: str
    data: str
    ocupacao_leitos: float
    ocupacao_uti: float
    ocupacao_emergencia: float
    pacientes_internados: int
    pacientes_uti: int
    pacientes_emergencia: int
    tempo_espera_medio: float
    admissoes_dia: int
    altas_dia: int

class RealDataService:
    """Serviço para integração com APIs de dados reais"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HospiCast/1.0 (Sistema de Previsão Hospitalar)',
            'Accept': 'application/json'
        })
        
        # Cache para evitar muitas requisições
        self.cache = {}
        self.cache_timeout = 3600  # 1 hora
        
    def _make_request(self, url: str, params: Dict = None, timeout: int = 30) -> Optional[Dict]:
        """Faz requisição HTTP com tratamento de erros"""
        try:
            cache_key = f"{url}_{json.dumps(params or {}, sort_keys=True)}"
            
            # Verificar cache
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.now().timestamp() - timestamp < self.cache_timeout:
                    return cached_data
            
            logger.info(f"Fazendo requisição para: {url}")
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Salvar no cache
            self.cache[cache_key] = (data, datetime.now().timestamp())
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON de {url}: {e}")
            return None

    def get_cnes_data(self, uf: str = None, municipio: str = None) -> List[RealHospitalData]:
        """Busca dados do CNES (Cadastro Nacional de Estabelecimentos de Saúde)"""
        try:
            # API do CNES via Datasus
            base_url = "https://cnes.datasus.gov.br/services/estabelecimentos"
            
            params = {
                'co_uf': uf,
                'co_municipio': municipio,
                'limit': 1000
            }
            
            # Remover parâmetros None
            params = {k: v for k, v in params.items() if v is not None}
            
            data = self._make_request(base_url, params)
            
            if not data:
                logger.warning("Não foi possível obter dados do CNES, usando dados simulados")
                return self._get_fallback_hospitals()
            
            hospitals = []
            for item in data.get('data', []):
                try:
                    hospital = RealHospitalData(
                        cnes=item.get('co_cnes', ''),
                        nome=item.get('no_fantasia', item.get('no_razao_social', 'Hospital')),
                        cidade=item.get('no_municipio', ''),
                        uf=item.get('co_uf', ''),
                        latitude=float(item.get('nu_latitude', 0)),
                        longitude=float(item.get('nu_longitude', 0)),
                        tipo_unidade=item.get('ds_tipo_unidade', ''),
                        gestao=item.get('ds_gestao', ''),
                        capacidade_leitos=int(item.get('qt_leitos_total', 0)),
                        leitos_uti=int(item.get('qt_leitos_uti', 0)),
                        leitos_emergencia=int(item.get('qt_leitos_emergencia', 0)),
                        especialidades=item.get('especialidades', []),
                        telefone=item.get('nu_telefone', ''),
                        endereco=item.get('ds_endereco', ''),
                        cep=item.get('co_cep', '')
                    )
                    hospitals.append(hospital)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Erro ao processar hospital {item.get('co_cnes', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Carregados {len(hospitals)} hospitais do CNES")
            return hospitals
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do CNES: {e}")
            return self._get_fallback_hospitals()

    def get_sih_data(self, cnes: str, start_date: str, end_date: str) -> List[RealOccupancyData]:
        """Busca dados do SIH (Sistema de Informações Hospitalares)"""
        try:
            # API do SIH via Datasus
            base_url = "https://sih.datasus.gov.br/services/ocupacao"
            
            params = {
                'co_cnes': cnes,
                'dt_inicio': start_date,
                'dt_fim': end_date
            }
            
            data = self._make_request(base_url, params)
            
            if not data:
                logger.warning(f"Não foi possível obter dados do SIH para CNES {cnes}")
                return self._generate_simulated_occupancy(cnes, start_date, end_date)
            
            occupancy_data = []
            for item in data.get('data', []):
                try:
                    occupancy = RealOccupancyData(
                        cnes=cnes,
                        data=item.get('dt_ocupacao', ''),
                        ocupacao_leitos=float(item.get('pc_ocupacao_leitos', 0)) / 100,
                        ocupacao_uti=float(item.get('pc_ocupacao_uti', 0)) / 100,
                        ocupacao_emergencia=float(item.get('pc_ocupacao_emergencia', 0)) / 100,
                        pacientes_internados=int(item.get('qt_pacientes_internados', 0)),
                        pacientes_uti=int(item.get('qt_pacientes_uti', 0)),
                        pacientes_emergencia=int(item.get('qt_pacientes_emergencia', 0)),
                        tempo_espera_medio=float(item.get('tempo_espera_medio', 0)),
                        admissoes_dia=int(item.get('qt_admissoes', 0)),
                        altas_dia=int(item.get('qt_altas', 0))
                    )
                    occupancy_data.append(occupancy)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Erro ao processar ocupação {item.get('dt_ocupacao', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Carregados {len(occupancy_data)} registros de ocupação do SIH")
            return occupancy_data
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do SIH: {e}")
            return self._generate_simulated_occupancy(cnes, start_date, end_date)

    def get_weather_data(self, latitude: float, longitude: float, date: str) -> Dict:
        """Busca dados meteorológicos da OpenWeatherMap"""
        try:
            # Usar API gratuita do OpenWeatherMap
            api_key = "your_openweather_api_key"  # Substituir por chave real
            base_url = "https://api.openweathermap.org/data/2.5/weather"
            
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': api_key,
                'units': 'metric',
                'lang': 'pt_br'
            }
            
            data = self._make_request(base_url, params)
            
            if not data:
                logger.warning("Não foi possível obter dados meteorológicos")
                return self._get_fallback_weather()
            
            return {
                'temperatura': data['main']['temp'],
                'temperatura_max': data['main']['temp_max'],
                'temperatura_min': data['main']['temp_min'],
                'umidade': data['main']['humidity'],
                'pressao': data['main']['pressure'],
                'velocidade_vento': data['wind']['speed'],
                'descricao': data['weather'][0]['description'],
                'icone': data['weather'][0]['icon']
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados meteorológicos: {e}")
            return self._get_fallback_weather()

    def get_holiday_data(self, uf: str, year: int) -> List[Dict]:
        """Busca dados de feriados via BrasilAPI"""
        try:
            base_url = f"https://brasilapi.com.br/api/feriados/v1/{year}"
            
            data = self._make_request(base_url)
            
            if not data:
                logger.warning("Não foi possível obter dados de feriados")
                return self._get_fallback_holidays(year)
            
            # Filtrar feriados nacionais e estaduais
            holidays = []
            for holiday in data:
                if holiday.get('type') in ['national', 'state']:
                    holidays.append({
                        'data': holiday['date'],
                        'nome': holiday['name'],
                        'tipo': holiday['type'],
                        'uf': holiday.get('state', 'BR')
                    })
            
            logger.info(f"Carregados {len(holidays)} feriados")
            return holidays
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados de feriados: {e}")
            return self._get_fallback_holidays(year)

    def get_covid_data(self, uf: str = None) -> Dict:
        """Busca dados de COVID-19 via BrasilAPI"""
        try:
            base_url = "https://brasilapi.com.br/api/covid19/v1"
            
            params = {}
            if uf:
                params['uf'] = uf
            
            data = self._make_request(base_url, params)
            
            if not data:
                logger.warning("Não foi possível obter dados de COVID-19")
                return self._get_fallback_covid_data()
            
            return {
                'casos_confirmados': data.get('confirmed', 0),
                'casos_recuperados': data.get('recovered', 0),
                'obitos': data.get('deaths', 0),
                'casos_ativos': data.get('active', 0),
                'taxa_letalidade': data.get('death_rate', 0),
                'taxa_recuperacao': data.get('recovery_rate', 0),
                'ultima_atualizacao': data.get('last_updated', '')
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados de COVID-19: {e}")
            return self._get_fallback_covid_data()

    def _get_fallback_hospitals(self) -> List[RealHospitalData]:
        """Dados de fallback quando APIs reais falham"""
        return [
            RealHospitalData(
                cnes="1234567",
                nome="Hospital Municipal São José - Joinville",
                cidade="Joinville",
                uf="SC",
                latitude=-26.3044,
                longitude=-48.8456,
                tipo_unidade="Hospital Geral",
                gestao="Municipal",
                capacidade_leitos=200,
                leitos_uti=20,
                leitos_emergencia=50,
                especialidades=["Emergência", "Cardiologia", "Neurologia"],
                telefone="(47) 3451-2000",
                endereco="Rua Dr. João Colin, 2700",
                cep="89201-000"
            ),
            RealHospitalData(
                cnes="2345678",
                nome="Hospital Universitário - Florianópolis",
                cidade="Florianópolis",
                uf="SC",
                latitude=-27.5954,
                longitude=-48.5480,
                tipo_unidade="Hospital Universitário",
                gestao="Estadual",
                capacidade_leitos=300,
                leitos_uti=30,
                leitos_emergencia=80,
                especialidades=["Emergência", "Cardiologia", "Neurologia", "Oncologia"],
                telefone="(48) 3721-9000",
                endereco="Rua Prof. Maria Flora Pausewang, 188",
                cep="88036-800"
            )
        ]

    def _generate_simulated_occupancy(self, cnes: str, start_date: str, end_date: str) -> List[RealOccupancyData]:
        """Gera dados simulados de ocupação quando API real falha"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        occupancy_data = []
        current_date = start
        
        while current_date <= end:
            # Simular dados realistas
            base_occupancy = np.random.normal(0.7, 0.15)
            base_occupancy = max(0.3, min(0.95, base_occupancy))
            
            occupancy = RealOccupancyData(
                cnes=cnes,
                data=current_date.strftime("%Y-%m-%d"),
                ocupacao_leitos=round(base_occupancy, 3),
                ocupacao_uti=round(base_occupancy * np.random.normal(0.9, 0.1), 3),
                ocupacao_emergencia=round(base_occupancy * np.random.normal(1.1, 0.1), 3),
                pacientes_internados=int(200 * base_occupancy),
                pacientes_uti=int(20 * base_occupancy * 0.9),
                pacientes_emergencia=int(50 * base_occupancy * 1.1),
                tempo_espera_medio=round(30 + (base_occupancy * 120), 1),
                admissoes_dia=int(40 * base_occupancy + np.random.randint(-5, 6)),
                altas_dia=int(40 * base_occupancy + np.random.randint(-5, 6))
            )
            
            occupancy_data.append(occupancy)
            current_date += timedelta(days=1)
        
        return occupancy_data

    def _get_fallback_weather(self) -> Dict:
        """Dados meteorológicos de fallback"""
        return {
            'temperatura': 22.0,
            'temperatura_max': 28.0,
            'temperatura_min': 16.0,
            'umidade': 65,
            'pressao': 1013,
            'velocidade_vento': 10,
            'descricao': 'céu limpo',
            'icone': '01d'
        }

    def _get_fallback_holidays(self, year: int) -> List[Dict]:
        """Feriados de fallback"""
        return [
            {'data': f'{year}-01-01', 'nome': 'Confraternização Universal', 'tipo': 'national', 'uf': 'BR'},
            {'data': f'{year}-04-21', 'nome': 'Tiradentes', 'tipo': 'national', 'uf': 'BR'},
            {'data': f'{year}-05-01', 'nome': 'Dia do Trabalhador', 'tipo': 'national', 'uf': 'BR'},
            {'data': f'{year}-09-07', 'nome': 'Independência do Brasil', 'tipo': 'national', 'uf': 'BR'},
            {'data': f'{year}-10-12', 'nome': 'Nossa Senhora Aparecida', 'tipo': 'national', 'uf': 'BR'},
            {'data': f'{year}-11-02', 'nome': 'Finados', 'tipo': 'national', 'uf': 'BR'},
            {'data': f'{year}-11-15', 'nome': 'Proclamação da República', 'tipo': 'national', 'uf': 'BR'},
            {'data': f'{year}-12-25', 'nome': 'Natal', 'tipo': 'national', 'uf': 'BR'}
        ]

    def _get_fallback_covid_data(self) -> Dict:
        """Dados de COVID-19 de fallback"""
        return {
            'casos_confirmados': 0,
            'casos_recuperados': 0,
            'obitos': 0,
            'casos_ativos': 0,
            'taxa_letalidade': 0,
            'taxa_recuperacao': 0,
            'ultima_atualizacao': datetime.now().strftime('%Y-%m-%d')
        }

# Instância global do serviço
real_data_service = RealDataService()
