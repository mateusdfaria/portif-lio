# HospiCast - Sistema de Previsão de Demanda Hospitalar
## RFC Atualizado - Versão 2.0

**Data de Atualização**: Janeiro 2025  
**Versão**: 2.0  
**Status**: Implementado e Funcional  

---

## 📋 Sumário Executivo

O HospiCast é um sistema avançado de previsão de demanda hospitalar que utiliza técnicas de machine learning, especificamente o Facebook Prophet, para prever a ocupação hospitalar. Esta versão 2.0 inclui melhorias significativas baseadas em feedback e demandas reais do setor de saúde.

### 🎯 Principais Melhorias da Versão 2.0

1. **Melhorias Específicas para Pronto-Socorro**
2. **Integração com Dados Reais (APIs Externas)**
3. **Sistema Especializado para Hospitais SUS**
4. **Arquitetura Híbrida Inteligente**
5. **Ensemble de Modelos Avançado**

---

## 🏥 1. Melhorias para Pronto-Socorro

### 1.1 Novos Regressores Implementados

#### **Feriados + Efeito Rebote Pós-Feriado**
- **Regressor `after_holiday`**: Detecta o primeiro dia útil após feriado
- **Exemplo**: 07/09 é feriado (queda), 08/09 tem efeito rebote (pico)
- **Implementação**: Busca feriados nos últimos 3 dias e marca dia útil seguinte

#### **Payday & Fim de Mês**
- **Flag `is_payday`**: Dias 01-05 do mês (pagamento de salários)
- **Flag `month_end`**: Últimos 2 dias do mês
- **Impacto**: Mudam padrão de busca ao PS

#### **Clima Melhorado**
- **Regressores**: `precip` (chuva), `tmax`, `tmin`
- **Lógica**: Chuva aumenta traumas, frio aumenta respiratórios
- **Fonte**: Open-Meteo API integrada

#### **Sazonalidade e Tendência Contidas**
- **`seasonality_mode='additive'`**: Evita "inflar" picos
- **`changepoint_prior_scale=0.01`**: Mais conservador para frear mudanças bruscas
- **`growth='logistic'`**: Com cap = P95 histórico quando necessário

### 1.2 Tratamento de Outliers Aprimorado

#### **Winsorize P1/P99 + 3σ**
- **Winsorize P1/P99**: Limita valores extremos
- **Limite 3σ**: Método estatístico adicional
- **Método conservador**: Usa o mais restritivo entre P1/P99 e 3σ

### 1.3 Backtesting + Seleção de Hiperparâmetros

#### **Cross-validation Temporal**
- **Janelas de 30 dias**: Validação temporal robusta
- **Grid de hiperparâmetros**:
  - `changepoint_prior_scale` ∈ {0.005, 0.01, 0.02}
  - `seasonality_prior_scale` ∈ {2, 5, 10}
  - `seasonality_mode` ∈ {'additive', 'multiplicative'}
- **Seleção**: Menor sMAPE/MAE nas últimas 8-12 semanas

### 1.4 Ensemble Prophet + Naive Semanal

#### **Média Ponderada Inteligente**
- **Combinação**: 0.7*Prophet + 0.3*NaiveSemanal
- **Naive Semanal**: Valor do mesmo dia da semana anterior
- **Benefício**: Reduz erro em variações abruptas de calendário

---

## 🌐 2. Integração com Dados Reais

### 2.1 APIs Integradas

#### **CNES (Cadastro Nacional de Estabelecimentos de Saúde)**
- **Fonte**: Datasus
- **Endpoint**: `https://cnes.datasus.gov.br/services/estabelecimentos`
- **Dados**: Informações de hospitais, capacidades, especialidades
- **Uso**: Lista de hospitais reais brasileiros

#### **SIH (Sistema de Informações Hospitalares)**
- **Fonte**: Datasus
- **Endpoint**: `https://sih.datasus.gov.br/services/ocupacao`
- **Dados**: Ocupação de leitos, admissões, altas
- **Uso**: Métricas de ocupação em tempo real

#### **BrasilAPI**
- **Fonte**: API pública brasileira
- **Endpoints**: 
  - `https://brasilapi.com.br/api/feriados/v1/{year}`
  - `https://brasilapi.com.br/api/covid19/v1`
- **Dados**: Feriados nacionais, dados de COVID-19
- **Uso**: Fatores externos que impactam demanda

#### **OpenWeatherMap**
- **Fonte**: API meteorológica internacional
- **Endpoint**: `https://api.openweathermap.org/data/2.5/weather`
- **Dados**: Temperatura, umidade, condições climáticas
- **Uso**: Impacto do clima na demanda hospitalar

### 2.2 Sistema Híbrido Inteligente

#### **Fallback Automático**
- **APIs reais**: Sempre que disponíveis
- **Dados simulados**: Fallback quando APIs falham
- **Cache inteligente**: Evita muitas requisições
- **Retry automático**: Com backoff exponencial

#### **Dados Enriquecidos**
- **Combinação**: Dados reais + fatores externos
- **Cálculo de impacto**: Clima, COVID-19 e feriados
- **Alertas baseados**: Em dados reais

---

## 🏥 3. Sistema Especializado para Hospitais SUS

### 3.1 Hospitais Integrados em Joinville

#### **Hospital Municipal São José**
- **CNES**: 1234567 (fictício)
- **Tipo**: Municipal
- **Capacidade**: 200 leitos (20 UTI, 50 emergência)
- **Especialidades**: 8 especialidades

#### **Hospital Infantil Dr. Jeser Amarante Faria**
- **CNES**: 2345678 (fictício)
- **Tipo**: Municipal
- **Capacidade**: 150 leitos (25 UTI, 30 emergência)
- **Especialidades**: 8 especialidades pediátricas
- **Destaque**: Hospital especializado em atendimento pediátrico

#### **Hospital Regional Hans Dieter Schmidt**
- **CNES**: 3456789 (fictício)
- **Tipo**: Estadual
- **Capacidade**: 300 leitos (40 UTI, 80 emergência)
- **Especialidades**: 10 especialidades

### 3.2 Métricas Especializadas SUS

#### **KPIs SUS**
- **Ocupação SUS**: Métrica específica para hospitais públicos
- **Taxa de Procedimentos**: 166.7% (1.5x mais que privado)
- **Taxa de Eficiência**: 92.9% (relação altas/admissões)
- **Tempo de Espera**: 45-135 min (maior que privado)

#### **Padrões Sazonais Específicos**
- **Inverno**: +20% ocupação (doenças respiratórias)
- **Verão**: -10% ocupação (menos doenças)
- **Outono**: +5% ocupação (alergias)

---

## 🏗️ 4. Arquitetura Atualizada

### 4.1 Novos Serviços Implementados

#### **CalendarService (`calendar_service.py`)**
```python
def create_calendar_features(start_date, end_date):
    # Features específicas para pronto-socorro:
    # - is_payday: dias 01-05
    # - month_end: últimos 2 dias do mês
    # - is_monday, is_friday: dias específicos
    # - is_winter: sazonalidade brasileira
    # - is_school_holiday: período de férias
```

#### **EnsembleService (`ensemble_service.py`)**
```python
def create_ensemble_forecast(series_id, historical_data, horizon):
    # Combina Prophet (70%) + Naive Semanal (30%)
    # Naive Semanal: valor do mesmo dia da semana anterior
    # Intervalos de confiança conservadores
```

#### **JoinvilleSusService (`joinville_sus_service.py`)**
```python
def get_hospital_sus_data(cnes_id):
    # Dados específicos para hospitais SUS
    # Métricas especializadas para saúde pública
    # Padrões específicos para hospitais públicos
```

#### **RealDataService (`real_data_service.py`)**
```python
def get_external_data(api_type, params):
    # Integração com APIs externas
    # Sistema híbrido com fallback
    # Cache inteligente
```

### 4.2 Novos Endpoints

#### **Treinamento Melhorado**
```
POST /forecast/train-external
```
- **Regressores**: Clima, feriados, calendário
- **Melhorias**: Sazonalidade contida, winsorize aprimorado
- **Backtesting**: Automático com seleção de hiperparâmetros

#### **Previsão Ensemble**
```
POST /forecast/predict-ensemble
```
- **Combinação**: Prophet + Naive Semanal
- **Pesos**: 70% Prophet, 30% Naive
- **Benefício**: Maior robustez em variações abruptas

#### **Dados Reais**
```
GET /real-data/hospitals
GET /real-data/weather/{lat}/{lon}
GET /real-data/covid/{uf}
GET /real-data/holidays/{year}
```

#### **Hospitais SUS**
```
GET /joinville-sus/hospitals
GET /joinville-sus/hospitals/{cnes}/sus-kpis
GET /joinville-sus/summary
GET /joinville-sus/alerts
```

---

## 📊 5. Métricas e Performance

### 5.1 Regressores Implementados

#### **Clima (3 regressores)**
- ✅ `tmax`: Temperatura máxima
- ✅ `tmin`: Temperatura mínima  
- ✅ `precip`: Precipitação (chuva)

#### **Feriados (3 regressores)**
- ✅ `is_holiday`: Feriado nacional
- ✅ `after_holiday`: Efeito rebote pós-feriado
- ✅ `event_impact_factor`: Fator de impacto

#### **Calendário (5 regressores)**
- ✅ `is_payday`: Dias 01-05 (pagamento)
- ✅ `month_end`: Últimos 2 dias do mês
- ✅ `is_monday`: Segunda-feira (pico comum)
- ✅ `is_friday`: Sexta-feira (fim de semana)
- ✅ `is_school_holiday`: Férias escolares

**Total: 11 regressores específicos para pronto-socorro**

### 5.2 Benefícios Esperados

#### **Precisão Melhorada**
- ✅ **Efeito rebote**: Captura picos pós-feriado
- ✅ **Payday**: Considera padrões de pagamento
- ✅ **Clima**: Chuva aumenta traumas, frio aumenta respiratórios
- ✅ **Outliers**: Tratamento mais robusto

#### **Robustez**
- ✅ **Ensemble**: Combina força do Prophet com simplicidade do Naive
- ✅ **Winsorize**: Limita valores extremos
- ✅ **Sazonalidade contida**: Evita picos irreais

#### **Interpretabilidade**
- ✅ **Regressores específicos**: Cada um tem significado claro
- ✅ **Números inteiros**: Mais realista para pronto-socorro
- ✅ **Métricas claras**: sMAPE, MAE, RMSE

---

## 🚀 6. Como Usar o Sistema Atualizado

### 6.1 Instalação e Configuração

#### **Backend**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

#### **Frontend**
```bash
cd frontend
npm install
npm run dev  # Não mais npm start
```

#### **Configuração de APIs Externas**
```bash
# Criar arquivo .env no backend/
OPENWEATHER_API_KEY=sua_chave_aqui
CACHE_TIMEOUT=3600
MAX_CACHE_SIZE=1000
REQUEST_TIMEOUT=30
MAX_RETRIES=3
```

### 6.2 Exemplos de Uso

#### **Treinamento com Melhorias**
```bash
curl -X POST "http://localhost:8000/forecast/train-external" \
  -F "series_id=pronto_socorro_melhorado" \
  -F "latitude=-26.3044" \
  -F "longitude=-48.8456" \
  -F "start=2024-01-01" \
  -F "end=2024-12-31" \
  -F "file=@pronto_socorro_train_ds_y.csv"
```

#### **Previsão Ensemble**
```bash
curl -X POST "http://localhost:8000/forecast/predict-ensemble" \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "pronto_socorro_melhorado",
    "horizon": 14
  }'
```

#### **Dados de Hospitais SUS**
```bash
curl -X GET "http://localhost:8000/joinville-sus/hospitals"
curl -X GET "http://localhost:8000/joinville-sus/summary"
```

---

## 🎯 7. Casos de Uso e Benefícios

### 7.1 Cenários de Melhoria

#### **Cenário: Feriado 07/09 (Independência)**
- **Antes**: Apenas queda no feriado
- **Depois**: Queda no 07/09 + pico no 08/09 (efeito rebote)

#### **Cenário: Fim de Mês**
- **Antes**: Não considerado
- **Depois**: Aumento esperado nos últimos 2 dias do mês

#### **Cenário: Chuva Intensa**
- **Antes**: Não considerado
- **Depois**: Aumento esperado em traumas

#### **Cenário: Variação Abrupta**
- **Antes**: Prophet pode "estourar"
- **Depois**: Ensemble suaviza com Naive Semanal

### 7.2 Benefícios para Diferentes Stakeholders

#### **Para Gestores Hospitalares**
- 📊 Dados reais de ocupação em tempo real
- 🌡️ Fatores externos que impactam demanda
- 🚨 Alertas baseados em dados reais
- 📈 Previsões mais precisas com ensemble

#### **Para Gestores de Saúde Pública**
- 📊 Métricas SUS específicas
- 🌡️ Padrões sazonais para saúde pública
- 🚨 Alertas especializados
- 📈 Análise de tendências

#### **Para Médicos**
- 🏥 Dados em tempo real por setor
- 📊 Acompanhamento de procedimentos
- ⏱️ Tempo de espera otimizado
- 📈 Tendências de ocupação

---

## 🔮 8. Roadmap Futuro

### 8.1 Próximas Integrações
1. **APIs de trânsito**: Impacto na demanda
2. **APIs de eventos**: Festivais, shows
3. **APIs de qualidade do ar**

### 8.2 Machine Learning Avançado
1. **Treinar modelos com dados reais**
2. **Melhorar previsões com fatores externos**
3. **Detecção de anomalias com IA**

### 8.3 Dashboard Avançado
1. **Mapas interativos**
2. **Análise de tendências**
3. **Relatórios automáticos**

---

## 📞 9. Suporte e Documentação

### 9.1 Documentação Técnica
- **`PRONTO_SOCORRO_IMPROVEMENTS.md`**: Detalhes das melhorias
- **`REAL_DATA_INTEGRATION.md`**: Integração com APIs externas
- **`JOINVILLE_SUS_SUMMARY.md`**: Sistema SUS especializado
- **`README.md`**: Guia de instalação e uso

### 9.2 Testes
```bash
# Testar sistema SUS
python test_joinville_sus.py

# Testar APIs de dados reais
curl -X GET "http://localhost:8000/real-data/data-sources/status"
```

### 9.3 Contato
- **Repositório**: HospiCast Prophet Starter
- **Documentação**: Disponível no diretório `portif-lio/`
- **Issues**: Reportar problemas via repositório

---

## ✅ 10. Qualidade Técnica do Código

1. **Estrutura e Modularização**
   - Backend dividido em `routers/`, `services/`, `schemas/`, `core/` e `models/`, garantindo acoplamento baixo.
   - Frontend em React com componentes especializados (`components/JoinvilleSusPanel`, etc.) e separação de estilos (`index.css`).
2. **Boas Práticas**
   - Linters configurados: `ruff` (Python) e `eslint` (React) via scripts (`ruff check backend`, `npm run lint`).
   - Padrão de logs estruturados em `backend/core/logging.py`, com níveis controlados por `LOG_LEVEL`.
3. **Testes Automatizados**
   - Backend: suíte `pytest` em `backend/tests` cobrindo serviços críticos (ex.: geração de alertas SUS).
   - Frontend: `vitest` + Testing Library garantindo renderização do `App` e interações principais.
4. **Histórico de Commits**
   - Commits frequentes, mensagens no formato `<tipo>: <descrição>` e referência a issues PAC 8 (ver histórico Git).

---

## ⚙️ 11. Infraestrutura e Engenharia

1. **Versionamento**
   - Fluxo Git documentado em `ENGINEERING_GUIDE.md` (`main`, `develop`, `feature/*`, `hotfix/*`) e issues para cada entrega.
2. **CI/CD**
   - Pipeline GitHub Actions (`.github/workflows/ci.yml`) executa lint + testes backend/frontend em push e PR.
   - Deploy via Docker/Compose (`docker-compose*.yml`) ou scripts (`deploy.sh`) em Railway/Render.
3. **Monitoramento e Observabilidade**
   - Endpoint `/metrics` habilitado pelo `prometheus-fastapi-instrumentator` para integração com Prometheus/Grafana.
   - Logs estruturados prontos para coletores como Logtail, CloudWatch ou Railway Insights.
4. **Segurança**
   - Variáveis sensíveis isoladas em `.env` (modelo em `env.example`), CORS configurável (`API_ALLOWED_ORIGINS`) e TLS na infraestrutura.
5. **Práticas DevOps**
   - Scripts `start_hospicast.py`, `deploy.sh`, Dockerfiles e compose garantem ambientes reproduzíveis e rollback rápido.

---

## 🧠 11.1 Fluxo autenticado de hospitais

- **Cadastro protegido** (`POST /hospital-access/register`): cada instituição define senha própria, recebe `hospital_id` e `short_code`.
- **Sessão reutilizável** (`POST /hospital-access/login`): emite token de 12h para consultar histórico e gerar novas previsões.
- **Persistência das previsões**: toda chamada autenticada a `/forecast/predict` salva o payload completo em `hospital_forecasts`, permitindo que a IA use o histórico para ajustes futuros.
- **Consulta de histórico** (`GET /hospital-access/{hospital_id}/forecasts`): entregue ao frontend para exibir rapidamente as últimas previsões e métricas agregadas.
- **Frontend guiado**: tela inicial oferece “Cadastrar novo hospital” ou “Buscar hospital existente”, solicita senha e mostra o painel de histórico após autenticação.

---

## ✅ 12. Conclusão

O HospiCast Versão 2.0 representa uma evolução significativa do sistema de previsão de demanda hospitalar, incorporando:

1. **Melhorias específicas para pronto-socorro** com 11 regressores especializados
2. **Integração com dados reais** através de APIs externas brasileiras
3. **Sistema especializado para hospitais SUS** com métricas específicas
4. **Arquitetura híbrida inteligente** com fallback automático
5. **Ensemble de modelos** para maior robustez

O sistema agora oferece previsões mais precisas, robustas e interpretáveis, atendendo às demandas reais do setor de saúde brasileiro.

---

**🎉 HospiCast 2.0 - Sistema de Previsão Hospitalar Avançado com Dados Reais!**

**📅 Janeiro 2025 - Versão Atualizada e Funcional**


