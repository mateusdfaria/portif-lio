from pydantic import BaseModel, Field


class TimePoint(BaseModel):
    ds: str = Field(..., description="Data no formato ISO-8601 (YYYY-MM-DD)")
    y: float = Field(..., description="Valor observado da série")

    class Config:
        extra = "allow"  # permitir colunas adicionais (regressores)


class TrainRequest(BaseModel):
    series_id: str = Field(..., description="Identificador único da série")
    data: list[TimePoint]
    regressors: list[str] | None = Field(
        default=None, description="Nomes das colunas de regressores a incluir"
    )


class PredictRequest(BaseModel):
    series_id: str
    horizon: int = Field(..., gt=0, le=365, description="Períodos futuros a prever")
    latitude: float | None = Field(None, description="Latitude para dados climáticos")
    longitude: float | None = Field(None, description="Longitude para dados climáticos")
    hospital_id: str | None = Field(
        None, description="Identificador do hospital autenticado para salvar histórico"
    )
    session_token: str | None = Field(
        None, description="Token de sessão emitido no login do hospital"
    )


class ForecastPoint(BaseModel):
    ds: str
    yhat: float
    yhat_lower: float | None = None
    yhat_upper: float | None = None


class Insight(BaseModel):
    type: str = Field(..., description="Tipo do insight")
    title: str = Field(..., description="Título do insight")
    message: str = Field(..., description="Mensagem descritiva")
    impact: str = Field(..., description="Nível de impacto: high, medium, low")
    date: str | None = Field(None, description="Data específica do evento")
    start_date: str | None = Field(None, description="Data de início do evento")
    end_date: str | None = Field(None, description="Data de fim do evento")
    expected_increase: str | None = Field(None, description="Aumento esperado")
    expected_change: str | None = Field(None, description="Mudança esperada")

class InsightsSummary(BaseModel):
    total_insights: int = Field(..., description="Total de insights gerados")
    high_impact: int = Field(..., description="Número de insights de alto impacto")
    medium_impact: int = Field(..., description="Número de insights de médio impacto")
    low_impact: int = Field(..., description="Número de insights de baixo impacto")
    insights: list[Insight] = Field(..., description="Lista de insights")

class ForecastResponse(BaseModel):
    series_id: str
    forecast: list[ForecastPoint]
    insights: InsightsSummary | None = Field(None, description="Insights derivados da previsão")


class ModelsResponse(BaseModel):
    models: list[str]



