"""Rotas para cadastro, login e histórico de hospitais."""

from fastapi import APIRouter, Header, HTTPException, status
from schemas.hospital_access import (
    ForecastHistoryResponse,
    HospitalLogin,
    HospitalRegistration,
    HospitalRegistrationResponse,
    HospitalSession,
)
from services.hospital_account_service import hospital_account_service

router = APIRouter(prefix="/hospital-access", tags=["hospital-access"])


@router.post("/register", response_model=HospitalRegistrationResponse, status_code=status.HTTP_201_CREATED)
def register(request: HospitalRegistration) -> HospitalRegistrationResponse:
    try:
        record = hospital_account_service.register_hospital(request.dict())
        return HospitalRegistrationResponse(**record)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/login", response_model=HospitalSession)
def login(request: HospitalLogin) -> HospitalSession:
    try:
        session = hospital_account_service.authenticate(request.identifier, request.password)
        return HospitalSession(**session)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{hospital_id}/forecasts", response_model=ForecastHistoryResponse)
def list_forecasts(
    hospital_id: str,
    x_hospital_token: str = Header(..., description="Token de sessão do hospital"),
) -> ForecastHistoryResponse:
    if not hospital_account_service.validate_session(hospital_id, x_hospital_token):
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada.")

    forecasts = hospital_account_service.list_forecasts(hospital_id)
    return ForecastHistoryResponse(hospital_id=hospital_id, forecasts=forecasts)

