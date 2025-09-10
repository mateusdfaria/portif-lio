# HospiCast - Starter Project

Este repositório contém a base inicial para o projeto HospiCast.

## Estrutura

- **frontend/**: Aplicação React
- **backend/**: API FastAPI em Python
- **docs/**: Documentação do TCC

## Como rodar

### Backend
```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
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

Observações:
- CSV deve conter colunas `ds` (datas) e `y` (valores).
- Modelos são salvos em `backend/models/` por `series_id`.
