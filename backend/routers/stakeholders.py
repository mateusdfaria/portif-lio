from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict
from services.stakeholder_service import stakeholder_service, StakeholderType, FeedbackType, FeedbackRating
from datetime import datetime, timedelta

router = APIRouter(prefix="/stakeholders", tags=["stakeholders"])

@router.get("/")
def get_stakeholders(
    hospital_id: Optional[str] = Query(None, description="Filtrar por hospital"),
    stakeholder_type: Optional[str] = Query(None, description="Filtrar por tipo (doctor, nurse, manager, administrator, director)")
):
    """Lista stakeholders com filtros opcionais"""
    try:
        parsed_type = None
        if stakeholder_type:
            try:
                parsed_type = StakeholderType(stakeholder_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Tipo de stakeholder inválido")
        
        stakeholders = stakeholder_service.get_stakeholders(hospital_id, parsed_type)
        
        return {
            "status": "ok",
            "count": len(stakeholders),
            "stakeholders": [
                {
                    "id": s.id,
                    "name": s.name,
                    "email": s.email,
                    "role": s.role,
                    "stakeholder_type": s.stakeholder_type.value,
                    "hospital_id": s.hospital_id,
                    "department": s.department,
                    "experience_years": s.experience_years,
                    "specialties": s.specialties,
                    "is_active": s.is_active,
                    "created_at": s.created_at
                }
                for s in stakeholders
            ]
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/{stakeholder_id}")
def get_stakeholder(stakeholder_id: str):
    """Retorna detalhes de um stakeholder específico"""
    try:
        stakeholder = stakeholder_service.get_stakeholder_by_id(stakeholder_id)
        
        if not stakeholder:
            raise HTTPException(status_code=404, detail="Stakeholder não encontrado")
        
        return {
            "status": "ok",
            "stakeholder": {
                "id": stakeholder.id,
                "name": stakeholder.name,
                "email": stakeholder.email,
                "role": stakeholder.role,
                "stakeholder_type": stakeholder.stakeholder_type.value,
                "hospital_id": stakeholder.hospital_id,
                "department": stakeholder.department,
                "experience_years": stakeholder.experience_years,
                "specialties": stakeholder.specialties,
                "is_active": stakeholder.is_active,
                "created_at": stakeholder.created_at
            }
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/feedback")
def submit_feedback(
    stakeholder_id: str = Body(..., description="ID do stakeholder"),
    feedback_type: str = Body(..., description="Tipo de feedback"),
    rating: int = Body(..., description="Classificação (1-5)"),
    comment: str = Body(..., description="Comentário"),
    context: Dict = Body(default={}, description="Contexto adicional"),
    is_anonymous: bool = Body(False, description="Feedback anônimo")
):
    """Submete feedback de um stakeholder"""
    try:
        # Validar tipo de feedback
        try:
            parsed_feedback_type = FeedbackType(feedback_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Tipo de feedback inválido")
        
        # Validar rating
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating deve estar entre 1 e 5")
        
        try:
            parsed_rating = FeedbackRating(rating)
        except ValueError:
            raise HTTPException(status_code=400, detail="Rating inválido")
        
        feedback = stakeholder_service.submit_feedback(
            stakeholder_id=stakeholder_id,
            feedback_type=parsed_feedback_type,
            rating=parsed_rating,
            comment=comment,
            context=context,
            is_anonymous=is_anonymous
        )
        
        return {
            "status": "ok",
            "message": "Feedback submetido com sucesso",
            "feedback": {
                "id": feedback.id,
                "stakeholder_name": feedback.stakeholder_name,
                "feedback_type": feedback.feedback_type.value,
                "rating": feedback.rating.value,
                "comment": feedback.comment,
                "timestamp": feedback.timestamp,
                "is_anonymous": feedback.is_anonymous
            }
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/feedback/summary")
def get_feedback_summary(
    hospital_id: Optional[str] = Query(None, description="Filtrar por hospital"),
    feedback_type: Optional[str] = Query(None, description="Filtrar por tipo de feedback"),
    days: int = Query(30, description="Período em dias")
):
    """Retorna resumo de feedbacks"""
    try:
        parsed_feedback_type = None
        if feedback_type:
            try:
                parsed_feedback_type = FeedbackType(feedback_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Tipo de feedback inválido")
        
        summary = stakeholder_service.get_feedback_summary(hospital_id, parsed_feedback_type, days)
        
        return {
            "status": "ok",
            **summary
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/feedback/simulate")
def simulate_realistic_feedback(
    hospital_id: str = Body(..., description="ID do hospital"),
    context: Dict = Body(..., description="Contexto para simulação")
):
    """Simula feedback realista baseado no contexto"""
    try:
        feedbacks = stakeholder_service.simulate_realistic_feedback(hospital_id, context)
        
        return {
            "status": "ok",
            "message": f"Simulação de feedback concluída para {len(feedbacks)} stakeholders",
            "hospital_id": hospital_id,
            "context": context,
            "feedbacks": [
                {
                    "id": f.id,
                    "stakeholder_name": f.stakeholder_name,
                    "feedback_type": f.feedback_type.value,
                    "rating": f.rating.value,
                    "comment": f.comment,
                    "timestamp": f.timestamp,
                    "metadata": f.metadata
                }
                for f in feedbacks
            ]
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/validation/session")
def create_validation_session(
    hospital_id: str = Body(..., description="ID do hospital"),
    session_type: str = Body(..., description="Tipo de sessão"),
    participants: List[str] = Body(..., description="IDs dos participantes"),
    objectives: List[str] = Body(..., description="Objetivos da sessão")
):
    """Cria uma sessão de validação"""
    try:
        session = stakeholder_service.create_validation_session(
            hospital_id=hospital_id,
            session_type=session_type,
            participants=participants,
            objectives=objectives
        )
        
        return {
            "status": "ok",
            "message": "Sessão de validação criada com sucesso",
            "session": {
                "id": session.id,
                "hospital_id": session.hospital_id,
                "session_type": session.session_type,
                "participants": session.participants,
                "start_time": session.start_time,
                "objectives": session.objectives,
                "status": session.status
            }
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/validation/session/{session_id}/complete")
def complete_validation_session(
    session_id: str,
    results: Dict = Body(..., description="Resultados da sessão"),
    recommendations: List[str] = Body(..., description="Recomendações")
):
    """Completa uma sessão de validação"""
    try:
        success = stakeholder_service.complete_validation_session(
            session_id=session_id,
            results=results,
            recommendations=recommendations
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Sessão de validação não encontrada")
        
        return {
            "status": "ok",
            "message": "Sessão de validação completada com sucesso",
            "session_id": session_id,
            "completed_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/validation/report/{hospital_id}")
def get_validation_report(
    hospital_id: str,
    days: int = Query(30, description="Período em dias")
):
    """Gera relatório de validação para um hospital"""
    try:
        report = stakeholder_service.generate_validation_report(hospital_id, days)
        
        return {
            "status": "ok",
            **report
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/hospital/{hospital_id}/dashboard")
def get_stakeholder_dashboard(hospital_id: str):
    """Retorna dados para dashboard de stakeholders"""
    try:
        stakeholders = stakeholder_service.get_stakeholders(hospital_id=hospital_id)
        feedback_summary = stakeholder_service.get_feedback_summary(hospital_id=hospital_id, days=30)
        
        # Calcular métricas por departamento
        department_stats = {}
        for stakeholder in stakeholders:
            dept = stakeholder.department
            if dept not in department_stats:
                department_stats[dept] = {
                    "total_stakeholders": 0,
                    "by_type": {},
                    "avg_experience": 0,
                    "total_experience": 0
                }
            
            department_stats[dept]["total_stakeholders"] += 1
            department_stats[dept]["total_experience"] += stakeholder.experience_years
            
            stakeholder_type = stakeholder.stakeholder_type.value
            if stakeholder_type not in department_stats[dept]["by_type"]:
                department_stats[dept]["by_type"][stakeholder_type] = 0
            department_stats[dept]["by_type"][stakeholder_type] += 1
        
        # Calcular média de experiência por departamento
        for dept in department_stats:
            if department_stats[dept]["total_stakeholders"] > 0:
                department_stats[dept]["avg_experience"] = round(
                    department_stats[dept]["total_experience"] / department_stats[dept]["total_stakeholders"], 1
                )
        
        return {
            "status": "ok",
            "hospital_id": hospital_id,
            "stakeholders_summary": {
                "total_stakeholders": len(stakeholders),
                "active_stakeholders": len([s for s in stakeholders if s.is_active]),
                "by_type": {t.value: len([s for s in stakeholders if s.stakeholder_type == t]) for t in StakeholderType},
                "by_department": department_stats
            },
            "feedback_summary": feedback_summary,
            "engagement_rate": round(
                (feedback_summary["total_feedback"] / len(stakeholders)) * 100, 1
            ) if stakeholders else 0
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
