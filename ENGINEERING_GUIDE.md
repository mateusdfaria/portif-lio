# Guia de Engenharia do HospiCast

Este guia documenta as práticas adotadas para Qualidade Técnica e Infraestrutura/DevOps do projeto na PAC 8.

## 1. Versionamento e Fluxo de Trabalho
- **Branches principais**: `main` (produção) e `develop` (pré-produção). Funcionalidades novas surgem em `feature/<escopo>` e hotfixes em `hotfix/<issue>`.
- **Issues GitHub**: cada issue referencia uma linha do Portfólio (ex.: `PAC8-Infra`, `PAC8-QA`). Commits usam o padrão `tipo: descrição` e fecham issues via `Fixes #ID`.
- **Commits frequentes**: recomenda-se granularidade diária com mensagem curta + contexto; exemplos constam no histórico recente.

## 2. Qualidade Técnica do Código
- **Estrutura modular**: backend dividido em `routers/`, `services/`, `schemas/`, `core/` e `models/`; frontend em componentes React modulares.
- **Linters/Formatação**:
  - Backend: `ruff` configurado via `pyproject.toml`.
  - Frontend: `eslint` com regras para hooks e React Refresh.
- **Testes Automatizados**:
  - Backend: `pytest` cobre serviços (ex.: `alerts_service`) e roda no CI com `pytest --maxfail=1`.
  - Frontend: `vitest` + Testing Library garantem renderização básica do `App`.

## 3. CI/CD
- Workflow GitHub Actions (`.github/workflows/ci.yml`) executa em push/PR:
  1. Instala requisitos Python (`backend/requirements-dev.txt`), roda `ruff` e `pytest`.
  2. Instala dependências Node (`npm ci`), roda `npm run lint` e `npm run test`.
- Deploy segue `DEPLOY.md` utilizando Docker/Compose; releases são criadas a partir de `main`.

## 4. Infraestrutura, Monitoramento e Observabilidade
- **Configuração via ambiente**: arquivo `env.example` documenta variáveis como `API_ALLOWED_ORIGINS`, `LOG_LEVEL` e `PROMETHEUS_ENABLED`. Copie para `.env` em cada ambiente.
- **Logging estruturado**: módulo `backend/core/logging.py` aplica `dictConfig` com formato padrão (`timestamp | level | logger | mensagem`).
- **Métricas**: `prometheus-fastapi-instrumentator` habilita `/metrics` para coleta por Prometheus/Grafana ou Railway Insights.
- **Containers e scripts**: `docker-compose.yml` e `docker-compose.prod.yml` realizam build/deploy com frontend + backend + banco. `deploy.sh` automatiza publicação em ambientes cloud (Railway/Render).

## 5. Segurança
- Configurações sensíveis via `.env`, nunca commitadas.
- CORS limitado por `API_ALLOWED_ORIGINS`.
- Deploy em HTTPS (Railway/Render) conforme `DEPLOY.md`.
- Autenticação JWT prevista para endpoints sensíveis na fase seguinte (descrita no roadmap).

## 6. Práticas DevOps
- **Releases**: taggear versões (`vX.Y.Z`) após passar pelo pipeline.
- **Rollback**: manter imagens Docker anteriores publicadas no registry.
- **Infra como código**: compose + scripts PowerShell/Bash (`start_hospicast.py`, `deploy.sh`) garantem ambientes reproduzíveis.

Este documento deve ser citado no RFC e na apresentação do Demo Day como evidência de maturidade de engenharia.




