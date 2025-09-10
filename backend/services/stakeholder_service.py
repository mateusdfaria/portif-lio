import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import random

class StakeholderType(Enum):
    """Tipos de stakeholders"""
    DOCTOR = "doctor"
    NURSE = "nurse"
    MANAGER = "manager"
    ADMINISTRATOR = "administrator"
    DIRECTOR = "director"

class FeedbackType(Enum):
    """Tipos de feedback"""
    ACCURACY = "accuracy"
    USABILITY = "usability"
    RELEVANCE = "relevance"
    TIMELINESS = "timeliness"
    ACTIONABILITY = "actionability"

class FeedbackRating(Enum):
    """Classificação do feedback"""
    EXCELLENT = 5
    GOOD = 4
    AVERAGE = 3
    POOR = 2
    TERRIBLE = 1

@dataclass
class Stakeholder:
    """Estrutura de um stakeholder"""
    id: str
    name: str
    email: str
    role: str
    stakeholder_type: StakeholderType
    hospital_id: str
    department: str
    experience_years: int
    specialties: List[str]
    is_active: bool
    created_at: str

@dataclass
class Feedback:
    """Estrutura de um feedback"""
    id: str
    stakeholder_id: str
    stakeholder_name: str
    hospital_id: str
    feedback_type: FeedbackType
    rating: FeedbackRating
    comment: str
    context: Dict
    timestamp: str
    is_anonymous: bool
    metadata: Dict

@dataclass
class ValidationSession:
    """Sessão de validação com stakeholders"""
    id: str
    hospital_id: str
    session_type: str  # "forecast_review", "dashboard_test", "alert_evaluation"
    participants: List[str]
    start_time: str
    end_time: Optional[str]
    objectives: List[str]
    results: Dict
    recommendations: List[str]
    status: str  # "planned", "in_progress", "completed", "cancelled"

class StakeholderService:
    """Serviço para gerenciar stakeholders e validações"""
    
    def __init__(self):
        self.stakeholders = self._load_stakeholders()
        self.feedback_history = []
        self.validation_sessions = []
        self.next_feedback_id = 1
        self.next_session_id = 1
    
    def _load_stakeholders(self) -> List[Stakeholder]:
        """Carrega stakeholders simulados"""
        stakeholders_data = [
            # Médicos
            {
                "id": "stakeholder_001",
                "name": "Dr. Ana Silva",
                "email": "ana.silva@hospital.com",
                "role": "Médica Coordenadora da Emergência",
                "stakeholder_type": StakeholderType.DOCTOR,
                "hospital_id": "hosp_joinville_ps",
                "department": "Emergência",
                "experience_years": 15,
                "specialties": ["Medicina de Emergência", "Clínica Médica"],
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "stakeholder_002",
                "name": "Dr. Carlos Mendes",
                "email": "carlos.mendes@hospital.com",
                "role": "Diretor Médico",
                "stakeholder_type": StakeholderType.DIRECTOR,
                "hospital_id": "hosp_joinville_ps",
                "department": "Diretoria",
                "experience_years": 25,
                "specialties": ["Administração Hospitalar", "Medicina Interna"],
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "stakeholder_003",
                "name": "Enf. Maria Santos",
                "email": "maria.santos@hospital.com",
                "role": "Enfermeira Supervisora da UTI",
                "stakeholder_type": StakeholderType.NURSE,
                "hospital_id": "hosp_joinville_ps",
                "department": "UTI",
                "experience_years": 12,
                "specialties": ["Enfermagem Intensiva", "Gestão de Enfermagem"],
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "stakeholder_004",
                "name": "Sr. João Oliveira",
                "email": "joao.oliveira@hospital.com",
                "role": "Gerente Administrativo",
                "stakeholder_type": StakeholderType.MANAGER,
                "hospital_id": "hosp_joinville_ps",
                "department": "Administração",
                "experience_years": 8,
                "specialties": ["Gestão Hospitalar", "Administração"],
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "stakeholder_005",
                "name": "Dr. Pedro Costa",
                "email": "pedro.costa@hospital.com",
                "role": "Médico da UTI",
                "stakeholder_type": StakeholderType.DOCTOR,
                "hospital_id": "hosp_joinville_ps",
                "department": "UTI",
                "experience_years": 10,
                "specialties": ["Medicina Intensiva", "Anestesiologia"],
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            },
            # Stakeholders de outros hospitais
            {
                "id": "stakeholder_006",
                "name": "Dr. Lucia Fernandes",
                "email": "lucia.fernandes@hospital.com",
                "role": "Coordenadora Médica",
                "stakeholder_type": StakeholderType.DOCTOR,
                "hospital_id": "hosp_florianopolis_central",
                "department": "Emergência",
                "experience_years": 18,
                "specialties": ["Medicina de Emergência", "Pediatria"],
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "stakeholder_007",
                "name": "Sr. Roberto Alves",
                "email": "roberto.alves@hospital.com",
                "role": "Diretor Executivo",
                "stakeholder_type": StakeholderType.DIRECTOR,
                "hospital_id": "hosp_sao_paulo_central",
                "department": "Diretoria",
                "experience_years": 30,
                "specialties": ["Administração Hospitalar", "Gestão Estratégica"],
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        
        return [Stakeholder(**data) for data in stakeholders_data]
    
    def get_stakeholders(self, hospital_id: Optional[str] = None, 
                        stakeholder_type: Optional[StakeholderType] = None) -> List[Stakeholder]:
        """Retorna lista de stakeholders com filtros opcionais"""
        filtered_stakeholders = [s for s in self.stakeholders if s.is_active]
        
        if hospital_id:
            filtered_stakeholders = [s for s in filtered_stakeholders if s.hospital_id == hospital_id]
        
        if stakeholder_type:
            filtered_stakeholders = [s for s in filtered_stakeholders if s.stakeholder_type == stakeholder_type]
        
        return filtered_stakeholders
    
    def get_stakeholder_by_id(self, stakeholder_id: str) -> Optional[Stakeholder]:
        """Retorna stakeholder por ID"""
        for stakeholder in self.stakeholders:
            if stakeholder.id == stakeholder_id:
                return stakeholder
        return None
    
    def submit_feedback(self, stakeholder_id: str, feedback_type: FeedbackType, 
                       rating: FeedbackRating, comment: str, context: Dict = None,
                       is_anonymous: bool = False) -> Feedback:
        """Submete feedback de um stakeholder"""
        stakeholder = self.get_stakeholder_by_id(stakeholder_id)
        if not stakeholder:
            raise ValueError("Stakeholder não encontrado")
        
        feedback_id = f"feedback_{self.next_feedback_id}"
        self.next_feedback_id += 1
        
        feedback = Feedback(
            id=feedback_id,
            stakeholder_id=stakeholder_id,
            stakeholder_name=stakeholder.name if not is_anonymous else "Anônimo",
            hospital_id=stakeholder.hospital_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            context=context or {},
            timestamp=datetime.now().isoformat(),
            is_anonymous=is_anonymous,
            metadata={
                "stakeholder_role": stakeholder.role,
                "stakeholder_type": stakeholder.stakeholder_type.value,
                "department": stakeholder.department,
                "experience_years": stakeholder.experience_years
            }
        )
        
        self.feedback_history.append(feedback)
        return feedback
    
    def get_feedback_summary(self, hospital_id: Optional[str] = None, 
                           feedback_type: Optional[FeedbackType] = None,
                           days: int = 30) -> Dict:
        """Retorna resumo de feedbacks"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()
        
        filtered_feedback = [
            f for f in self.feedback_history 
            if f.timestamp >= cutoff_str
        ]
        
        if hospital_id:
            filtered_feedback = [f for f in filtered_feedback if f.hospital_id == hospital_id]
        
        if feedback_type:
            filtered_feedback = [f for f in filtered_feedback if f.feedback_type == feedback_type]
        
        if not filtered_feedback:
            return {
                "total_feedback": 0,
                "average_rating": 0,
                "rating_distribution": {},
                "feedback_by_type": {},
                "recent_comments": []
            }
        
        # Calcular estatísticas
        ratings = [f.rating.value for f in filtered_feedback]
        average_rating = sum(ratings) / len(ratings)
        
        # Distribuição de ratings
        rating_distribution = {}
        for rating in FeedbackRating:
            count = len([f for f in filtered_feedback if f.rating == rating])
            rating_distribution[rating.name.lower()] = count
        
        # Feedback por tipo
        feedback_by_type = {}
        for feedback_type in FeedbackType:
            count = len([f for f in filtered_feedback if f.feedback_type == feedback_type])
            feedback_by_type[feedback_type.value] = count
        
        # Comentários recentes
        recent_comments = [
            {
                "comment": f.comment,
                "rating": f.rating.name,
                "type": f.feedback_type.value,
                "timestamp": f.timestamp,
                "stakeholder": f.stakeholder_name
            }
            for f in sorted(filtered_feedback, key=lambda x: x.timestamp, reverse=True)[:10]
        ]
        
        return {
            "total_feedback": len(filtered_feedback),
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution,
            "feedback_by_type": feedback_by_type,
            "recent_comments": recent_comments,
            "period_days": days
        }
    
    def create_validation_session(self, hospital_id: str, session_type: str,
                                participants: List[str], objectives: List[str]) -> ValidationSession:
        """Cria uma sessão de validação"""
        session_id = f"session_{self.next_session_id}"
        self.next_session_id += 1
        
        session = ValidationSession(
            id=session_id,
            hospital_id=hospital_id,
            session_type=session_type,
            participants=participants,
            start_time=datetime.now().isoformat(),
            end_time=None,
            objectives=objectives,
            results={},
            recommendations=[],
            status="in_progress"
        )
        
        self.validation_sessions.append(session)
        return session
    
    def complete_validation_session(self, session_id: str, results: Dict, 
                                  recommendations: List[str]) -> bool:
        """Completa uma sessão de validação"""
        for session in self.validation_sessions:
            if session.id == session_id:
                session.end_time = datetime.now().isoformat()
                session.results = results
                session.recommendations = recommendations
                session.status = "completed"
                return True
        return False
    
    def simulate_realistic_feedback(self, hospital_id: str, context: Dict) -> List[Feedback]:
        """Simula feedback realista baseado no contexto"""
        stakeholders = self.get_stakeholders(hospital_id=hospital_id)
        if not stakeholders:
            return []
        
        feedbacks = []
        
        # Simular feedback baseado no contexto
        for stakeholder in stakeholders:
            # Determinar tipo de feedback baseado no contexto
            if "forecast_accuracy" in context:
                feedback_type = FeedbackType.ACCURACY
                accuracy = context["forecast_accuracy"]
                
                # Médicos tendem a ser mais críticos com precisão
                if stakeholder.stakeholder_type == StakeholderType.DOCTOR:
                    if accuracy > 0.8:
                        rating = random.choice([FeedbackRating.EXCELLENT, FeedbackRating.GOOD])
                        comment = f"A precisão das previsões está muito boa. Como médica com {stakeholder.experience_years} anos de experiência, posso confiar nos dados para planejamento."
                    elif accuracy > 0.6:
                        rating = random.choice([FeedbackRating.GOOD, FeedbackRating.AVERAGE])
                        comment = f"As previsões são úteis, mas ainda há margem para melhoria. Às vezes preciso ajustar o planejamento baseado na experiência clínica."
                    else:
                        rating = random.choice([FeedbackRating.POOR, FeedbackRating.TERRIBLE])
                        comment = f"As previsões não refletem a realidade clínica. Preciso confiar mais na experiência do que nos dados."
                else:
                    # Gestores tendem a ser mais pragmáticos
                    if accuracy > 0.8:
                        rating = FeedbackRating.EXCELLENT
                        comment = f"Excelente ferramenta para planejamento estratégico. Os dados nos ajudam a otimizar recursos."
                    elif accuracy > 0.6:
                        rating = FeedbackRating.GOOD
                        comment = f"Útil para tomada de decisões, mas precisamos de mais precisão para investimentos críticos."
                    else:
                        rating = FeedbackRating.AVERAGE
                        comment = f"Conceito interessante, mas precisa de mais desenvolvimento antes de ser usado em decisões importantes."
            
            elif "dashboard_usability" in context:
                feedback_type = FeedbackType.USABILITY
                usability_score = context["dashboard_usability"]
                
                if stakeholder.stakeholder_type in [StakeholderType.DOCTOR, StakeholderType.NURSE]:
                    if usability_score > 0.8:
                        rating = FeedbackRating.GOOD
                        comment = f"Interface intuitiva. Como profissional da saúde, consigo navegar facilmente e encontrar as informações que preciso."
                    else:
                        rating = FeedbackRating.AVERAGE
                        comment = f"Precisa ser mais simples. Durante o plantão não tenho tempo para aprender interfaces complexas."
                else:
                    if usability_score > 0.8:
                        rating = FeedbackRating.EXCELLENT
                        comment = f"Dashboard muito bem estruturado. Facilita a análise de dados e tomada de decisões gerenciais."
                    else:
                        rating = FeedbackRating.GOOD
                        comment = f"Boa funcionalidade, mas poderia ter mais opções de filtros e relatórios personalizados."
            
            elif "alert_relevance" in context:
                feedback_type = FeedbackType.RELEVANCE
                relevance_score = context["alert_relevance"]
                
                if stakeholder.stakeholder_type == StakeholderType.DOCTOR:
                    if relevance_score > 0.8:
                        rating = FeedbackRating.EXCELLENT
                        comment = f"Os alertas são muito relevantes para a prática clínica. Me ajudam a antecipar picos de demanda."
                    else:
                        rating = FeedbackRating.AVERAGE
                        comment = f"Alguns alertas são úteis, mas muitos são falsos positivos que geram desgaste desnecessário."
                else:
                    if relevance_score > 0.8:
                        rating = FeedbackRating.GOOD
                        comment = f"Sistema de alertas eficiente para gestão de recursos e planejamento de equipes."
                    else:
                        rating = FeedbackRating.AVERAGE
                        comment = f"Alertas úteis, mas precisam ser mais específicos para diferentes níveis hierárquicos."
            
            else:
                # Feedback genérico
                feedback_type = random.choice(list(FeedbackType))
                rating = random.choice(list(FeedbackRating))
                comment = f"Feedback sobre {feedback_type.value} do sistema HospiCast."
            
            # Adicionar variação baseada na experiência
            if stakeholder.experience_years > 20:
                # Profissionais mais experientes tendem a ser mais críticos
                if rating.value > 3:
                    rating = FeedbackRating(max(1, rating.value - 1))
            elif stakeholder.experience_years < 5:
                # Profissionais mais novos tendem a ser mais positivos
                if rating.value < 4:
                    rating = FeedbackRating(min(5, rating.value + 1))
            
            feedback = self.submit_feedback(
                stakeholder_id=stakeholder.id,
                feedback_type=feedback_type,
                rating=rating,
                comment=comment,
                context=context,
                is_anonymous=False
            )
            
            feedbacks.append(feedback)
        
        return feedbacks
    
    def generate_validation_report(self, hospital_id: str, days: int = 30) -> Dict:
        """Gera relatório de validação para um hospital"""
        stakeholders = self.get_stakeholders(hospital_id=hospital_id)
        feedback_summary = self.get_feedback_summary(hospital_id=hospital_id, days=days)
        
        # Calcular métricas por tipo de stakeholder
        stakeholder_metrics = {}
        for stakeholder_type in StakeholderType:
            type_stakeholders = [s for s in stakeholders if s.stakeholder_type == stakeholder_type]
            if type_stakeholders:
                type_feedback = [
                    f for f in self.feedback_history 
                    if f.stakeholder_id in [s.id for s in type_stakeholders]
                    and f.timestamp >= (datetime.now() - timedelta(days=days)).isoformat()
                ]
                
                if type_feedback:
                    avg_rating = sum(f.rating.value for f in type_feedback) / len(type_feedback)
                    stakeholder_metrics[stakeholder_type.value] = {
                        "count": len(type_stakeholders),
                        "feedback_count": len(type_feedback),
                        "average_rating": round(avg_rating, 2)
                    }
        
        # Recomendações baseadas no feedback
        recommendations = []
        if feedback_summary["average_rating"] < 3.0:
            recommendations.append("Melhorar a precisão das previsões e interface do sistema")
        if feedback_summary["rating_distribution"].get("terrible", 0) > 0:
            recommendations.append("Investigar feedbacks negativos e implementar melhorias urgentes")
        if feedback_summary["total_feedback"] < len(stakeholders) * 0.5:
            recommendations.append("Aumentar engajamento dos stakeholders com o sistema")
        
        return {
            "hospital_id": hospital_id,
            "period_days": days,
            "stakeholders_summary": {
                "total_stakeholders": len(stakeholders),
                "active_stakeholders": len([s for s in stakeholders if s.is_active]),
                "by_type": {t.value: len([s for s in stakeholders if s.stakeholder_type == t]) for t in StakeholderType}
            },
            "feedback_summary": feedback_summary,
            "stakeholder_metrics": stakeholder_metrics,
            "recommendations": recommendations,
            "validation_sessions": len([s for s in self.validation_sessions if s.hospital_id == hospital_id])
        }

# Instância global do serviço
stakeholder_service = StakeholderService()
