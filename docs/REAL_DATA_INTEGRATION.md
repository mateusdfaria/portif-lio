# 🌐 Integração com Dados Reais - HospiCast

Este documento explica como o HospiCast foi integrado com APIs reais de dados hospitalares brasileiros.

## 📊 APIs Integradas

### 1. **CNES (Cadastro Nacional de Estabelecimentos de Saúde)**
- **Fonte**: Datasus
- **Endpoint**: `https://cnes.datasus.gov.br/services/estabelecimentos`
- **Dados**: Informações de hospitais, capacidades, especialidades
- **Uso**: Lista de hospitais reais brasileiros

### 2. **SIH (Sistema de Informações Hospitalares)**
- **Fonte**: Datasus
- **Endpoint**: `https://sih.datasus.gov.br/services/ocupacao`
- **Dados**: Ocupação de leitos, admissões, altas
- **Uso**: Métricas de ocupação em tempo real

### 3. **BrasilAPI**
- **Fonte**: API pública brasileira
- **Endpoints**: 
  - `https://brasilapi.com.br/api/feriados/v1/{year}`
  - `https://brasilapi.com.br/api/covid19/v1`
- **Dados**: Feriados nacionais, dados de COVID-19
- **Uso**: Fatores externos que impactam demanda

### 4. **OpenWeatherMap**
- **Fonte**: API meteorológica internacional
- **Endpoint**: `https://api.openweathermap.org/data/2.5/weather`
- **Dados**: Temperatura, umidade, condições climáticas
- **Uso**: Impacto do clima na demanda hospitalar

## 🔧 Configuração

### 1. **Variáveis de Ambiente**
Crie um arquivo `.env` no diretório `backend/`:

```bash
# OpenWeatherMap API Key
OPENWEATHER_API_KEY=sua_chave_aqui

# Configurações de Cache
CACHE_TIMEOUT=3600
MAX_CACHE_SIZE=1000

# Configurações de Timeout
REQUEST_TIMEOUT=30
MAX_RETRIES=3
```

### 2. **Obter Chave da OpenWeatherMap**
1. Acesse: https://openweathermap.org/api
2. Crie uma conta gratuita
3. Gere uma API key
4. Adicione no arquivo `.env`

## 🚀 Como Usar

### 1. **Endpoints Disponíveis**

#### **Hospitais com Dados Reais**
```bash
GET /real-data/hospitals?uf=SC&municipio=Joinville&use_real_data=true
```

#### **KPIs Enriquecidos**
```bash
GET /real-data/hospitals/{hospital_id}/enhanced-kpis?start_date=2024-01-01&end_date=2024-01-31
```

#### **Dados Meteorológicos**
```bash
GET /real-data/weather/{latitude}/{longitude}?date=2024-01-15
```

#### **Dados de COVID-19**
```bash
GET /real-data/covid/SC
```

#### **Feriados**
```bash
GET /real-data/holidays/2024?uf=SC
```

#### **Status das APIs**
```bash
GET /real-data/data-sources/status
```

### 2. **Alternar entre Dados Reais e Simulados**
```bash
POST /real-data/config/use-real-data?use_real_data=true
```

### 3. **Limpar Cache**
```bash
GET /real-data/cache/clear
```

## 📱 Interface do Usuário

### **Painel de Dados Reais**
O Dashboard agora inclui um painel que mostra:

- **Status das APIs**: Conectividade com cada fonte de dados
- **Dados Meteorológicos**: Temperatura, umidade, condições climáticas
- **Dados de COVID-19**: Casos confirmados, recuperados, óbitos por UF
- **Feriados**: Próximos feriados que podem impactar a demanda
- **Toggle**: Alternar entre dados reais e simulados

### **Indicadores Visuais**
- 🟢 **Verde**: API funcionando perfeitamente
- 🔵 **Azul**: API funcionando com limitações
- 🟡 **Amarelo**: API com problemas
- 🔴 **Vermelho**: API offline

## 🔄 Sistema Híbrido

O HospiCast usa um sistema híbrido inteligente:

### **Fallback Automático**
- Se APIs reais falharem, usa dados simulados
- Cache inteligente para evitar muitas requisições
- Retry automático com backoff exponencial

### **Dados Enriquecidos**
- Combina dados reais com fatores externos
- Calcula impacto de clima, COVID-19 e feriados
- Gera alertas baseados em dados reais

## 📊 Exemplo de Resposta

### **KPIs Enriquecidos**
```json
{
  "status": "ok",
  "hospital_id": "real_1234567",
  "hospital_name": "Hospital Municipal São José",
  "period": "2024-01-01 a 2024-01-31",
  "kpis": {
    "avg_occupancy_rate": 75.2,
    "avg_emergency_occupancy": 82.1,
    "avg_icu_occupancy": 68.5,
    "avg_wait_time": 45.3,
    "total_admissions": 1250,
    "total_discharges": 1180
  },
  "external_factors": {
    "temperature_impact": 5.2,
    "covid_impact": 12.8,
    "holiday_impact": 3.1,
    "total_impact": 21.1,
    "impact_level": "high"
  },
  "weather_data": {
    "temperatura": 28.5,
    "umidade": 65,
    "descricao": "céu limpo"
  },
  "covid_data": {
    "casos_confirmados": 15420,
    "casos_recuperados": 14200,
    "obitos": 89
  },
  "data_source": "real",
  "last_updated": "2024-01-15 14:30:00"
}
```

## 🛠️ Desenvolvimento

### **Estrutura de Arquivos**
```
backend/
├── services/
│   ├── real_data_service.py      # Serviço de APIs externas
│   ├── hybrid_hospital_service.py # Serviço híbrido
│   └── hospital_service.py        # Serviço original
├── routers/
│   └── real_data.py              # Endpoints de dados reais
├── config/
│   └── api_config.py            # Configuração das APIs
└── env.example                  # Exemplo de variáveis

frontend/src/components/
└── RealDataPanel.jsx           # Painel de dados reais
```

### **Adicionando Novas APIs**
1. Adicione a configuração em `api_config.py`
2. Implemente o método em `real_data_service.py`
3. Crie endpoint em `real_data.py`
4. Atualize o frontend se necessário

## 🔒 Segurança e Limitações

### **Rate Limiting**
- Cache de 1 hora para evitar muitas requisições
- Timeout de 30 segundos por requisição
- Máximo de 3 tentativas com backoff

### **Dados Sensíveis**
- APIs públicas não expõem dados de pacientes
- Apenas dados agregados e anonimizados
- Conformidade com LGPD

### **Limitações**
- Algumas APIs podem ter limites de uso
- Dados podem ter delay de atualização
- Dependência de conectividade externa

## 🎯 Benefícios

### **Para Gestores Hospitalares**
- Dados reais de ocupação em tempo real
- Fatores externos que impactam demanda
- Alertas baseados em dados reais

### **Para Desenvolvedores**
- Sistema híbrido robusto
- Fallback automático
- APIs bem documentadas

### **Para Pesquisadores**
- Dados reais para análise
- Integração com múltiplas fontes
- Métricas de qualidade dos dados

## 🚀 Próximos Passos

1. **Integração com mais APIs**
   - APIs de trânsito (impacto na demanda)
   - APIs de eventos (festivais, shows)
   - APIs de qualidade do ar

2. **Machine Learning**
   - Treinar modelos com dados reais
   - Melhorar previsões com fatores externos
   - Detecção de anomalias

3. **Dashboard Avançado**
   - Mapas interativos
   - Análise de tendências
   - Relatórios automáticos

---

**🎉 O HospiCast agora está integrado com dados reais brasileiros!**
