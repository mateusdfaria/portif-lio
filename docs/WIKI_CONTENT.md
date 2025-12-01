# HospiCast - Conteúdo para Wiki do GitHub

Este arquivo contém o conteúdo que deve ser adicionado à Wiki do GitHub. Copie e cole cada seção na Wiki.

---

## 📚 Índice da Wiki

1. [Home](#home)
2. [Instalação](#instalação)
3. [Configuração](#configuração)
4. [Uso](#uso)
5. [API Reference](#api-reference)
6. [Desenvolvimento](#desenvolvimento)
7. [Deploy](#deploy)
8. [Troubleshooting](#troubleshooting)

---

## 🏠 Home

### HospiCast - Sistema de Previsão de Demanda Hospitalar

O **HospiCast** é um sistema completo de previsão de demanda hospitalar utilizando machine learning (Facebook Prophet) para prever ocupação hospitalar.

### Características Principais

- ✅ Previsão de demanda com Prophet
- ✅ Integração com dados reais (CNES, SIH, BrasilAPI)
- ✅ Monitoramento SUS para Joinville
- ✅ Sistema de cadastro e autenticação de hospitais
- ✅ Comparação de previsões com métricas de acurácia
- ✅ Interface moderna e responsiva

### Links Rápidos

- [Documentação Completa](https://github.com/mateusdfaria/portif-lio/blob/main/README.md)
- [RFC do Projeto](https://github.com/mateusdfaria/portif-lio/blob/main/HospiCast_RFC_Atualizado.md)
- [Status do Projeto](https://github.com/mateusdfaria/portif-lio/blob/main/PROJETO_STATUS.md)

---

## 📦 Instalação

### Pré-requisitos

- Python 3.11+
- Node.js 20+
- Docker (opcional)

### Instalação Local

#### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### Frontend

```bash
cd frontend
npm install
```

### Instalação com Docker

```bash
docker-compose up -d
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

Copie `env.example` para `.env` e configure:

```bash
# API
API_TITLE=HospiCast API
API_VERSION=0.1.0
API_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=INFO

# Monitoramento
PROMETHEUS_ENABLED=true
```

---

## 🚀 Uso

### Iniciar o Sistema

#### Backend

```bash
cd backend
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend
npm start
```

### Treinar um Modelo

1. Acesse a interface web
2. Faça upload de um CSV com colunas `ds` (data) e `y` (valor)
3. Informe o `series_id`
4. Clique em "Treinar"

### Gerar Previsão

1. Selecione o modelo treinado
2. Escolha o horizonte (dias)
3. Clique em "Prever"

---

## 📡 API Reference

### Endpoints Principais

#### Forecast

- `POST /forecast/train-file` - Treinar modelo com CSV
- `POST /forecast/predict` - Gerar previsão
- `POST /forecast/compare-predictions` - Comparar previsões
- `GET /forecast/models` - Listar modelos

#### Hospital Access

- `POST /hospital-access/register` - Cadastrar hospital
- `POST /hospital-access/login` - Autenticar
- `GET /hospital-access/{id}/forecasts` - Histórico

#### Joinville SUS

- `GET /joinville-sus/hospitals` - Listar hospitais
- `GET /joinville-sus/hospitals/{cnes}/sus-data` - Dados SUS
- `GET /joinville-sus/alerts` - Alertas

[Ver documentação completa da API](https://github.com/mateusdfaria/portif-lio/blob/main/README.md#api)

---

## 💻 Desenvolvimento

### Estrutura do Projeto

```
backend/
  ├── core/          # Configuração centralizada
  ├── routers/       # Endpoints da API
  ├── services/      # Lógica de negócio
  ├── schemas/       # Modelos Pydantic
  └── tests/         # Testes automatizados

frontend/
  ├── src/
  │   ├── components/  # Componentes React
  │   └── App.jsx      # Aplicação principal
  └── package.json
```

### Testes

#### Backend

```bash
pytest backend/tests/
```

#### Frontend

```bash
cd frontend
npm run test
```

### Linting

#### Backend

```bash
ruff check backend
```

#### Frontend

```bash
cd frontend
npm run lint
```

### TDD (Test-Driven Development)

O projeto segue práticas de TDD:

1. **Escrever teste primeiro** - Defina o comportamento esperado
2. **Executar teste** - Deve falhar (Red)
3. **Implementar código** - Código mínimo para passar
4. **Refatorar** - Melhorar código mantendo testes passando

Exemplo:

```python
# 1. Teste primeiro
def test_calculate_occupancy_rate():
    assert calculate_occupancy_rate(80, 100) == 0.8

# 2. Implementação
def calculate_occupancy_rate(occupied, total):
    return occupied / total if total > 0 else 0
```

---

## 🚢 Deploy

### Deploy Automático via CI/CD

O projeto possui GitHub Actions configurado para:

- ✅ **CI**: Executa testes e linting em cada push
- ✅ **Deploy**: Deploy automático para produção em `main`

### Deploy Manual

Ver [DEPLOY.md](https://github.com/mateusdfaria/portif-lio/blob/main/DEPLOY.md)

---

## 🔧 Troubleshooting

### Problemas Comuns

#### Erro de encoding ao treinar

**Solução**: O sistema detecta automaticamente o encoding. Se persistir, salve o CSV como UTF-8.

#### Modelo não encontrado

**Solução**: Verifique se o `series_id` está correto e se o modelo foi treinado.

#### Erro de CORS

**Solução**: Configure `API_ALLOWED_ORIGINS` no `.env` com a URL do frontend.

#### Testes falhando

**Solução**: 
```bash
# Backend
pip install -r backend/requirements-dev.txt
pytest backend/tests/

# Frontend
cd frontend
npm install
npm run test
```

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/mateusdfaria/portif-lio/issues)
- **Documentação**: [README.md](https://github.com/mateusdfaria/portif-lio/blob/main/README.md)

---

*Última atualização: Janeiro 2025*

