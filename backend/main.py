from core.config import get_settings
from core.logging import configure_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

# Verificar/instalar CmdStan se necessário (para Prophet)
# NOTA: Em produção (Cloud Run), CmdStan já está instalado no Dockerfile
# Esta verificação é apenas para desenvolvimento local
import os
if os.getenv("ENVIRONMENT") != "production":
    try:
        import cmdstanpy
        try:
            # Verificar se CmdStan está instalado (sem instalar)
            from cmdstanpy import CmdStanModel
            print("✅ CmdStan já está instalado")
        except Exception:
            # Em produção, não tentar instalar (já está no Dockerfile)
            print("⚠️  CmdStan não encontrado, mas continuando...")
    except ImportError:
        print("⚠️  cmdstanpy não está instalado. Prophet pode não funcionar corretamente.")
else:
    print("✅ Ambiente de produção - CmdStan já instalado no container")

try:
    # Local imports may fail before files exist during initial boot; guarded import
    from routers.forecast import router as forecast_router
    print("✅ Router de forecast carregado com sucesso")
except Exception as e:  # pragma: no cover - safe fallback before files are created
    print(f"❌ Erro ao carregar router de forecast: {e}")
    forecast_router = None

try:
    from routers.cities import router as cities_router
    print("✅ Router de cidades carregado com sucesso")
except Exception as e:  # pragma: no cover - safe fallback before files are created
    print(f"❌ Erro ao carregar router de cidades: {e}")
    cities_router = None

try:
    from routers.hospitals import router as hospitals_router
    print("✅ Router de hospitais carregado com sucesso")
except Exception as e:  # pragma: no cover - safe fallback before files are created
    print(f"❌ Erro ao carregar router de hospitais: {e}")
    hospitals_router = None

try:
    from routers.alerts import router as alerts_router
    print("✅ Router de alertas carregado com sucesso")
except Exception as e:  # pragma: no cover - safe fallback before files are created
    print(f"❌ Erro ao carregar router de alertas: {e}")
    alerts_router = None

try:
    from routers.stakeholders import router as stakeholders_router
    print("✅ Router de stakeholders carregado com sucesso")
except Exception as e:  # pragma: no cover - safe fallback before files are created
    print(f"❌ Erro ao carregar router de stakeholders: {e}")
    stakeholders_router = None

try:
    from routers.real_data import router as real_data_router
    print("✅ Router de dados reais carregado com sucesso")
except Exception as e:  # pragma: no cover - safe fallback before files are created
    print(f"❌ Erro ao carregar router de dados reais: {e}")
    real_data_router = None

try:
    from routers.joinville_sus import router as joinville_sus_router
    print("✅ Router dos Hospitais SUS de Joinville carregado com sucesso")
except Exception as e:  # pragma: no cover - safe fallback before files are created
    print(f"❌ Erro ao carregar router dos Hospitais SUS: {e}")
    joinville_sus_router = None

try:
    from routers.hospital_access import router as hospital_access_router
    print("✅ Router de acesso hospitalar carregado com sucesso")
except Exception as e:  # pragma: no cover
    print(f"❌ Erro ao carregar router de acesso hospitalar: {e}")
    hospital_access_router = None

settings = get_settings()
logger = configure_logging()

app = FastAPI(title=settings.api_title, version=settings.api_version)

# CORS configurável (React em 3000 durante desenvolvimento por padrão)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.prometheus_enabled:
    Instrumentator().instrument(app).expose(app)
    logger.info("📊 Endpoint /metrics habilitado para Prometheus")


@app.get("/")
def root():
    return {"message": "HospiCast API funcionando!"}


if forecast_router:
    app.include_router(forecast_router)

if cities_router:
    app.include_router(cities_router)

if hospitals_router:
    app.include_router(hospitals_router)

if alerts_router:
    app.include_router(alerts_router)
    logger.debug("Router de alertas incluído")

if stakeholders_router:
    app.include_router(stakeholders_router)

if real_data_router:
    app.include_router(real_data_router)

if joinville_sus_router:
    app.include_router(joinville_sus_router)

if hospital_access_router:
    app.include_router(hospital_access_router)
