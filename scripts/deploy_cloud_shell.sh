#!/bin/bash

# Script para fazer deploy do HospiCast pelo Cloud Shell
# Baseado no workflow .github/workflows/deploy-cloud-run.yml

set -e  # Para em caso de erro

# Variáveis de ambiente
PROJECT_ID="hospicast-prod"
SERVICE_NAME="hospicast-backend"
REGION="southamerica-east1"
BUCKET_NAME="hospicast-frontend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/hospicast-backend"

echo "🚀 Iniciando deploy do HospiCast..."
echo "📦 Projeto: ${PROJECT_ID}"
echo "🌍 Região: ${REGION}"

# 1. Configurar projeto
echo ""
echo "1️⃣ Configurando projeto GCP..."
gcloud config set project ${PROJECT_ID}

# 2. Obter connection name do Cloud SQL
echo ""
echo "2️⃣ Obtendo connection name do Cloud SQL..."
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "✅ Connection name: ${CONNECTION_NAME}"

# 3. Configurar Docker para GCR
echo ""
echo "3️⃣ Configurando Docker para GCR..."
gcloud auth configure-docker --quiet

# 4. Verificar se está no diretório correto
echo ""
echo "4️⃣ Verificando diretório..."
if [ ! -d "backend" ]; then
  echo "❌ Erro: Diretório 'backend' não encontrado!"
  echo "💡 Certifique-se de estar no diretório raiz do repositório"
  echo "💡 Ou clone o repositório: git clone <seu-repo>"
  exit 1
fi

# 5. Obter DATABASE_URL atual do Cloud Run
echo ""
echo "5️⃣ Obtendo DATABASE_URL atual do Cloud Run..."
DATABASE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(spec.template.spec.containers[0].env[0].value)" 2>/dev/null || echo "")
if [ -z "$DATABASE_URL" ]; then
  echo "⚠️  Não foi possível obter DATABASE_URL automaticamente"
  echo "💡 Você precisará fornecer o DATABASE_URL manualmente"
  read -p "Digite o DATABASE_URL: " DATABASE_URL
fi

# 6. Gerar tag com timestamp
IMAGE_TAG=$(date +%Y%m%d-%H%M%S)
echo "📌 Tag da imagem: ${IMAGE_TAG}"

# 7. Build da imagem Docker
echo ""
echo "7️⃣ Fazendo build da imagem Docker..."
cd backend
docker build -t ${IMAGE_NAME}:latest \
  -t ${IMAGE_NAME}:${IMAGE_TAG} \
  .
cd ..

# 8. Push da imagem
echo ""
echo "8️⃣ Fazendo push da imagem para GCR..."
docker push ${IMAGE_NAME}:latest
docker push ${IMAGE_NAME}:${IMAGE_TAG}

# 9. Deploy no Cloud Run (SEM API_ALLOWED_ORIGINS para preservar o valor atual)
echo ""
echo "9️⃣ Fazendo deploy no Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:${IMAGE_TAG} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --add-cloudsql-instances ${CONNECTION_NAME} \
  --set-env-vars DATABASE_URL="${DATABASE_URL}",LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --max-instances 10 \
  --port 8080 \
  --cpu-boost

# 10. Obter URL do serviço
echo ""
echo "🔟 Obtendo URL do serviço..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(status.url)")
echo "✅ Backend URL: ${SERVICE_URL}"

# 11. Testar deploy
echo ""
echo "1️⃣1️⃣ Testando deploy..."
curl -f ${SERVICE_URL}/ || exit 1
echo "✅ Backend deployment test passed!"

echo ""
echo "🎉 Deploy do backend concluído com sucesso!"
echo "📝 URL: ${SERVICE_URL}"

