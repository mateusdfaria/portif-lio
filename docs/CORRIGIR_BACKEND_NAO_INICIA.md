# 🔧 Corrigir Backend que Não Inicia

## ❌ Problema: Container não inicia

O serviço existe mas a revisão não está pronta. O container falha ao iniciar.

## 🔍 Diagnóstico

### 1. Ver Logs da Última Revisão

```bash
# Ver logs da revisão que falhou
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100
```

**Procure por:**
- `error parsing env var "api_allowed_origins"` = Erro que precisa corrigir
- Outros erros de inicialização

## ✅ Solução: Rebuild e Redeploy

### Passo 1: Verificar Código Local

O código já foi corrigido, mas a imagem Docker precisa ser reconstruída.

### Passo 2: Rebuild da Imagem

```bash
# No Cloud Shell
cd ~/portif-lio

PROJECT_ID=$(gcloud config get-value project)

# Fazer rebuild
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend
```

**⏱️ Isso vai demorar 5-10 minutos** - não cancele!

### Passo 3: Deploy no Cloud Run

Após o build completar:

```bash
# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")

# Definir variáveis
PROJECT_ID=$(gcloud config get-value project)
DB_PASSWORD="mateus22"
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# Deploy
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

### Passo 4: Verificar Logs Após Deploy

```bash
# Aguardar 1-2 minutos e verificar logs
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

**✅ SUCESSO**: Não deve aparecer mais `error parsing env var "api_allowed_origins"`

## 📋 Comandos Completos

```bash
# === 1. VER LOGS ATUAIS ===
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100

# === 2. REBUILD ===
cd ~/portif-lio
PROJECT_ID=$(gcloud config get-value project)
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# === 3. DEPLOY ===
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

# === 4. VERIFICAR ===
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)"
```

---

**Execute primeiro os logs para confirmar o erro, depois faça o rebuild!**



