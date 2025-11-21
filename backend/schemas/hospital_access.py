"""Schemas para cadastro/autenticação de hospitais."""

from datetime import datetime

from pydantic import BaseModel, Field


class HospitalRegistration(BaseModel):
    display_name: str = Field(..., description="Nome da instituição")
    cnes: str | None = Field(None, description="Identificador CNES")
    city: str | None = Field(None, description="Cidade")
    state: str | None = Field(None, description="UF de duas letras")
    contact_email: str | None = Field(None, description="Contato principal")
    password: str = Field(..., min_length=6, description="Senha para reuso do hospital")


class HospitalRegistrationResponse(BaseModel):
    hospital_id: str
    display_name: str
    short_code: str
    created_at: datetime


class HospitalLogin(BaseModel):
    identifier: str = Field(..., description="ID ou código curto do hospital")
    password: str


class HospitalSession(BaseModel):
    hospital_id: str
    display_name: str
    short_code: str
    token: str
    expires_at: datetime


class ForecastHistoryItem(BaseModel):
    forecast_id: str
    series_id: str
    horizon: int
    average_yhat: float | None
    created_at: datetime
    payload: dict


class ForecastHistoryResponse(BaseModel):
    hospital_id: str
    forecasts: list[ForecastHistoryItem]




