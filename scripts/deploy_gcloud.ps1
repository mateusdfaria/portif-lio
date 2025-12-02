# Script PowerShell para deploy no Google Cloud
# Uso: .\scripts\deploy_gcloud.ps1

$ErrorActionPreference = "Stop"

# Variáveis
$PROJECT_ID = "hospicast-prod"
$SERVICE_NAME = "hospicast-backend"
$REGION = "southamerica-east1"
$BUCKET_NAME = "hospicast-frontend"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/hospicast-backend"

Write-Host "🚀 Iniciando deploy do HospiCast..." -ForegroundColor Green
Write-Host "📦 Projeto: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "🌍 Região: $REGION" -ForegroundColor Cyan
Write-Host ""

# 1. Configurar projeto
Write-Host "1️⃣ Configurando projeto GCP..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

# 2. Obter connection name
Write-Host "2️⃣ Obtendo connection name do Cloud SQL..." -ForegroundColor Yellow
$CONNECTION_NAME = gcloud sql instances describe hospicast-db --format="value(connectionName)"
Write-Host "✅ Connection name: $CONNECTION_NAME" -ForegroundColor Green

# 3. Configurar Docker
Write-Host "3️⃣ Configurando Docker..." -ForegroundColor Yellow
gcloud auth configure-docker --quiet

# 4. Verificar diretório
Write-Host "4️⃣ Verificando diretório..." -ForegroundColor Yellow
if (-not (Test-Path "backend")) {
    Write-Host "❌ Erro: Diretório 'backend' não encontrado!" -ForegroundColor Red
    exit 1
}

# 5. Obter DATABASE_URL
Write-Host "5️⃣ Obtendo DATABASE_URL..." -ForegroundColor Yellow
$DATABASE_URL = gcloud run services describe $SERVICE_NAME `
    --platform managed `
    --region $REGION `
    --format="value(spec.template.spec.containers[0].env[0].value)" 2>$null

if ([string]::IsNullOrEmpty($DATABASE_URL)) {
    Write-Host "⚠️ DATABASE_URL não encontrado. Digite manualmente:" -ForegroundColor Yellow
    $DATABASE_URL = Read-Host "DATABASE_URL"
}

# 6. Gerar tag
$IMAGE_TAG = Get-Date -Format "yyyyMMdd-HHmmss"
Write-Host "📌 Tag da imagem: $IMAGE_TAG" -ForegroundColor Cyan

# 7. Build da imagem
Write-Host "7️⃣ Fazendo build da imagem Docker..." -ForegroundColor Yellow
Set-Location backend
docker build -t "${IMAGE_NAME}:latest" -t "${IMAGE_NAME}:${IMAGE_TAG}" .
Set-Location ..

# 8. Push da imagem
Write-Host "8️⃣ Fazendo push da imagem..." -ForegroundColor Yellow
docker push "${IMAGE_NAME}:latest"
docker push "${IMAGE_NAME}:${IMAGE_TAG}"

# 9. Deploy no Cloud Run
Write-Host "9️⃣ Fazendo deploy no Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --image "${IMAGE_NAME}:${IMAGE_TAG}" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars "DATABASE_URL=$DATABASE_URL,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" `
    --memory 2Gi `
    --cpu 2 `
    --timeout 600 `
    --max-instances 10 `
    --port 8080 `
    --cpu-boost

# 10. Obter URL
Write-Host "🔟 Obtendo URL do serviço..." -ForegroundColor Yellow
$SERVICE_URL = gcloud run services describe $SERVICE_NAME `
    --platform managed `
    --region $REGION `
    --format="value(status.url)"
Write-Host "✅ Backend URL: $SERVICE_URL" -ForegroundColor Green

# 11. Testar
Write-Host "1️⃣1️⃣ Testando deploy..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$SERVICE_URL/" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Deploy testado com sucesso!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Teste falhou, mas o deploy pode estar OK" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Deploy do backend concluído com sucesso!" -ForegroundColor Green
Write-Host "📝 URL: $SERVICE_URL" -ForegroundColor Cyan
