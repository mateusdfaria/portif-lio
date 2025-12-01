# 🏥 HospiCast - Sistema de Previsão de Demanda Hospitalar

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Sistema avançado de previsão de demanda hospitalar utilizando Machine Learning**

[Documentação](#-documentação) • [Funcionalidades](#-funcionalidades) • [Tecnologias](#-tecnologias) • [Instalação](#-instalação) • [Deploy](#-deploy)

</div>

---

## 📋 Sobre o Projeto

O **HospiCast** é um sistema completo de previsão de demanda hospitalar desenvolvido para auxiliar gestores de saúde na tomada de decisões estratégicas. Utilizando técnicas avançadas de **Machine Learning** (Facebook Prophet) e integração com dados reais de APIs brasileiras, o sistema oferece previsões precisas de ocupação hospitalar com horizonte de até 30 dias.

### 🎯 Objetivo

Fornecer previsões confiáveis de demanda hospitalar, considerando fatores como:
- 📅 **Feriados e eventos especiais**
- 🌤️ **Condições climáticas**
- 📊 **Padrões sazonais e tendências históricas**
- 🏥 **Características específicas de cada hospital**

### 💡 Diferenciais

- ✅ **Modelos especializados** para Pronto-Socorro e hospitais SUS
- ✅ **Integração com dados reais** (CNES, SIH, BrasilAPI, OpenWeatherMap)
- ✅ **Ensemble de modelos** para maior robustez
- ✅ **Interface web intuitiva** com visualizações interativas
- ✅ **Sistema de autenticação** para hospitais
- ✅ **Métricas de qualidade** (MAE, RMSE, MAPE, sMAPE)
- ✅ **Backtesting automático** para validação de modelos

---

## 🚀 Funcionalidades

### 📊 Previsão de Demanda

- **Previsões de curto e médio prazo** (7 a 30 dias)
- **Intervalos de confiança** (lower/upper bounds)
- **Múltiplos modelos** (Prophet, Naive, Ensemble)
- **Regressores externos** (clima, feriados, eventos)

### 🏥 Gestão Hospitalar

- **Cadastro de hospitais** com autenticação
- **Histórico de previsões** por hospital
- **Comparação de modelos** (Prophet vs Baseline)
- **Métricas de desempenho** em tempo real

### 📈 Visualizações

- **Gráficos interativos** (Chart.js)
- **Exportação de dados** (CSV, PNG)
- **Painéis especializados**:
  - Hospitais SUS de Joinville
  - Comparação de previsões
  - Sessão hospitalar

### 🔍 Integrações

- **CNES** (Cadastro Nacional de Estabelecimentos de Saúde)
- **SIH** (Sistema de Informações Hospitalares)
- **BrasilAPI** (Feriados nacionais, COVID-19)
- **OpenWeatherMap** (Dados meteorológicos)

---

## 🛠️ Tecnologias

### Backend

- **Python 3.11**
- **FastAPI** - Framework web assíncrono
- **Facebook Prophet** - Modelo de previsão temporal
- **PostgreSQL** - Banco de dados relacional
- **SQLite** - Banco de dados para desenvolvimento
- **Pandas** - Manipulação de dados
- **NumPy** - Computação numérica
- **Prometheus** - Métricas e monitoramento

### Frontend

- **React 18.2** - Biblioteca JavaScript
- **Vite** - Build tool e dev server
- **Chart.js** - Visualizações de gráficos
- **React Chart.js 2** - Wrapper React para Chart.js

### DevOps & Infraestrutura

- **Docker** - Containerização
- **Google Cloud Run** - Plataforma serverless
- **Google Cloud SQL** - Banco de dados gerenciado
- **Google Cloud Storage** - Armazenamento de arquivos estáticos
- **GitHub Actions** - CI/CD automatizado
- **Nginx** - Servidor web para frontend

---

## 📁 Estrutura do Projeto

```
portif-lio/
├── backend/                 # API FastAPI
│   ├── core/               # Configurações core
│   │   ├── config.py      # Configurações da aplicação
│   │   ├── database.py    # Abstração de banco de dados
│   │   └── logging.py      # Configuração de logs
│   ├── routers/           # Endpoints da API
│   │   ├── forecast.py    # Previsões
│   │   ├── hospitals.py   # Gestão de hospitais
│   │   ├── alerts.py      # Alertas
│   │   └── ...
│   ├── services/          # Lógica de negócio
│   │   ├── prophet_service.py      # Serviço Prophet
│   │   ├── weather_service.py      # Integração clima
│   │   ├── holidays_service.py     # Feriados
│   │   └── ...
│   ├── schemas/           # Modelos Pydantic
│   ├── tests/             # Testes automatizados
│   └── requirements.txt   # Dependências Python
│
├── frontend/              # Interface React
│   ├── src/
│   │   ├── App.jsx        # Componente principal
│   │   └── components/    # Componentes React
│   ├── package.json       # Dependências Node.js
│   └── vite.config.js     # Configuração Vite
│
├── .github/
│   └── workflows/         # GitHub Actions CI/CD
│       └── deploy-cloud-run.yml
│
├── scripts/               # Scripts de automação
│   ├── deploy_cloud_shell.sh
│   └── corrigir_database_url.sh
│
├── docs/                  # Documentação
│   └── ...
│
└── README.md              # Este arquivo
```

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.11+**
- **Node.js 20+**
- **Docker** (opcional, para containerização)
- **PostgreSQL** (opcional, para produção)

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/portif-lio.git
cd portif-lio
```

> 💡 **Nota**: Substitua `seu-usuario` pela sua URL do GitHub. Veja [`docs/COMO_TROCAR_LINKS_PROJETO.md`](docs/COMO_TROCAR_LINKS_PROJETO.md) para mais detalhes.

### 2. Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desenvolvimento

# Configurar variáveis de ambiente
cp ../env.example .env
# Editar .env com suas configurações

# Executar servidor
uvicorn main:app --reload --port 8001
```

### 3. Frontend

```bash
cd frontend

# Instalar dependências
npm install --legacy-peer-deps

# Executar servidor de desenvolvimento
npm run dev
```

### 4. Acessar aplicação

- **Backend API**: http://127.0.0.1:8001
- **Frontend**: http://localhost:5173
- **Documentação API**: http://127.0.0.1:8001/docs

---

## 🐳 Docker

### Desenvolvimento

```bash
docker-compose up -d
```

### Produção

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## ☁️ Deploy

### Google Cloud Platform

O projeto está configurado para deploy automático no **Google Cloud Run** via GitHub Actions.

#### Pré-requisitos

1. **Google Cloud Project** configurado
2. **Cloud SQL** (PostgreSQL) criado
3. **Cloud Storage** bucket para frontend
4. **Service Account** com permissões adequadas
5. **GitHub Secrets** configurados:
   - `GCP_SA_KEY`
   - `DATABASE_URL`
   - `VITE_API_BASE_URL`

#### Deploy Automático

O deploy é executado automaticamente ao fazer push para a branch `main`:

```bash
git push origin main
```

#### Deploy Manual (Cloud Shell)

```bash
# Executar script de deploy
chmod +x scripts/deploy_cloud_shell.sh
./scripts/deploy_cloud_shell.sh
```

Ou usar os scripts em `scripts/deploy_cloud_shell.sh`

#### URLs de Produção

Após o deploy, o sistema estará disponível em:

- **Frontend**: https://storage.googleapis.com/hospicast-frontend/index.html
- **Backend API**: https://hospicast-backend-fbuqwglmsq-rj.a.run.app
- **API Documentation**: https://hospicast-backend-fbuqwglmsq-rj.a.run.app/docs

> 💡 **Nota**: Para trocar essas URLs, edite os arquivos de configuração ou use domínios personalizados no Google Cloud

---

## 🧪 Testes

### Backend

```bash
cd backend
pytest tests/ --cov=core --cov=services --cov-report=term-missing
```

**Cobertura mínima**: 75%

### Frontend

```bash
cd frontend
npm test
```

**Cobertura mínima**: 25%

---

## 🔍 Qualidade de Código

O projeto utiliza **SonarCloud** para análise contínua de qualidade de código.

### Análise Automática

- ✅ Análise automática em cada push e pull request
- ✅ Detecção de bugs, vulnerabilidades e code smells
- ✅ Métricas de cobertura de testes
- ✅ Complexidade ciclomática
- ✅ Código duplicado

### Configuração

Veja o guia completo em [`SONARCLOUD_SETUP.md`](SONARCLOUD_SETUP.md)

### Executar Análise Local (Opcional)

```bash
# Instalar SonarScanner
# Backend
sonar-scanner -Dproject.settings=backend/sonar-project.properties

# Frontend
sonar-scanner -Dproject.settings=frontend/sonar-project.properties
```

---

## 📊 Métricas e Monitoramento

### Prometheus

O backend expõe métricas Prometheus em `/metrics`:

- Requisições HTTP
- Tempo de resposta
- Erros
- Uso de recursos

### Logs

Logs estruturados com níveis configuráveis:
- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`

---

## 🔐 Segurança

- **CORS** configurável por origem
- **Autenticação** por hospital (senha)
- **Validação de dados** com Pydantic
- **Sanitização** de inputs
- **HTTPS** em produção

---

## 📚 Documentação

### Documentação Técnica

- [`HospiCast_RFC_Atualizado.md`](HospiCast_RFC_Atualizado.md) - Especificação completa do projeto
- [`docs/`](docs/) - Documentação adicional

### API

A documentação interativa da API está disponível em:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

---

## 🎓 Contexto Acadêmico

### Objetivos de Aprendizado

Este projeto demonstra:

1. **Machine Learning Aplicado**
   - Modelos de séries temporais
   - Feature engineering
   - Validação e métricas

2. **Arquitetura de Software**
   - API RESTful
   - Frontend/Backend separados
   - Microserviços

3. **DevOps**
   - CI/CD automatizado
   - Containerização
   - Cloud computing

4. **Integração de Sistemas**
   - APIs externas
   - Bancos de dados
   - Autenticação

### Tecnologias Utilizadas

- **Backend**: Python, FastAPI, Prophet, PostgreSQL
- **Frontend**: React, Vite, Chart.js
- **Cloud**: Google Cloud Platform (Run, SQL, Storage)
- **DevOps**: Docker, GitHub Actions, gcloud CLI

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 👥 Autores

- **Desenvolvedor Principal** - [Seu Nome]
- **Orientador** - [Nome do Professor]

---

## 🙏 Agradecimentos

- **Facebook Prophet** - Framework de previsão temporal
- **FastAPI** - Framework web moderno
- **Google Cloud Platform** - Infraestrutura em nuvem
- **Comunidade Open Source** - Ferramentas e bibliotecas utilizadas

---

## 📞 Contato

Para dúvidas ou sugestões, entre em contato:

- **Email**: [seu-email@exemplo.com]
- **GitHub**: [@seu-usuario]

---

<div align="center">

**Desenvolvido com ❤️ para melhorar a gestão hospitalar**

⭐ Se este projeto foi útil, considere dar uma estrela!

</div>

