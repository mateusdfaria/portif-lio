# 🚀 Deploy no Google Cloud - Guia Completo

Este guia contém todos os comandos necessários para fazer deploy do HospiCast no Google Cloud Platform.

---

## 📋 Pré-requisitos

1. **Google Cloud Project** configurado: `hospicast-prod`
2. **Cloud SQL** criado: `hospicast-db`
3. **Cloud Storage** bucket criado: `hospicast-frontend`
4. **gcloud CLI** instalado e autenticado
5. **Docker** instalado (para build local)

---

## 🔧 Opção 1: Deploy Completo (Backend + Frontend)

### Via Cloud Shell (Recomendado)

```bash
# 1. Configurar variáveis
export PROJECT_ID="hospicast-prod"
export SERVICE_NAME="hospicast-backend"
export REGION="southamerica-east1"
export BUCKET_NAME="hospicast-frontend"
export IMAGE_NAME="gcr.io/${PROJECT_ID}/hospicast-backend"

# 2. Configurar projeto
gcloud config set project ${PROJECT_ID}

# 3. Obter connection name do Cloud SQL
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection name: ${CONNECTION_NAME}"

# 4. Configurar Docker
gcloud auth configure-docker --quiet

# 5. Obter DATABASE_URL atual (ou definir manualmente)
DATABASE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(spec.template.spec.containers[0].env[0].value)" 2>/dev/null || echo "")

if [ -z "$DATABASE_URL" ]; then
  echo "⚠️ DATABASE_URL não encontrado. Defina manualmente:"
  read -p "Digite o DATABASE_URL: " DATABASE_URL
fi

# 6. Gerar tag
IMAGE_TAG=$(date +%Y%m%d-%H%M%S)

# 7. Build da imagem
cd backend
docker build -t ${IMAGE_NAME}:latest -t ${IMAGE_NAME}:${IMAGE_TAG} .
cd ..

# 8. Push da imagem
docker push ${IMAGE_NAME}:latest
docker push ${IMAGE_NAME}:${IMAGE_TAG}

# 9. Deploy no Cloud Run
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
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(status.url)")
echo "✅ Backend URL: ${SERVICE_URL}"

# 11. Testar
curl -f ${SERVICE_URL}/
echo "✅ Deploy concluído!"
```

---

## 🔧 Opção 2: Deploy Apenas Backend (Rápido)

```bash
# Configurar variáveis
export PROJECT_ID="hospicast-prod"
export SERVICE_NAME="hospicast-backend"
export REGION="southamerica-east1"
export IMAGE_NAME="gcr.io/${PROJECT_ID}/hospicast-backend"
export IMAGE_TAG=$(date +%Y%m%d-%H%M%S)

# Configurar projeto
gcloud config set project ${PROJECT_ID}

# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")

# Obter DATABASE_URL
DATABASE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(spec.template.spec.containers[0].env[0].value)")

# Build e push
cd backend && docker build -t ${IMAGE_NAME}:${IMAGE_TAG} . && docker push ${IMAGE_NAME}:${IMAGE_TAG} && cd ..

# Deploy
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:${IMAGE_TAG} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --add-cloudsql-instances ${CONNECTION_NAME} \
  --set-env-vars DATABASE_URL="${DATABASE_URL}",LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production \
  --memory 2Gi --cpu 2 --timeout 600 --max-instances 10 --port 8080 --cpu-boost
```

---

## 🔧 Opção 3: Usar Script Automatizado

```bash
# Tornar executável
chmod +x scripts/deploy_cloud_shell.sh

# Executar
./scripts/deploy_cloud_shell.sh
```

---

## 🌐 Deploy do Frontend

```bash
# Configurar variáveis
export BUCKET_NAME="hospicast-frontend"
export VITE_API_BASE_URL="https://hospicast-backend-fbuqwglmsq-rj.a.run.app"

# Build do frontend
cd frontend
npm install --legacy-peer-deps
VITE_API_BASE_URL=${VITE_API_BASE_URL} npm run build
cd ..

# Upload para Cloud Storage
gsutil -m rsync -d -r ./frontend/dist gs://${BUCKET_NAME}

# Configurar como público
gsutil iam ch allUsers:objectViewer gs://${BUCKET_NAME}

echo "✅ Frontend deployado: https://storage.googleapis.com/${BUCKET_NAME}/index.html"
```

---

## 🔍 Comandos Úteis

### Verificar Status do Serviço

```bash
gcloud run services describe hospicast-backend \
  --platform managed \
  --region southamerica-east1 \
  --format="yaml(status)"
```

### Ver Logs

```bash
gcloud run services logs read hospicast-backend \
  --platform managed \
  --region southamerica-east1 \
  --limit 50
```

### Ver Variáveis de Ambiente

```bash
gcloud run services describe hospicast-backend \
  --platform managed \
  --region southamerica-east1 \
  --format="value(spec.template.spec.containers[0].env)"
```

### Atualizar Apenas Variáveis de Ambiente

```bash
gcloud run services update hospicast-backend \
  --platform managed \
  --region southamerica-east1 \
  --update-env-vars LOG_LEVEL=DEBUG
```

### Ver URL do Serviço

```bash
gcloud run services describe hospicast-backend \
  --platform managed \
  --region southamerica-east1 \
  --format="value(status.url)"
```

---

## 🐛 Troubleshooting

### Erro: "Image not found"

```bash
# Verificar se a imagem existe
gcloud container images list --repository=gcr.io/${PROJECT_ID}

# Ver tags da imagem
gcloud container images list-tags gcr.io/${PROJECT_ID}/hospicast-backend
```

### Erro: "Connection refused" no Cloud SQL

```bash
# Verificar se o Cloud SQL está rodando
gcloud sql instances describe hospicast-db

# Verificar connection name
gcloud sql instances describe hospicast-db --format="value(connectionName)"
```

### Erro: "Permission denied"

```bash
# Verificar permissões
gcloud projects get-iam-policy ${PROJECT_ID}

# Verificar se está autenticado
gcloud auth list
```

---

## 📝 Exemplo Completo (Copy & Paste)

```bash
#!/bin/bash
# Deploy completo do HospiCast

set -e

export PROJECT_ID="hospicast-prod"
export SERVICE_NAME="hospicast-backend"
export REGION="southamerica-east1"
export BUCKET_NAME="hospicast-frontend"
export IMAGE_NAME="gcr.io/${PROJECT_ID}/hospicast-backend"

echo "🚀 Iniciando deploy..."

# Configurar
gcloud config set project ${PROJECT_ID}
gcloud auth configure-docker --quiet

# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")

# Obter DATABASE_URL
DATABASE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(spec.template.spec.containers[0].env[0].value)")

# Build e push
IMAGE_TAG=$(date +%Y%m%d-%H%M%S)
cd backend
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
docker push ${IMAGE_NAME}:${IMAGE_TAG}
cd ..

# Deploy
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:${IMAGE_TAG} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --add-cloudsql-instances ${CONNECTION_NAME} \
  --set-env-vars DATABASE_URL="${DATABASE_URL}",LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production \
  --memory 2Gi --cpu 2 --timeout 600 --max-instances 10 --port 8080 --cpu-boost

# Obter URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(status.url)")

echo "✅ Deploy concluído!"
echo "🌐 URL: ${SERVICE_URL}"
```

---

## 🎯 Deploy do Frontend (Separado)

```bash
#!/bin/bash
# Deploy do frontend

export BUCKET_NAME="hospicast-frontend"
export VITE_API_BASE_URL="https://hospicast-backend-fbuqwglmsq-rj.a.run.app"

cd frontend
npm install --legacy-peer-deps
VITE_API_BASE_URL=${VITE_API_BASE_URL} npm run build
cd ..

gsutil -m rsync -d -r ./frontend/dist gs://${BUCKET_NAME}
gsutil iam ch allUsers:objectViewer gs://${BUCKET_NAME}

echo "✅ Frontend: https://storage.googleapis.com/${BUCKET_NAME}/index.html"
```

---

## 📚 Referências

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Cloud Storage Documentation](https://cloud.google.com/storage/docs)

---

**✅ Pronto! Use os comandos acima para fazer deploy no Google Cloud.**


