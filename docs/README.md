# HospiCast - Sistema de Previsão de Demanda Hospitalar

[![CI](https://github.com/mateusdfaria/portif-lio/actions/workflows/ci.yml/badge.svg)](https://github.com/mateusdfaria/portif-lio/actions/workflows/ci.yml)
[![Deploy](https://github.com/mateusdfaria/portif-lio/actions/workflows/deploy.yml/badge.svg)](https://github.com/mateusdfaria/portif-lio/actions/workflows/deploy.yml)

Este repositório contém o projeto HospiCast, um sistema completo de previsão de demanda hospitalar utilizando Prophet e outras técnicas de machine learning.

## Estrutura

- **frontend/**: Aplicação React com interface moderna
- **backend/**: API FastAPI em Python com serviços de previsão
- **portif-lio/**: Documentação do projeto (TCC)
- **models/**: Modelos treinados salvos automaticamente

## Como rodar

### Backend
```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

Para desenvolvimento:
```bash
pip install -r requirements-dev.txt
ruff check backend
pytest
```

### Frontend
```bash
cd frontend
npm install
npm start
```

Qualidade:
```bash
npm run lint
npm run test
```

### Variáveis de ambiente

1. Copie `env.example` para `.env`.
2. Ajuste `API_ALLOWED_ORIGINS`, `LOG_LEVEL`, `PROMETHEUS_ENABLED` e demais valores conforme o ambiente.

### Qualidade e CI

- Backend: `ruff check backend` e `pytest`.
- Frontend: `npm run lint` e `npm run test`.
- GitHub Actions (`.github/workflows/ci.yml`) executa automaticamente essas verificações em cada push/pull request.
- Detalhes adicionais em `ENGINEERING_GUIDE.md`.

### Scripts de inicialização
```bash
# Iniciar backend e frontend simultaneamente
python start_hospicast.py

# Ou individualmente
python start_backend.py
python start_frontend.py
```

## API

Base URL padrão: `http://localhost:8000`

- `GET /` — status da API

### Forecast

- `POST /forecast/train` — Treina um modelo com JSON
  - Body: `{ "series_id": "str", "data": [{"ds": "YYYY-MM-DD", "y": number, ...}], "regressors": ["colA", ...] }`
  - Retorna: `{ status: "ok", series_id: "..." }`

- `POST /forecast/train-file` — Treina um modelo com CSV (multipart/form-data)
  - Campos: `series_id: string`, `file: CSV (colunas ds,y)`
  - Retorna: `{ status: "ok", series_id: "..." }`

- `POST /forecast/predict` — Gera previsão
  - Body: `{ "series_id": "str", "horizon": 14 }`
  - Retorna: `{ series_id: "...", forecast: [{ ds, yhat, yhat_lower, yhat_upper }] }`

- `GET /forecast/models` — Lista modelos disponíveis

### Cidades

- `GET /cities` — Lista cidades disponíveis para previsão

## Características

- **Previsão com Prophet**: Utiliza Facebook Prophet para séries temporais
- **Múltiplos modelos**: Suporte a diferentes tipos de dados hospitalares
- **Interface moderna**: Frontend React com design responsivo
- **API robusta**: Backend FastAPI com validação de dados
- **Documentação completa**: Inclui documentação técnica e RFC

## Observações

- CSV deve conter colunas `ds` (datas) e `y` (valores)
- Modelos são salvos em `backend/models/` por `series_id`
- Sistema otimizado para previsão de demanda hospitalar
