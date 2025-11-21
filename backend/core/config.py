"""Carregamento e validação de configurações do backend."""

from functools import lru_cache

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Configurações globais do backend carregadas via variáveis de ambiente."""

    api_title: str = Field("HospiCast API", env="API_TITLE")
    api_version: str = Field("0.1.0", env="API_VERSION")
    allowed_origins: list[str] = Field(default_factory=lambda: ["*"], env="API_ALLOWED_ORIGINS")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    prometheus_enabled: bool = Field(True, env="PROMETHEUS_ENABLED")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("allowed_origins", pre=True)
    def _split_origins(cls, value: str | list[str]) -> list[str]:  # type: ignore[override]
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Retorna instância única de configurações carregadas."""
    return Settings()




