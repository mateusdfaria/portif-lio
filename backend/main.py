from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app = FastAPI(title="HospiCast API", version="0.1.0")

# CORS for local development (React on port 3000 by default)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

if stakeholders_router:
    app.include_router(stakeholders_router)

if real_data_router:
    app.include_router(real_data_router)

if joinville_sus_router:
    app.include_router(joinville_sus_router)
