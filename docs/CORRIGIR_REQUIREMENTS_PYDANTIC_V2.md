# 🔧 Corrigir Requirements.txt para Pydantic v2

## ❌ Problema

Conflito de dependências ao instalar Pydantic v2 com FastAPI.

## ✅ Solução

Atualizei `backend/requirements.txt` para usar versões compatíveis:

```diff
- fastapi==0.110.0
- uvicorn[standard]==0.27.1
- pydantic>=1.10.15,<2.0.0
- pydantic-settings>=2.0.0
+ fastapi>=0.110.0
+ uvicorn[standard]>=0.27.1
+ pydantic>=2.0.0,<3.0.0
+ pydantic-settings>=2.0.0,<3.0.0
```

## 🔄 Próximos Passos

### 1. Fazer Commit e Push

```bash
cd ~/portif-lio
git add backend/requirements.txt
git commit -m "fix: atualizar requirements para Pydantic v2 compatível"
git push origin main
```

### 2. Rebuild

```bash
PROJECT_ID=$(gcloud config get-value project)
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend
```

### 3. Deploy

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

---

**Execute os comandos acima!**



