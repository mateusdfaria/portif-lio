"""Carregamento e validação de configurações do backend."""

from functools import lru_cache

try:
    # Pydantic v2 - BaseSettings foi movido para pydantic-settings
    from pydantic_settings import BaseSettings
except ImportError:
    # Pydantic v1 - BaseSettings está em pydantic
    try:
        from pydantic import BaseSettings
    except ImportError:
        raise ImportError(
            "pydantic ou pydantic-settings não está instalado. "
            "Instale com: pip install pydantic pydantic-settings"
        )

from pydantic import Field, field_validator
import os


class Settings(BaseSettings):
    """Configurações globais do backend carregadas via variáveis de ambiente."""

    api_title: str = Field("HospiCast API", env="API_TITLE")
    api_version: str = Field("0.1.0", env="API_VERSION")
    allowed_origins: str = Field("*", env="API_ALLOWED_ORIGINS")  # String para evitar parse JSON
    log_level: str = Field("INFO", env="LOG_LEVEL")
    prometheus_enabled: bool = Field(True, env="PROMETHEUS_ENABLED")
    
    # Database configuration
    database_url: str | None = Field(None, env="DATABASE_URL")
    database_type: str = Field("sqlite", env="DATABASE_TYPE")  # sqlite or postgresql
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **data):
        # Interceptar API_ALLOWED_ORIGINS da variável de ambiente antes do Pydantic tentar fazer parse JSON
        if "allowed_origins" not in data:
            env_value = os.getenv("API_ALLOWED_ORIGINS")
            if env_value is not None:
                # Forçar como string, nunca tentar parse JSON
                data["allowed_origins"] = str(env_value)
        super().__init__(**data)
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _validate_allowed_origins(cls, value: str | list[str] | None) -> str:  # type: ignore[override]
        """Força allowed_origins a ser sempre string, evitando parse JSON do Pydantic."""
        if value is None:
            return "*"
        if isinstance(value, list):
            return ",".join(str(v) for v in value)
        return str(value)
    
    def get_allowed_origins_list(self) -> list[str]:
        """Retorna allowed_origins como lista para uso no CORS."""
        if not self.allowed_origins or self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
    
    @field_validator("database_type", mode="before")
    @classmethod
    def _validate_database_type(cls, value: str) -> str:  # type: ignore[override]
        if value.lower() not in ["sqlite", "postgresql", "postgres"]:
            return "sqlite"
        return value.lower()


@lru_cache
def get_settings() -> Settings:
    """Retorna instância única de configurações carregadas."""
    return Settings()




