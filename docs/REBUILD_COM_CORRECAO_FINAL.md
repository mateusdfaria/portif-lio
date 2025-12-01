# 🔄 Rebuild com Correção Final - API_ALLOWED_ORIGINS

## ✅ Correção Aplicada

O código foi atualizado para interceptar `API_ALLOWED_ORIGINS` antes do Pydantic tentar fazer parse JSON.

## 📋 Passos para Rebuild e Deploy

### 1. Rebuild da Imagem Docker

```bash
cd /home/mateusfarias2308/portif-lio
PROJECT_ID=$(gcloud config get-value project)
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend
```

**⏱️ Aguarde 5-10 minutos** - não cancele o processo!

### 2. Deploy no Cloud Run

Após o build completar:

```bash
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASSWORD="mateus22"
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

gcloud run deploy hospicast-backend \
    --image gcr.io/${PROJECT_ID}/hospicast-backend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances ${CONNECTION_NAME} \
    --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --set-env-vars "LOG_LEVEL=INFO" \
    --set-env-vars "PROMETHEUS_ENABLED=true" \
    --set-env-vars "ENVIRONMENT=production" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 600 \
    --max-instances 10 \
    --port 8080 \
    --cpu-boost
```

### 3. Verificar Logs

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

**✅ SUCESSO**: Não deve aparecer mais `error parsing env var "api_allowed_origins"`

---

**Execute o rebuild e me avise o resultado!**



