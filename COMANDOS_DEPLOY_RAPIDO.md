# ⚡ Comandos de Deploy Rápido - Google Cloud

## 🚀 Deploy Backend (Copy & Paste)

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

# Ver URL
gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(status.url)"
```

---

## 🌐 Deploy Frontend (Copy & Paste)

```bash
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

## 📋 Usar Scripts Automatizados

### Linux/Mac (Cloud Shell)
```bash
chmod +x scripts/deploy_cloud_shell.sh
./scripts/deploy_cloud_shell.sh
```

### Windows (PowerShell)
```powershell
.\scripts\deploy_gcloud.ps1
```

---

## 🔍 Comandos Úteis

### Ver Logs
```bash
gcloud run services logs read hospicast-backend \
  --platform managed \
  --region southamerica-east1 \
  --limit 50
```

### Ver Status
```bash
gcloud run services describe hospicast-backend \
  --platform managed \
  --region southamerica-east1 \
  --format="value(status.url)"
```

### Ver Variáveis de Ambiente
```bash
gcloud run services describe hospicast-backend \
  --platform managed \
  --region southamerica-east1 \
  --format="yaml(spec.template.spec.containers[0].env)"
```

---

**💡 Dica**: Para mais detalhes, veja `DEPLOY_GOOGLE_CLOUD.md`


