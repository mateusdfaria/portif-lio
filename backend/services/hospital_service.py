import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class Hospital:
    """Estrutura de dados para hospital"""
    id: str
    name: str
    city: str
    state: str
    region: str
    latitude: float
    longitude: float
    capacity: int
    specialties: List[str]
    emergency_capacity: int
    icu_capacity: int
    is_public: bool
    created_at: str

@dataclass
class HospitalMetrics:
    """Métricas de um hospital"""
    hospital_id: str
    date: str
    occupancy_rate: float
    emergency_occupancy: float
    icu_occupancy: float
    avg_wait_time: float
    total_patients: int
    emergency_patients: int
    icu_patients: int
    discharges: int
    admissions: int

class HospitalService:
    """Serviço para gerenciar hospitais e suas métricas"""
    
    def __init__(self):
        self.hospitals = self._load_hospitals()
        self.metrics_cache = {}
    
    def _load_hospitals(self) -> List[Hospital]:
        """Carrega lista de hospitais brasileiros"""
        # Dados simulados de hospitais brasileiros principais
        hospitals_data = [
            {
                "id": "hosp_infantil_joinville",
                "name": "Hospital Infantil de Joinville",
                "city": "Joinville",
                "state": "SC",
                "region": "Sul",
                "latitude": -26.3044,
                "longitude": -48.8456,
                "capacity": 150,
                "specialties": ["Pediatria", "Cirurgia Pediátrica", "Cardiologia Pediátrica", "Neurologia Pediátrica", "Oncologia Pediátrica", "UTI Pediátrica"],
                "emergency_capacity": 30,
                "icu_capacity": 25,
                "is_public": True,
                "created_at": "2024-01-01"
            },
            {
                "id": "hosp_joinville_ps",
                "name": "Hospital Municipal São José - Joinville",
                "city": "Joinville",
                "state": "SC",
                "region": "Sul",
                "latitude": -26.3044,
                "longitude": -48.8456,
                "capacity": 200,
                "specialties": ["Emergência", "Cardiologia", "Neurologia", "Pediatria"],
                "emergency_capacity": 50,
                "icu_capacity": 20,
                "is_public": True,
                "created_at": "2024-01-01"
            },
            {
                "id": "hosp_florianopolis_central",
                "name": "Hospital Universitário - Florianópolis",
                "city": "Florianópolis",
                "state": "SC",
                "region": "Sul",
                "latitude": -27.5954,
                "longitude": -48.5480,
                "capacity": 300,
                "specialties": ["Emergência", "Cardiologia", "Neurologia", "Pediatria", "Oncologia"],
                "emergency_capacity": 80,
                "icu_capacity": 30,
                "is_public": True,
                "created_at": "2024-01-01"
            },
            {
                "id": "hosp_curitiba_central",
                "name": "Hospital de Clínicas - Curitiba",
                "city": "Curitiba",
                "state": "PR",
                "region": "Sul",
                "latitude": -25.4284,
                "longitude": -49.2733,
                "capacity": 500,
                "specialties": ["Emergência", "Cardiologia", "Neurologia", "Pediatria", "Oncologia", "Transplantes"],
                "emergency_capacity": 120,
                "icu_capacity": 50,
                "is_public": True,
                "created_at": "2024-01-01"
            },
            {
                "id": "hosp_sao_paulo_central",
                "name": "Hospital das Clínicas - São Paulo",
                "city": "São Paulo",
                "state": "SP",
                "region": "Sudeste",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "capacity": 1000,
                "specialties": ["Emergência", "Cardiologia", "Neurologia", "Pediatria", "Oncologia", "Transplantes", "Trauma"],
                "emergency_capacity": 200,
                "icu_capacity": 100,
                "is_public": True,
                "created_at": "2024-01-01"
            },
            {
                "id": "hosp_rio_janeiro_central",
                "name": "Hospital Universitário Clementino Fraga Filho - Rio de Janeiro",
                "city": "Rio de Janeiro",
                "state": "RJ",
                "region": "Sudeste",
                "latitude": -22.9068,
                "longitude": -43.1729,
                "capacity": 400,
                "specialties": ["Emergência", "Cardiologia", "Neurologia", "Pediatria", "Oncologia"],
                "emergency_capacity": 100,
                "icu_capacity": 40,
                "is_public": True,
                "created_at": "2024-01-01"
            },
            {
                "id": "hosp_belo_horizonte_central",
                "name": "Hospital das Clínicas - Belo Horizonte",
                "city": "Belo Horizonte",
                "state": "MG",
                "region": "Sudeste",
                "latitude": -19.9167,
                "longitude": -43.9345,
                "capacity": 600,
                "specialties": ["Emergência", "Cardiologia", "Neurologia", "Pediatria", "Oncologia", "Transplantes"],
                "emergency_capacity": 150,
                "icu_capacity": 60,
                "is_public": True,
                "created_at": "2024-01-01"
            },
            {
                "id": "hosp_salvador_central",
                "name": "Hospital Universitário Professor Edgard Santos - Salvador",
                "city": "Salvador",
                "state": "BA",
                "region": "Nordeste",
                "latitude": -12.9714,
                "longitude": -38.5014,
                "capacity": 350,
                "specialties": ["Emergência", "Cardiologia", "Neurologia", "Pediatria", "Oncologia"],
                "emergency_capacity": 90,
                "icu_capacity": 35,
                "is_public": True,
                "created_at": "2024-01-01"
            },
            {
                "id": "hosp_recife_central",
                "name": "Hospital das Clínicas - Recife",
                "city": "Recife",
                "state": "PE",
                "region": "Nordeste",
                "latitude": -8.0476,
                "longitude": -34.8770,
                "capacity": 450,
                "specialties": ["Emergência", "Cardiologia", "Neurologia", "Pediatria", "Oncologia", "Transplantes"],
                "emergency_capacity": 110,
                "icu_capacity": 45,
                "is_public": True,
                "created_at": "2024-01-01"
            },
            {
                "id": "hosp_manaus_central",
                "name": "Hospital Universitário Getúlio Vargas - Manaus",
                "city": "Manaus",
                "state": "AM",
                "region": "Norte",
                "latitude": -3.1190,
                "longitude": -60.0217,
                "capacity": 300,
                "specialties": ["Emergência", "Cardiologia", "Neurologia", "Pediatria", "Oncologia"],
                "emergency_capacity": 75,
                "icu_capacity": 30,
                "is_public": True,
                "created_at": "2024-01-01"
            },
            {
                "id": "hosp_brasilia_central",
                "name": "Hospital Universitário de Brasília",
                "city": "Brasília",
                "state": "DF",
                "region": "Centro-Oeste",
                "latitude": -15.7801,
                "longitude": -47.9292,
                "capacity": 400,
                "specialties": ["Emergência", "Cardiologia", "Neurologia", "Pediatria", "Oncologia", "Transplantes"],
                "emergency_capacity": 100,
                "icu_capacity": 40,
                "is_public": True,
                "created_at": "2024-01-01"
            }
        ]
        
        return [Hospital(**hospital_data) for hospital_data in hospitals_data]
    
    def get_hospitals(self, city: Optional[str] = None, state: Optional[str] = None, 
                     region: Optional[str] = None, is_public: Optional[bool] = None) -> List[Hospital]:
        """Retorna lista de hospitais com filtros opcionais"""
        filtered_hospitals = self.hospitals
        
        if city:
            filtered_hospitals = [h for h in filtered_hospitals if h.city.lower() == city.lower()]
        
        if state:
            filtered_hospitals = [h for h in filtered_hospitals if h.state.upper() == state.upper()]
        
        if region:
            filtered_hospitals = [h for h in filtered_hospitals if h.region.lower() == region.lower()]
        
        if is_public is not None:
            filtered_hospitals = [h for h in filtered_hospitals if h.is_public == is_public]
        
        return filtered_hospitals
    
    def get_hospital_by_id(self, hospital_id: str) -> Optional[Hospital]:
        """Retorna hospital por ID"""
        for hospital in self.hospitals:
            if hospital.id == hospital_id:
                return hospital
        return None
    
    def search_hospitals(self, query: str, limit: int = 10) -> List[Hospital]:
        """Busca hospitais por nome ou cidade"""
        query_lower = query.lower()
        results = []
        
        for hospital in self.hospitals:
            if (query_lower in hospital.name.lower() or 
                query_lower in hospital.city.lower() or
                query_lower in hospital.state.lower()):
                results.append(hospital)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_hospital_coordinates(self, hospital_id: str) -> Optional[Dict[str, float]]:
        """Retorna coordenadas de um hospital"""
        hospital = self.get_hospital_by_id(hospital_id)
        if hospital:
            return {
                "latitude": hospital.latitude,
                "longitude": hospital.longitude
            }
        return None
    
    def generate_hospital_metrics(self, hospital_id: str, start_date: str, end_date: str) -> List[HospitalMetrics]:
        """Gera métricas simuladas para um hospital"""
        hospital = self.get_hospital_by_id(hospital_id)
        if not hospital:
            return []
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        metrics = []
        current_date = start
        
        while current_date <= end:
            # Gerar métricas baseadas na capacidade do hospital
            base_occupancy = np.random.normal(0.7, 0.15)  # 70% ± 15%
            base_occupancy = max(0.3, min(0.95, base_occupancy))  # Limitar entre 30% e 95%
            
            # Ajustar por sazonalidade (mais ocupado no inverno)
            month = current_date.month
            if month in [6, 7, 8]:  # Inverno
                seasonal_factor = 1.2
            elif month in [12, 1, 2]:  # Verão
                seasonal_factor = 0.9
            else:
                seasonal_factor = 1.0
            
            # Ajustar por dia da semana (mais ocupado em dias úteis)
            weekday = current_date.weekday()
            if weekday < 5:  # Dias úteis
                weekday_factor = 1.1
            else:  # Fim de semana
                weekday_factor = 0.8
            
            # Calcular métricas finais
            occupancy_rate = base_occupancy * seasonal_factor * weekday_factor
            occupancy_rate = max(0.2, min(0.98, occupancy_rate))
            
            emergency_occupancy = occupancy_rate * np.random.normal(1.1, 0.1)
            emergency_occupancy = max(0.3, min(1.0, emergency_occupancy))
            
            icu_occupancy = occupancy_rate * np.random.normal(0.9, 0.1)
            icu_occupancy = max(0.2, min(0.95, icu_occupancy))
            
            # Tempo de espera baseado na ocupação
            avg_wait_time = 30 + (occupancy_rate * 120)  # 30-150 minutos
            
            # Números de pacientes
            total_patients = int(hospital.capacity * occupancy_rate)
            emergency_patients = int(hospital.emergency_capacity * emergency_occupancy)
            icu_patients = int(hospital.icu_capacity * icu_occupancy)
            
            # Admissões e altas (aproximadamente 20% do total por dia)
            daily_turnover = int(total_patients * 0.2)
            admissions = daily_turnover + np.random.randint(-5, 6)
            discharges = daily_turnover + np.random.randint(-5, 6)
            
            metric = HospitalMetrics(
                hospital_id=hospital_id,
                date=current_date.strftime("%Y-%m-%d"),
                occupancy_rate=round(occupancy_rate, 3),
                emergency_occupancy=round(emergency_occupancy, 3),
                icu_occupancy=round(icu_occupancy, 3),
                avg_wait_time=round(avg_wait_time, 1),
                total_patients=total_patients,
                emergency_patients=emergency_patients,
                icu_patients=icu_patients,
                discharges=max(0, discharges),
                admissions=max(0, admissions)
            )
            
            metrics.append(metric)
            current_date += timedelta(days=1)
        
        return metrics
    
    def get_hospital_kpis(self, hospital_id: str, start_date: str, end_date: str) -> Dict:
        """Retorna KPIs agregados de um hospital"""
        metrics = self.generate_hospital_metrics(hospital_id, start_date, end_date)
        
        if not metrics:
            return {}
        
        # Calcular KPIs agregados
        avg_occupancy = np.mean([m.occupancy_rate for m in metrics])
        avg_emergency_occupancy = np.mean([m.emergency_occupancy for m in metrics])
        avg_icu_occupancy = np.mean([m.icu_occupancy for m in metrics])
        avg_wait_time = np.mean([m.avg_wait_time for m in metrics])
        
        total_admissions = sum([m.admissions for m in metrics])
        total_discharges = sum([m.discharges for m in metrics])
        
        # Calcular tendências (últimos 7 dias vs anteriores)
        if len(metrics) >= 14:
            recent_metrics = metrics[-7:]
            previous_metrics = metrics[-14:-7]
            
            recent_occupancy = np.mean([m.occupancy_rate for m in recent_metrics])
            previous_occupancy = np.mean([m.occupancy_rate for m in previous_metrics])
            
            occupancy_trend = ((recent_occupancy - previous_occupancy) / previous_occupancy) * 100
        else:
            occupancy_trend = 0
        
        # Determinar status de alerta
        alert_level = "verde"
        if avg_occupancy > 0.9 or avg_emergency_occupancy > 0.95 or avg_wait_time > 120:
            alert_level = "vermelho"
        elif avg_occupancy > 0.8 or avg_emergency_occupancy > 0.85 or avg_wait_time > 90:
            alert_level = "amarelo"
        
        hospital = self.get_hospital_by_id(hospital_id)
        
        return {
            "hospital_id": hospital_id,
            "hospital_name": hospital.name if hospital else "Hospital Desconhecido",
            "period": f"{start_date} a {end_date}",
            "kpis": {
                "avg_occupancy_rate": round(avg_occupancy * 100, 1),
                "avg_emergency_occupancy": round(avg_emergency_occupancy * 100, 1),
                "avg_icu_occupancy": round(avg_icu_occupancy * 100, 1),
                "avg_wait_time": round(avg_wait_time, 1),
                "total_admissions": total_admissions,
                "total_discharges": total_discharges,
                "occupancy_trend": round(occupancy_trend, 1)
            },
            "alert_level": alert_level,
            "capacity": {
                "total_capacity": hospital.capacity if hospital else 0,
                "emergency_capacity": hospital.emergency_capacity if hospital else 0,
                "icu_capacity": hospital.icu_capacity if hospital else 0
            },
            "metrics_count": len(metrics)
        }
    
    def get_regional_summary(self, region: str, start_date: str, end_date: str) -> Dict:
        """Retorna resumo regional de hospitais"""
        hospitals = self.get_hospitals(region=region)
        
        if not hospitals:
            return {}
        
        regional_kpis = []
        total_capacity = 0
        total_emergency_capacity = 0
        total_icu_capacity = 0
        
        for hospital in hospitals:
            kpis = self.get_hospital_kpis(hospital.id, start_date, end_date)
            if kpis:
                regional_kpis.append(kpis)
                total_capacity += hospital.capacity
                total_emergency_capacity += hospital.emergency_capacity
                total_icu_capacity += hospital.icu_capacity
        
        if not regional_kpis:
            return {}
        
        # Calcular médias regionais
        avg_occupancy = np.mean([kpi["kpis"]["avg_occupancy_rate"] for kpi in regional_kpis])
        avg_emergency_occupancy = np.mean([kpi["kpis"]["avg_emergency_occupancy"] for kpi in regional_kpis])
        avg_icu_occupancy = np.mean([kpi["kpis"]["avg_icu_occupancy"] for kpi in regional_kpis])
        avg_wait_time = np.mean([kpi["kpis"]["avg_wait_time"] for kpi in regional_kpis])
        
        # Contar alertas
        red_alerts = sum([1 for kpi in regional_kpis if kpi["alert_level"] == "vermelho"])
        yellow_alerts = sum([1 for kpi in regional_kpis if kpi["alert_level"] == "amarelo"])
        green_alerts = sum([1 for kpi in regional_kpis if kpi["alert_level"] == "verde"])
        
        return {
            "region": region,
            "period": f"{start_date} a {end_date}",
            "hospitals_count": len(hospitals),
            "regional_kpis": {
                "avg_occupancy_rate": round(avg_occupancy, 1),
                "avg_emergency_occupancy": round(avg_emergency_occupancy, 1),
                "avg_icu_occupancy": round(avg_icu_occupancy, 1),
                "avg_wait_time": round(avg_wait_time, 1)
            },
            "capacity": {
                "total_capacity": total_capacity,
                "emergency_capacity": total_emergency_capacity,
                "icu_capacity": total_icu_capacity
            },
            "alerts": {
                "red": red_alerts,
                "yellow": yellow_alerts,
                "green": green_alerts
            },
            "hospitals": regional_kpis
        }

# Instância global do serviço
hospital_service = HospitalService()
