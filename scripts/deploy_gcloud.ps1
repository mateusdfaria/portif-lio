# Script de deploy automático para Google Cloud (PowerShell)
# Uso: .\scripts\deploy_gcloud.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Iniciando deploy do HospiCast no Google Cloud..." -ForegroundColor Green

# Verificar se gcloud está instalado
try {
    $null = gcloud --version 2>&1
} catch {
    Write-Host "❌ gcloud não está instalado." -ForegroundColor Red
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Obter PROJECT_ID
$PROJECT_ID = gcloud config get-value project 2>$null

if (-not $PROJECT_ID) {
    Write-Host "⚠️  Nenhum projeto configurado." -ForegroundColor Yellow
    $PROJECT_ID = Read-Host "Digite o PROJECT_ID"
    gcloud config set project $PROJECT_ID
}

Write-Host "✅ Projeto: $PROJECT_ID" -ForegroundColor Green

# Verificar se está autenticado
$activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $activeAccount) {
    Write-Host "⚠️  Não autenticado. Fazendo login..." -ForegroundColor Yellow
    gcloud auth login
}

# Habilitar APIs necessárias
Write-Host "📦 Habilitando APIs..." -ForegroundColor Green
gcloud services enable run.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

# Configurar Docker para GCR
Write-Host "🐳 Configurando Docker..." -ForegroundColor Green
gcloud auth configure-docker --quiet

# Build e push da imagem
Write-Host "🔨 Fazendo build da imagem..." -ForegroundColor Green
gcloud builds submit --tag "gcr.io/$PROJECT_ID/hospicast-backend:latest" ./backend

# Obter connection name do Cloud SQL
Write-Host "🗄️  Verificando Cloud SQL..." -ForegroundColor Green
$INSTANCE_NAME = "hospicast-db"
$CONNECTION_NAME = gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)" 2>$null

if (-not $CONNECTION_NAME) {
    Write-Host "⚠️  Instância Cloud SQL não encontrada." -ForegroundColor Yellow
    Write-Host "Crie a instância primeiro com:" -ForegroundColor Yellow
    Write-Host "gcloud sql instances create $INSTANCE_NAME --database-version=POSTGRES_15 --tier=db-f1-micro --region=southamerica-east1" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Connection name: $CONNECTION_NAME" -ForegroundColor Green

# Solicitar informações
$securePassword = Read-Host "Digite a senha do banco de dados" -AsSecureString
$DB_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
)

$ALLOWED_ORIGINS = Read-Host "Digite as origens permitidas (CORS), separadas por vírgula [*]"
if (-not $ALLOWED_ORIGINS) {
    $ALLOWED_ORIGINS = "*"
}

# Construir DATABASE_URL
$DATABASE_URL = "postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# Deploy no Cloud Run
Write-Host "🚀 Fazendo deploy no Cloud Run..." -ForegroundColor Green
gcloud run deploy hospicast-backend `
    --image "gcr.io/$PROJECT_ID/hospicast-backend:latest" `
    --platform managed `
    --region southamerica-east1 `
    --allow-unauthenticated `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars "DATABASE_URL=${DATABASE_URL}" `
    --set-env-vars "API_ALLOWED_ORIGINS=${ALLOWED_ORIGINS}" `
    --set-env-vars "LOG_LEVEL=INFO" `
    --set-env-vars "PROMETHEUS_ENABLED=true" `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 0

# Obter URL do serviço
$SERVICE_URL = gcloud run services describe hospicast-backend --platform managed --region southamerica-east1 --format="value(status.url)"

Write-Host "✅ Deploy concluído!" -ForegroundColor Green
Write-Host "🌐 URL do serviço: $SERVICE_URL" -ForegroundColor Green
Write-Host ""
Write-Host "Teste o endpoint:" -ForegroundColor Yellow
Write-Host "curl $SERVICE_URL/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Atualize o frontend para usar esta URL!" -ForegroundColor Yellow



