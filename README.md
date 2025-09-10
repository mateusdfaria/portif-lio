# HospiCast - Sistema de Previsão de Demanda Hospitalar

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

### Frontend
```bash
cd frontend
npm install
npm start
```

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
