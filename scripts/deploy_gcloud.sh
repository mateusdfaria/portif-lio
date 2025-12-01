#!/bin/bash
# Script de deploy automático para Google Cloud
# Uso: ./scripts/deploy_gcloud.sh

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy do HospiCast no Google Cloud..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud não está instalado.${NC}"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Obter PROJECT_ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠️  Nenhum projeto configurado.${NC}"
    read -p "Digite o PROJECT_ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo -e "${GREEN}✅ Projeto: $PROJECT_ID${NC}"

# Verificar se está autenticado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Não autenticado. Fazendo login...${NC}"
    gcloud auth login
fi

# Habilitar APIs necessárias
echo -e "${GREEN}📦 Habilitando APIs...${NC}"
gcloud services enable run.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

# Configurar Docker para GCR
echo -e "${GREEN}🐳 Configurando Docker...${NC}"
gcloud auth configure-docker --quiet

# Build e push da imagem
echo -e "${GREEN}🔨 Fazendo build da imagem...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/hospicast-backend:latest ./backend

# Obter connection name do Cloud SQL
echo -e "${GREEN}🗄️  Verificando Cloud SQL...${NC}"
INSTANCE_NAME="hospicast-db"
CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)" 2>/dev/null || echo "")

if [ -z "$CONNECTION_NAME" ]; then
    echo -e "${YELLOW}⚠️  Instância Cloud SQL não encontrada.${NC}"
    echo "Crie a instância primeiro com:"
    echo "gcloud sql instances create $INSTANCE_NAME --database-version=POSTGRES_15 --tier=db-f1-micro --region=southamerica-east1"
    exit 1
fi

echo -e "${GREEN}✅ Connection name: $CONNECTION_NAME${NC}"

# Solicitar informações
read -p "Digite a senha do banco de dados: " -s DB_PASSWORD
echo ""

read -p "Digite as origens permitidas (CORS), separadas por vírgula [*]: " ALLOWED_ORIGINS
ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-"*"}

# Construir DATABASE_URL
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# Deploy no Cloud Run
echo -e "${GREEN}🚀 Fazendo deploy no Cloud Run...${NC}"
gcloud run deploy hospicast-backend \
    --image gcr.io/$PROJECT_ID/hospicast-backend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
    --set-env-vars "API_ALLOWED_ORIGINS=${ALLOWED_ORIGINS}" \
    --set-env-vars "LOG_LEVEL=INFO" \
    --set-env-vars "PROMETHEUS_ENABLED=true" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe hospicast-backend --platform managed --region southamerica-east1 --format="value(status.url)")

echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo -e "${GREEN}🌐 URL do serviço: $SERVICE_URL${NC}"
echo ""
echo "Teste o endpoint:"
echo "curl $SERVICE_URL/"
echo ""
echo "Atualize o frontend para usar esta URL!"



