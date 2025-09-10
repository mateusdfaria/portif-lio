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
