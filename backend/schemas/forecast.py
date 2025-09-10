from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TimePoint(BaseModel):
    ds: str = Field(..., description="Data no formato ISO-8601 (YYYY-MM-DD)")
    y: float = Field(..., description="Valor observado da série")

    class Config:
        extra = "allow"  # permitir colunas adicionais (regressores)


class TrainRequest(BaseModel):
    series_id: str = Field(..., description="Identificador único da série")
    data: List[TimePoint]
    regressors: Optional[List[str]] = Field(
        default=None, description="Nomes das colunas de regressores a incluir"
    )


class PredictRequest(BaseModel):
    series_id: str
    horizon: int = Field(..., gt=0, le=365, description="Períodos futuros a prever")
    latitude: Optional[float] = Field(None, description="Latitude para dados climáticos")
    longitude: Optional[float] = Field(None, description="Longitude para dados climáticos")


class ForecastPoint(BaseModel):
    ds: str
    yhat: float
    yhat_lower: Optional[float] = None
    yhat_upper: Optional[float] = None


class Insight(BaseModel):
    type: str = Field(..., description="Tipo do insight")
    title: str = Field(..., description="Título do insight")
    message: str = Field(..., description="Mensagem descritiva")
    impact: str = Field(..., description="Nível de impacto: high, medium, low")
    date: Optional[str] = Field(None, description="Data específica do evento")
    start_date: Optional[str] = Field(None, description="Data de início do evento")
    end_date: Optional[str] = Field(None, description="Data de fim do evento")
    expected_increase: Optional[str] = Field(None, description="Aumento esperado")
    expected_change: Optional[str] = Field(None, description="Mudança esperada")

class InsightsSummary(BaseModel):
    total_insights: int = Field(..., description="Total de insights gerados")
    high_impact: int = Field(..., description="Número de insights de alto impacto")
    medium_impact: int = Field(..., description="Número de insights de médio impacto")
    low_impact: int = Field(..., description="Número de insights de baixo impacto")
    insights: List[Insight] = Field(..., description="Lista de insights")

class ForecastResponse(BaseModel):
    series_id: str
    forecast: List[ForecastPoint]
    insights: Optional[InsightsSummary] = Field(None, description="Insights derivados da previsão")


class ModelsResponse(BaseModel):
    models: List[str]



