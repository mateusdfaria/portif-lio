# HospiCast PowerShell Script - Guia de Uso

## Visão Geral

O script `hospicast.ps1` é uma ferramenta PowerShell que facilita o uso da API do HospiCast, permitindo treinar modelos, fazer previsões e gerenciar dados de forma simples e intuitiva.

## Pré-requisitos

1. **Backend rodando**: Certifique-se de que o backend está funcionando em `http://localhost:8000`
2. **PowerShell**: O script funciona no PowerShell 5.1+ (Windows 10/11)
3. **Arquivo CSV**: Tenha o arquivo de dados disponível (padrão: `hospicast_train_ds_y.csv`)

## Como Executar

### 1. Verificar Status da API
```powershell
.\hospicast.ps1 -Action status
```

### 2. Ver Ajuda
```powershell
.\hospicast.ps1 -Action help
```

### 3. Listar Modelos Disponíveis
```powershell
.\hospicast.ps1 -Action models
```

## Treinamento de Modelos

### Treino Simples (sem regressores externos)
```powershell
.\hospicast.ps1 -Action train -SeriesId meu_hospital -CsvFile "caminho/para/dados.csv"
```

**Parâmetros:**
- `-SeriesId`: Nome único para identificar o modelo
- `-CsvFile`: Caminho para o arquivo CSV com colunas `ds` (data) e `y` (valor)

### Treino com Clima e Feriados
```powershell
.\hospicast.ps1 -Action train-external -SeriesId hosp_joinville_ps -Latitude -26.3044 -Longitude -48.8487 -StartDate 2025-08-01 -EndDate 2025-08-27
```

**Parâmetros:**
- `-SeriesId`: Nome único para identificar o modelo
- `-Latitude`: Latitude da localização (para dados climáticos)
- `-Longitude`: Longitude da localização (para dados climáticos)
- `-StartDate`: Data inicial do período de treino (YYYY-MM-DD)
- `-EndDate`: Data final do período de treino (YYYY-MM-DD)
- `-CsvFile`: Caminho para o arquivo CSV (opcional, usa padrão se não especificado)

## Geração de Previsões

### Previsão Simples
```powershell
.\hospicast.ps1 -Action predict -SeriesId hosp_joinville_ps -Horizon 14
```

**Parâmetros:**
- `-SeriesId`: ID do modelo treinado
- `-Horizon`: Número de dias para prever (padrão: 14)

### Previsão com Clima e Feriados
```powershell
.\hospicast.ps1 -Action predict-climate -SeriesId hosp_joinville_ps -Horizon 30 -Latitude -26.3044 -Longitude -48.8487
```

**Parâmetros:**
- `-SeriesId`: ID do modelo treinado
- `-Horizon`: Número de dias para prever
- `-Latitude`: Latitude da localização
- `-Longitude`: Longitude da localização

## Exemplos Práticos

### 1. Treinar Modelo para Joinville
```powershell
.\hospicast.ps1 -Action train-external -SeriesId joinville_ps -Latitude -26.3044 -Longitude -48.8487 -StartDate 2025-08-01 -EndDate 2025-08-27
```

### 2. Fazer Previsão para 30 Dias
```powershell
.\hospicast.ps1 -Action predict -SeriesId joinville_ps -Horizon 30
```

### 3. Previsão com Clima para Blumenau
```powershell
.\hospicast.ps1 -Action predict-climate -SeriesId blumenau_ps -Horizon 21 -Latitude -26.9186 -Longitude -49.0661
```

## Saídas e Resultados

### Arquivos Gerados
- **Previsões**: Salvas automaticamente em arquivos JSON com timestamp
- **Formato**: `previsao_[series_id]_[timestamp].json`
- **Conteúdo**: Dados completos da previsão com intervalos de confiança

### Resumo na Tela
- Média prevista de pacientes por dia
- Pico previsto (valor máximo)
- Valor mínimo previsto
- Status da operação

## Parâmetros Padrão

Se não especificados, o script usa estes valores padrão:
- `SeriesId`: `hosp_joinville_ps`
- `Horizon`: `14` dias
- `Latitude`: `-26.3044` (Joinville)
- `Longitude`: `-48.8487` (Joinville)
- `StartDate`: `2025-08-01`
- `EndDate`: `2025-08-27`
- `CsvFile`: `C:\Users\mateus.si\Downloads\hospicast_train_ds_y.csv`

## Solução de Problemas

### Erro: "API não está respondendo"
1. Verifique se o backend está rodando
2. Execute: `cd backend && .\.venv\Scripts\python.exe -m uvicorn main:app --reload`

### Erro: "Arquivo CSV não encontrado"
1. Verifique o caminho do arquivo
2. Use o parâmetro `-CsvFile` para especificar o caminho correto

### Erro: "Modelo não encontrado"
1. Verifique se o modelo foi treinado: `.\hospicast.ps1 -Action models`
2. Treine o modelo primeiro usando `-Action train` ou `-Action train-external`

## Integrações Externas

### Dados Climáticos
- **Fonte**: Open-Meteo (gratuito, sem API key)
- **Dados**: Temperatura máxima, mínima e precipitação
- **Cobertura**: Dados históricos para treino

### Feriados
- **Fonte**: BrasilAPI
- **Dados**: Feriados nacionais brasileiros
- **Uso**: Regressor binário (0 = dia normal, 1 = feriado)

## Estrutura do CSV

O arquivo CSV deve conter:
```csv
ds,y
2025-08-01,23
2025-08-02,15
2025-08-03,25
...
```

- `ds`: Data no formato YYYY-MM-DD
- `y`: Valor numérico (número de pacientes, ocupação, etc.)

## Comandos Rápidos

```powershell
# Verificar tudo
.\hospicast.ps1 -Action status
.\hospicast.ps1 -Action models

# Treinar e prever
.\hospicast.ps1 -Action train-external
.\hospicast.ps1 -Action predict

# Previsão personalizada
.\hospicast.ps1 -Action predict -Horizon 30
```

## Suporte

Para problemas ou dúvidas:
1. Verifique se o backend está funcionando
2. Use `-Action help` para ver todas as opções
3. Verifique os logs do backend para erros detalhados




