# 📊 Guia Completo: Arquivos de Teste Comparativo e Real

Este guia explica como usar os arquivos `teste_comparativo_2022.csv` e `real.csv` para testar as funcionalidades de previsão e comparação do HospiCast.

---

## 📁 Arquivos Disponíveis

### 1. `teste_comparativo_2022.csv`

**Descrição**: Arquivo com dados históricos de demanda hospitalar para treinamento de modelos e geração de previsões.

**Formato:**
```csv
ds;y
2021-01-01;102
2021-01-02;115
2021-01-03;127
...
```

**Características:**
- **Colunas**: `ds` (data) e `y` (valor)
- **Separador**: `;` (ponto e vírgula)
- **Período**: Dados históricos de 2021-2022
- **Uso**: Treinar modelos e gerar previsões futuras

### 2. `real.csv`

**Descrição**: Arquivo com valores reais de demanda hospitalar para comparar com as previsões geradas.

**Formato:**
```csv
ds;y
2025-11-01;146
2025-11-02;167
2025-11-03;252
...
```

**Características:**
- **Colunas**: `ds` (data) e `y` (valor real)
- **Separador**: `;` (ponto e vírgula)
- **Período**: Valores reais para o período previsto
- **Uso**: Comparar previsões com dados reais

---

## 🔄 Fluxo Completo de Uso

### Passo 1: Treinar Modelo com Dados Históricos

Use o arquivo `teste_comparativo_2022.csv` para treinar um modelo de previsão.

#### Via API REST

```bash
curl -X POST "http://127.0.0.1:8001/forecast/train-external" \
  -F "series_id=hospital_joinville_2022" \
  -F "latitude=-26.3044" \
  -F "longitude=-48.8464" \
  -F "start=2021-01-01" \
  -F "end=2022-12-31" \
  -F "file=@teste_comparativo_2022.csv"
```

**Resposta:**
```json
{
  "status": "ok",
  "series_id": "hospital_joinville_2022",
  "regressors": [...],
  "improvements": [...]
}
```

**⚠️ Importante**: Anote o `series_id` retornado! Você precisará dele nos próximos passos.

#### Via Interface Web

1. Acesse `http://localhost:5173`
2. Navegue até a seção **Treinamento de Modelos**
3. Faça upload do arquivo `teste_comparativo_2022.csv`
4. Configure:
   - **Series ID**: Um identificador único (ex: `hospital_joinville_2022`)
   - **Latitude**: `-26.3044` (exemplo para Joinville)
   - **Longitude**: `-48.8464` (exemplo para Joinville)
   - **Data Inicial**: `2021-01-01`
   - **Data Final**: `2022-12-31`
5. Clique em **Treinar Modelo**
6. **Copie o `series_id` retornado**

---

### Passo 2: Gerar Previsão

Use o `series_id` obtido no Passo 1 para gerar previsões futuras.

#### Via API REST

```bash
curl -X POST "http://127.0.0.1:8001/forecast/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "hospital_joinville_2022",
    "horizon": 14,
    "latitude": -26.3044,
    "longitude": -48.8464
  }'
```

**Resposta:**
```json
{
  "forecast": [
    {
      "ds": "2025-11-01",
      "yhat": 150.5,
      "yhat_lower": 120.3,
      "yhat_upper": 180.7
    },
    ...
  ],
  "insights": [...],
  "series_id": "hospital_joinville_2022"
}
```

**⚠️ Importante**: 
- Anote as **datas** das previsões geradas (ex: `2025-11-01` a `2025-11-14`)
- O `series_id` será usado no próximo passo

#### Via Interface Web

1. Acesse a seção **Previsão**
2. Informe o `series_id` do modelo treinado
3. Configure:
   - **Horizonte**: Número de dias a prever (ex: `14`)
   - **Latitude**: `-26.3044`
   - **Longitude**: `-48.8464`
4. Clique em **Gerar Previsão**
5. **Anote as datas das previsões geradas**

---

### Passo 3: Comparar com Valores Reais

Use o arquivo `real.csv` junto com o `series_id` e as datas das previsões para comparar os resultados.

#### Via API REST

```bash
curl -X POST "http://127.0.0.1:8001/forecast/compare-predictions" \
  -F "series_id=hospital_joinville_2022" \
  -F "file=@real.csv" \
  -F "start_date=2025-11-01" \
  -F "end_date=2025-11-14"
```

**Resposta:**
```json
{
  "comparison_data": [
    {
      "ds": "2025-11-01",
      "actual": 146,
      "predicted": 150.5,
      "predicted_lower": 120.3,
      "predicted_upper": 180.7,
      "error": -4.5,
      "absolute_error": 4.5,
      "percentage_error": -3.08
    },
    ...
  ],
  "metrics": {
    "mae": 12.3,
    "rmse": 15.7,
    "mape": 8.5,
    "smape": 8.2
  },
  "series_id": "hospital_joinville_2022"
}
```

#### Via Interface Web

1. Acesse a seção **Comparação de Previsões**
2. Informe o `series_id` usado na previsão (ex: `hospital_joinville_2022`)
3. Faça upload do arquivo `real.csv`
4. (Opcional) Configure as datas:
   - **Data Inicial**: `2025-11-01` (primeira data prevista)
   - **Data Final**: `2025-11-14` (última data prevista)
5. Clique em **Comparar**
6. Visualize os gráficos e métricas de comparação

---

## 📋 Requisitos dos Arquivos CSV

### Formato Obrigatório

Ambos os arquivos devem seguir este formato:

```csv
ds;y
2021-01-01;102
2021-01-02;115
2021-01-03;127
```

### Colunas

- **`ds`** (obrigatório): Data no formato `YYYY-MM-DD`
- **`y`** (obrigatório): Valor numérico (ex: número de pacientes)

### Separadores Suportados

- `;` (ponto e vírgula) - **Recomendado**
- `,` (vírgula)

### Encoding

- **UTF-8** (recomendado)
- **ISO-8859-1** (Latin-1)
- **Windows-1252**

---

## ⚠️ Regras Importantes

### 1. Correspondência de Datas

O arquivo `real.csv` deve conter valores reais para as **mesmas datas** das previsões geradas.

**Exemplo:**
- Se a previsão foi gerada para `2025-11-01` a `2025-11-14`
- O `real.csv` deve ter valores reais para essas mesmas datas

### 2. Series ID

- O `series_id` é criado automaticamente quando você treina um modelo
- Use o **mesmo `series_id`** para:
  - Gerar previsões (Passo 2)
  - Comparar com dados reais (Passo 3)

### 3. Ordem dos Passos

Siga a ordem correta:

1. ✅ **Treinar** modelo com `teste_comparativo_2022.csv`
2. ✅ **Gerar** previsão usando o `series_id`
3. ✅ **Comparar** usando `real.csv` com o mesmo `series_id`

---

## 🔍 Exemplo Prático Completo

### Cenário: Prever demanda para os próximos 14 dias

```bash
# 1. Treinar modelo
curl -X POST "http://127.0.0.1:8001/forecast/train-external" \
  -F "series_id=meu_teste" \
  -F "latitude=-26.3044" \
  -F "longitude=-48.8464" \
  -F "start=2021-01-01" \
  -F "end=2022-12-31" \
  -F "file=@teste_comparativo_2022.csv"

# Resposta: {"status": "ok", "series_id": "meu_teste"}

# 2. Gerar previsão para 14 dias
curl -X POST "http://127.0.0.1:8001/forecast/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "meu_teste",
    "horizon": 14,
    "latitude": -26.3044,
    "longitude": -48.8464
  }'

# Resposta: {
#   "forecast": [
#     {"ds": "2025-11-01", "yhat": 150.5, ...},
#     {"ds": "2025-11-02", "yhat": 152.3, ...},
#     ...
#     {"ds": "2025-11-14", "yhat": 148.9, ...}
#   ],
#   "series_id": "meu_teste"
# }

# 3. Comparar com valores reais
curl -X POST "http://127.0.0.1:8001/forecast/compare-predictions" \
  -F "series_id=meu_teste" \
  -F "file=@real.csv" \
  -F "start_date=2025-11-01" \
  -F "end_date=2025-11-14"

# Resposta: {
#   "comparison_data": [
#     {
#       "ds": "2025-11-01",
#       "actual": 146,
#       "predicted": 150.5,
#       "error": -4.5,
#       ...
#     },
#     ...
#   ],
#   "metrics": {
#     "mae": 12.3,
#     "rmse": 15.7,
#     "mape": 8.5,
#     "smape": 8.2
#   }
# }
```

---

## 🐛 Troubleshooting

### Erro: "Modelo não encontrado"

**Causa**: O `series_id` não existe ou foi digitado incorretamente.

**Solução**: 
1. Verifique se treinou o modelo primeiro
2. Use o `series_id` exato retornado no treinamento
3. Liste modelos disponíveis: `GET /forecast/models`

### Erro: "CSV deve conter colunas 'ds' e 'y'"

**Causa**: Formato do arquivo CSV incorreto.

**Solução**:
1. Verifique se as colunas estão nomeadas como `ds` e `y`
2. Verifique se o separador está correto (`;` ou `,`)
3. Verifique se não há espaços extras nos nomes das colunas

### Erro: "Nenhum dado encontrado no período especificado"

**Causa**: As datas no `real.csv` não correspondem às datas das previsões.

**Solução**:
1. Verifique as datas das previsões geradas
2. Certifique-se de que o `real.csv` contém valores para essas mesmas datas
3. Use os parâmetros `start_date` e `end_date` para filtrar o período correto

### Erro: "Arquivo vazio"

**Causa**: O arquivo CSV está vazio ou corrompido.

**Solução**:
1. Verifique se o arquivo não está vazio
2. Verifique se o arquivo foi salvo corretamente
3. Tente abrir o arquivo em um editor de texto para verificar o conteúdo

---

## 📚 Referências

- [Documentação da API](/docs) - Endpoints completos
- [README.md](../README.md) - Visão geral do projeto
- [Swagger UI](http://127.0.0.1:8001/docs) - Documentação interativa da API

---

**✅ Pronto! Agora você sabe como usar os arquivos de teste para validar as previsões do HospiCast.**

