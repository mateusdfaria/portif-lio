# HospiCast PowerShell Script
# Script para facilitar o uso dos comandos do HospiCast

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "help",
    
    [Parameter(Mandatory=$false)]
    [string]$SeriesId = "hosp_joinville_ps",
    
    [Parameter(Mandatory=$false)]
    [int]$Horizon = 14,
    
    [Parameter(Mandatory=$false)]
    [string]$Latitude = "-26.3044",
    
    [Parameter(Mandatory=$false)]
    [string]$Longitude = "-48.8487",
    
    [Parameter(Mandatory=$false)]
    [string]$StartDate = "2025-08-01",
    
    [Parameter(Mandatory=$false)]
    [string]$EndDate = "2025-08-27",
    
    [Parameter(Mandatory=$false)]
    [string]$CsvFile = "C:\Users\mateus.si\Downloads\hospicast_train_ds_y.csv"
)

# Funcao para mostrar ajuda
function Show-Help {
    Write-Host "=== HospiCast PowerShell Script ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Uso:" -ForegroundColor Yellow
    Write-Host "  .\hospicast.ps1 -Action <acao> [parametros]" -ForegroundColor White
    Write-Host ""
    Write-Host "Acoes disponiveis:" -ForegroundColor Yellow
    Write-Host "  help          - Mostra esta ajuda" -ForegroundColor White
    Write-Host "  train         - Treina modelo simples" -ForegroundColor White
    Write-Host "  train-external - Treina com clima e feriados" -ForegroundColor White
    Write-Host "  predict       - Faz previsao" -ForegroundColor White
    Write-Host "  predict-climate - Previsao com clima e feriados" -ForegroundColor White
    Write-Host "  models        - Lista modelos disponiveis" -ForegroundColor White
    Write-Host "  status        - Verifica status da API" -ForegroundColor White
    Write-Host ""
    Write-Host "Exemplos:" -ForegroundColor Yellow
    Write-Host "  .\hospicast.ps1 -Action train-external" -ForegroundColor White
    Write-Host "  .\hospicast.ps1 -Action predict -SeriesId hosp_joinville_ps -Horizon 30" -ForegroundColor White
    Write-Host "  .\hospicast.ps1 -Action predict-climate -Latitude -26.3044 -Longitude -48.8487" -ForegroundColor White
    Write-Host ""
    Write-Host "Parametros:" -ForegroundColor Yellow
    Write-Host "  -SeriesId     - ID da serie (padrao: hosp_joinville_ps)" -ForegroundColor White
    Write-Host "  -Horizon      - Horizonte de previsao em dias (padrao: 14)" -ForegroundColor White
    Write-Host "  -Latitude     - Latitude para dados climaticos" -ForegroundColor White
    Write-Host "  -Longitude    - Longitude para dados climaticos" -ForegroundColor White
    Write-Host "  -StartDate    - Data inicial para treino (YYYY-MM-DD)" -ForegroundColor White
    Write-Host "  -EndDate      - Data final para treino (YYYY-MM-DD)" -ForegroundColor White
    Write-Host "  -CsvFile      - Caminho para arquivo CSV" -ForegroundColor White
}

# Funcao para verificar status da API
function Test-APIStatus {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method GET
        Write-Host "API esta funcionando: $($response.message)" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "API nao esta respondendo. Verifique se o backend esta rodando." -ForegroundColor Red
        Write-Host "Execute: cd backend && .\.venv\Scripts\python.exe -m uvicorn main:app --reload" -ForegroundColor Yellow
        return $false
    }
}

# Funcao para treinar modelo simples
function Train-SimpleModel {
    param($SeriesId, $CsvFile)
    
    if (-not (Test-Path $CsvFile)) {
        Write-Host "Arquivo CSV nao encontrado: $CsvFile" -ForegroundColor Red
        return
    }
    
    try {
        Write-Host "Treinando modelo simples..." -ForegroundColor Cyan
        
        $Form = @{
            series_id = $SeriesId
            file = Get-Item $CsvFden
        }
        
        $response = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/forecast/train-file" -Form $Form
        Write-Host "Modelo treinado com sucesso!" -ForegroundColor Green
        Write-Host "   Series ID: $($response.series_id)" -ForegroundColor White
        Write-Host "   Status: $($response.status)" -ForegroundColor White
    }
    catch {
        Write-Host "Erro ao treinar modelo: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Funcao para treinar com clima e feriados
function Train-ExternalModel {
    param($SeriesId, $Latitude, $Longitude, $StartDate, $EndDate, $CsvFile)
    
    if (-not (Test-Path $CsvFile)) {
        Write-Host "Arquivo CSV nao encontrado: $CsvFile" -ForegroundColor Red
        return
    }
    
    try {
        Write-Host "Treinando modelo com clima e feriados..." -ForegroundColor Cyan
        Write-Host "   Coordenadas: $Latitude, $Longitude" -ForegroundColor White
        Write-Host "   Periodo: $StartDate a $EndDate" -ForegroundColor White
        
        $Form = @{
            series_id = $SeriesId
            latitude = $Latitude
            longitude = $Longitude
            start = $StartDate
            end = $EndDate
            file = Get-Item $CsvFile
        }
        
        $response = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/forecast/train-external" -Form $Form
        Write-Host "Modelo treinado com sucesso!" -ForegroundColor Green
        Write-Host "   Series ID: $($response.series_id)" -ForegroundColor White
        Write-Host "   Regressores: $($response.regressors -join ', ')" -ForegroundColor White
    }
    catch {
        Write-Host "Erro ao treinar modelo: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Funcao para fazer previsao
function Get-Prediction {
    param($SeriesId, $Horizon)
    
    try {
        Write-Host "Gerando previsao..." -ForegroundColor Cyan
        Write-Host "   Series ID: $SeriesId" -ForegroundColor White
        Write-Host "   Horizonte: $Horizon dias" -ForegroundColor White
        
        $body = @{
            series_id = $SeriesId
            horizon = $Horizon
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/forecast/predict" -ContentType "application/json" -Body $body
        
        Write-Host "Previsao gerada com sucesso!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Resumo da previsao:" -ForegroundColor Yellow
        Write-Host "   Media prevista: $([math]::Round(($response.forecast.yhat | Measure-Object -Average).Average, 2)) pacientes/dia" -ForegroundColor White
        Write-Host "   Pico previsto: $([math]::Round(($response.forecast.yhat | Measure-Object -Maximum).Maximum, 2)) pacientes" -ForegroundColor White
        Write-Host "   Minimo previsto: $([math]::Round(($response.forecast.yhat | Measure-Object -Minimum).Minimum, 2)) pacientes" -ForegroundColor White
        
        # Salvar resultado em arquivo
        $outputFile = "previsao_${SeriesId}_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
        $response | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputFile -Encoding UTF8
        Write-Host "Resultado salvo em: $outputFile" -ForegroundColor Cyan
        
        return $response
    }
    catch {
        Write-Host "Erro ao gerar previsao: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Funcao para previsao com clima e feriados
function Get-PredictionWithClimate {
    param($SeriesId, $Horizon, $Latitude, $Longitude)
    
    try {
        Write-Host "Gerando previsao com clima e feriados..." -ForegroundColor Cyan
        Write-Host "   Series ID: $SeriesId" -ForegroundColor White
        Write-Host "   Horizonte: $Horizon dias" -ForegroundColor White
        Write-Host "   Coordenadas: $Latitude, $Longitude" -ForegroundColor White
        
        $body = @{
            series_id = $SeriesId
            horizon = $Horizon
            latitude = [double]$Latitude
            longitude = [double]$Longitude
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/forecast/predict" -ContentType "application/json" -Body $body
        
        Write-Host "Previsao com clima gerada com sucesso!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Resumo da previsao:" -ForegroundColor Yellow
        Write-Host "   Media prevista: $([math]::Round(($response.forecast.yhat | Measure-Object -Average).Average, 2)) pacientes/dia" -ForegroundColor White
        Write-Host "   Pico previsto: $([math]::Round(($response.forecast.yhat | Measure-Object -Maximum).Maximum, 2)) pacientes" -ForegroundColor White
        Write-Host "   Minimo previsto: $([math]::Round(($response.forecast.yhat | Measure-Object -Minimum).Minimum, 2)) pacientes" -ForegroundColor White
        
        # Salvar resultado em arquivo
        $outputFile = "previsao_clima_${SeriesId}_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
        $response | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputFile -Encoding UTF8
        Write-Host "Resultado salvo em: $outputFile" -ForegroundColor Cyan
        
        return $response
    }
    catch {
        Write-Host "Erro ao gerar previsao: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Funcao para listar modelos
function Get-Models {
    try {
        Write-Host "Listando modelos disponiveis..." -ForegroundColor Cyan
        
        $response = Invoke-RestMethod -Method GET -Uri "http://localhost:8000/forecast/models"
        
        Write-Host "Modelos encontrados:" -ForegroundColor Green
        foreach ($model in $response.models) {
            Write-Host "   $model" -ForegroundColor White
        }
    }
    catch {
        Write-Host "Erro ao listar modelos: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Execucao principal
Write-Host "HospiCast PowerShell Script" -ForegroundColor Cyan
Write-Host ""

switch ($Action.ToLower()) {
    "help" {
        Show-Help
    }
    "status" {
        Test-APIStatus
    }
    "train" {
        if (Test-APIStatus) {
            Train-SimpleModel -SeriesId $SeriesId -CsvFile $CsvFile
        }
    }
    "train-external" {
        if (Test-APIStatus) {
            Train-ExternalModel -SeriesId $SeriesId -Latitude $Latitude -Longitude $Longitude -StartDate $StartDate -EndDate $EndDate -CsvFile $CsvFile
        }
    }
    "predict" {
        if (Test-APIStatus) {
            Get-Prediction -SeriesId $SeriesId -Horizon $Horizon
        }
    }
    "predict-climate" {
        if (Test-APIStatus) {
            Get-PredictionWithClimate -SeriesId $SeriesId -Horizon $Horizon -Latitude $Latitude -Longitude $Longitude
        }
    }
    "models" {
        if (Test-APIStatus) {
            Get-Models
        }
    }
    default {
        Write-Host "Acao '$Action' nao reconhecida." -ForegroundColor Red
        Show-Help
    }
}
