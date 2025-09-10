import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from services.real_data_service import real_data_service, RealHospitalData, RealOccupancyData
from services.hospital_service import Hospital, HospitalMetrics, HospitalService
from services.joinville_sus_service import joinville_sus_service, JoinvilleSusHospital

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridHospitalService(HospitalService):
    """Serviço híbrido que combina dados reais com dados simulados"""
    
    def __init__(self):
        super().__init__()
        self.real_data_service = real_data_service
        self.joinville_sus_service = joinville_sus_service
        self.use_real_data = True  # SEMPRE usar dados reais
        self.real_hospitals_cache = {}
        self.last_cache_update = None
        
    def _should_use_real_data(self) -> bool:
        """SEMPRE usar dados reais - não mais dados simulados"""
        return True  # Forçar sempre dados reais
    
    def _check_api_availability(self) -> bool:
        """Verifica se as APIs externas estão disponíveis"""
        try:
            # Testar conectividade com uma API simples
            test_data = self.real_data_service._make_request(
                "https://brasilapi.com.br/api/feriados/v1/2024"
            )
            return test_data is not None
        except Exception as e:
            logger.warning(f"APIs externas não disponíveis: {e}")
            return False
    
    def _load_real_hospitals(self, uf: str = None, municipio: str = None) -> List[Hospital]:
        """Carrega hospitais reais do CNES"""
        try:
            # Verificar cache
            cache_key = f"{uf}_{municipio}"
            if (cache_key in self.real_hospitals_cache and 
                self.last_cache_update and 
                datetime.now() - self.last_cache_update < timedelta(hours=1)):
                return self.real_hospitals_cache[cache_key]
            
            # Buscar dados reais
            real_hospitals = self.real_data_service.get_cnes_data(uf, municipio)
            
            # Converter para formato interno
            hospitals = []
            for real_hosp in real_hospitals:
                hospital = Hospital(
                    id=f"real_{real_hosp.cnes}",
                    name=real_hosp.nome,
                    city=real_hosp.cidade,
                    state=real_hosp.uf,
                    region=self._get_region_from_uf(real_hosp.uf),
                    latitude=real_hosp.latitude,
                    longitude=real_hosp.longitude,
                    capacity=real_hosp.capacidade_leitos,
                    specialties=real_hosp.especialidades,
                    emergency_capacity=real_hosp.leitos_emergencia,
                    icu_capacity=real_hosp.leitos_uti,
                    is_public=real_hosp.gestao in ['Municipal', 'Estadual', 'Federal'],
                    created_at=datetime.now().strftime("%Y-%m-%d")
                )
                hospitals.append(hospital)
            
            # Atualizar cache
            self.real_hospitals_cache[cache_key] = hospitals
            self.last_cache_update = datetime.now()
            
            logger.info(f"Carregados {len(hospitals)} hospitais reais do CNES")
            return hospitals
            
        except Exception as e:
            logger.error(f"Erro ao carregar hospitais reais: {e}")
            return self._load_fallback_hospitals()
    
    def _get_region_from_uf(self, uf: str) -> str:
        """Mapeia UF para região"""
        region_map = {
            'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
            'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 
            'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
            'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
            'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
            'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
        }
        return region_map.get(uf, 'Desconhecida')
    
    def _load_fallback_hospitals(self) -> List[Hospital]:
        """Carrega hospitais de fallback quando APIs reais falham"""
        return super()._load_hospitals()
    
    def get_hospitals(self, city: Optional[str] = None, state: Optional[str] = None, 
                     region: Optional[str] = None, is_public: Optional[bool] = None) -> List[Hospital]:
        """Retorna lista de hospitais (reais ou simulados)"""
        if self._should_use_real_data():
            try:
                hospitals = self._load_real_hospitals(state, city)
                logger.info(f"Usando dados reais: {len(hospitals)} hospitais")
            except Exception as e:
                logger.error(f"Erro ao carregar dados reais, usando fallback: {e}")
                hospitals = super().get_hospitals(city, state, region, is_public)
        else:
            hospitals = super().get_hospitals(city, state, region, is_public)
            logger.info(f"Usando dados simulados: {len(hospitals)} hospitais")
        
        # Aplicar filtros
        filtered_hospitals = hospitals
        
        if city:
            filtered_hospitals = [h for h in filtered_hospitals if h.city.lower() == city.lower()]
        
        if state:
            filtered_hospitals = [h for h in filtered_hospitals if h.state.upper() == state.upper()]
        
        if region:
            filtered_hospitals = [h for h in filtered_hospitals if h.region.lower() == region.lower()]
        
        if is_public is not None:
            filtered_hospitals = [h for h in filtered_hospitals if h.is_public == is_public]
        
        return filtered_hospitals
    
    def get_real_occupancy_data(self, hospital_id: str, start_date: str, end_date: str) -> List[HospitalMetrics]:
        """Busca dados reais de ocupação do SIH"""
        try:
            # Extrair CNES do ID do hospital
            if hospital_id.startswith('real_'):
                cnes = hospital_id.replace('real_', '')
            else:
                logger.warning(f"Hospital {hospital_id} não é um hospital real")
                return self.generate_hospital_metrics(hospital_id, start_date, end_date)
            
            # Buscar dados reais
            real_occupancy = self.real_data_service.get_sih_data(cnes, start_date, end_date)
            
            if not real_occupancy:
                logger.warning(f"Não foi possível obter dados reais para CNES {cnes}")
                return self.generate_hospital_metrics(hospital_id, start_date, end_date)
            
            # Converter para formato interno
            metrics = []
            for real_data in real_occupancy:
                metric = HospitalMetrics(
                    hospital_id=hospital_id,
                    date=real_data.data,
                    occupancy_rate=real_data.ocupacao_leitos,
                    emergency_occupancy=real_data.ocupacao_emergencia,
                    icu_occupancy=real_data.ocupacao_uti,
                    avg_wait_time=real_data.tempo_espera_medio,
                    total_patients=real_data.pacientes_internados,
                    emergency_patients=real_data.pacientes_emergencia,
                    icu_patients=real_data.pacientes_uti,
                    discharges=real_data.altas_dia,
                    admissions=real_data.admissoes_dia
                )
                metrics.append(metric)
            
            logger.info(f"Carregados {len(metrics)} registros reais de ocupação")
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados reais de ocupação: {e}")
            return self.generate_hospital_metrics(hospital_id, start_date, end_date)
    
    def generate_hospital_metrics(self, hospital_id: str, start_date: str, end_date: str) -> List[HospitalMetrics]:
        """Gera métricas (reais ou simuladas) para um hospital"""
        if self._should_use_real_data() and hospital_id.startswith('real_'):
            return self.get_real_occupancy_data(hospital_id, start_date, end_date)
        else:
            return super().generate_hospital_metrics(hospital_id, start_date, end_date)
    
    def get_enhanced_hospital_kpis(self, hospital_id: str, start_date: str, end_date: str) -> Dict:
        """Retorna KPIs enriquecidos com dados externos"""
        # Obter KPIs básicos
        basic_kpis = self.get_hospital_kpis(hospital_id, start_date, end_date)
        
        if not basic_kpis:
            return {}
        
        # Enriquecer com dados externos
        hospital = self.get_hospital_by_id(hospital_id)
        if not hospital:
            return basic_kpis
        
        try:
            # Dados meteorológicos
            weather_data = self.real_data_service.get_weather_data(
                hospital.latitude, hospital.longitude, start_date
            )
            
            # Dados de COVID-19
            covid_data = self.real_data_service.get_covid_data(hospital.state)
            
            # Dados de feriados
            current_year = datetime.now().year
            holidays = self.real_data_service.get_holiday_data(hospital.state, current_year)
            
            # Calcular impacto de fatores externos
            external_factors = self._calculate_external_impact(
                weather_data, covid_data, holidays, start_date, end_date
            )
            
            # Adicionar dados externos aos KPIs
            enhanced_kpis = {
                **basic_kpis,
                'external_factors': external_factors,
                'weather_data': weather_data,
                'covid_data': covid_data,
                'data_source': 'real' if hospital_id.startswith('real_') else 'simulated',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return enhanced_kpis
            
        except Exception as e:
            logger.error(f"Erro ao enriquecer KPIs: {e}")
            return {
                **basic_kpis,
                'data_source': 'simulated',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def _calculate_external_impact(self, weather_data: Dict, covid_data: Dict, 
                                 holidays: List[Dict], start_date: str, end_date: str) -> Dict:
        """Calcula impacto de fatores externos na demanda hospitalar"""
        try:
            # Impacto meteorológico
            temp_impact = 0
            if weather_data['temperatura'] > 30:
                temp_impact += 0.1  # +10% em dias muito quentes
            elif weather_data['temperatura'] < 10:
                temp_impact += 0.15  # +15% em dias muito frios
            
            # Impacto de COVID-19
            covid_impact = 0
            if covid_data['casos_ativos'] > 1000:
                covid_impact += 0.2  # +20% com muitos casos ativos
            
            # Impacto de feriados
            holiday_impact = 0
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            for holiday in holidays:
                holiday_date = datetime.strptime(holiday['data'], "%Y-%m-%d")
                if start_dt <= holiday_date <= end_dt:
                    holiday_impact += 0.05  # +5% em feriados
            
            total_impact = temp_impact + covid_impact + holiday_impact
            
            return {
                'temperature_impact': round(temp_impact * 100, 1),
                'covid_impact': round(covid_impact * 100, 1),
                'holiday_impact': round(holiday_impact * 100, 1),
                'total_impact': round(total_impact * 100, 1),
                'impact_level': 'high' if total_impact > 0.2 else 'medium' if total_impact > 0.1 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular impacto externo: {e}")
            return {
                'temperature_impact': 0,
                'covid_impact': 0,
                'holiday_impact': 0,
                'total_impact': 0,
                'impact_level': 'low'
            }
    
    def get_regional_summary_with_real_data(self, region: str, start_date: str, end_date: str) -> Dict:
        """Retorna resumo regional com dados reais quando disponíveis"""
        # Obter resumo básico
        basic_summary = self.get_regional_summary(region, start_date, end_date)
        
        if not basic_summary:
            return {}
        
        # Enriquecer com dados externos regionais
        try:
            # Dados de COVID-19 regional
            covid_data = self.real_data_service.get_covid_data()
            
            # Calcular tendências regionais
            regional_trends = self._calculate_regional_trends(region, start_date, end_date)
            
            enhanced_summary = {
                **basic_summary,
                'regional_covid_data': covid_data,
                'regional_trends': regional_trends,
                'data_quality': 'real' if self._should_use_real_data() else 'simulated',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return enhanced_summary
            
        except Exception as e:
            logger.error(f"Erro ao enriquecer resumo regional: {e}")
            return {
                **basic_summary,
                'data_quality': 'simulated',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def _calculate_regional_trends(self, region: str, start_date: str, end_date: str) -> Dict:
        """Calcula tendências regionais baseadas em dados históricos"""
        try:
            # Simular cálculo de tendências (em produção, usaria dados históricos reais)
            hospitals = self.get_hospitals(region=region)
            
            if not hospitals:
                return {'trend': 'stable', 'change_percentage': 0}
            
            # Calcular tendência média da região
            total_change = 0
            for hospital in hospitals:
                kpis = self.get_hospital_kpis(hospital.id, start_date, end_date)
                if kpis and 'kpis' in kpis:
                    total_change += kpis['kpis'].get('occupancy_trend', 0)
            
            avg_change = total_change / len(hospitals) if hospitals else 0
            
            return {
                'trend': 'increasing' if avg_change > 5 else 'decreasing' if avg_change < -5 else 'stable',
                'change_percentage': round(avg_change, 1),
                'hospitals_analyzed': len(hospitals)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular tendências regionais: {e}")
            return {'trend': 'stable', 'change_percentage': 0}

# Instância global do serviço híbrido
hybrid_hospital_service = HybridHospitalService()
