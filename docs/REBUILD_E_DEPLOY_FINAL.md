# 🔄 Rebuild e Deploy Final - Corrigir Erro API_ALLOWED_ORIGINS

## ✅ Correção Aplicada

O código foi corrigido para evitar o erro `error parsing env var "api_allowed_origins"` adicionando um validator que força o valor a ser sempre string.

## 📋 Passos para Deploy

### 1. Fazer Rebuild da Imagem Docker

**No Cloud Shell ou localmente:**

```bash
# 1. Navegar para o diretório do projeto
cd ~/portif-lio  # ou o caminho onde está o projeto

# 2. Obter PROJECT_ID
PROJECT_ID=$(gcloud config get-value project)
echo "Project ID: $PROJECT_ID"

# 3. Fazer build e push da nova imagem
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend
```

**Isso vai demorar alguns minutos** enquanto o Docker constrói a imagem com as correções.

### 2. Deploy no Cloud Run

Após o build completar com sucesso:

```bash
# 1. Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection name: $CONNECTION_NAME"

# 2. Definir variáveis
PROJECT_ID=$(gcloud config get-value project)
DB_PASSWORD="mateus22"
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# 3. Deploy no Cloud Run com timeout maior
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

Após o deploy, verifique os logs:

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

**O que procurar:**
- ✅ **SUCESSO**: Não deve aparecer mais `error parsing env var "api_allowed_origins"`
- ✅ **SUCESSO**: Deve aparecer "Application startup complete" ou similar
- ❌ **ERRO**: Se ainda aparecer o erro, me envie os logs completos

### 4. Testar o Serviço

Após o deploy, teste o endpoint:

```bash
# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "Service URL: $SERVICE_URL"

# Testar endpoint raiz
curl $SERVICE_URL/
```

## 🔍 Comandos Completos (Copiar e Colar)

```bash
# === 1. REBUILD ===
cd ~/portif-lio
PROJECT_ID=$(gcloud config get-value project)
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# === 2. DEPLOY ===
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

# === 3. VERIFICAR LOGS ===
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50

# === 4. TESTAR ===
SERVICE_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")
curl $SERVICE_URL/
```

## ⚠️ Importante

1. **O build pode demorar 5-10 minutos** - seja paciente!
2. **O deploy pode demorar 2-3 minutos** - aguarde a conclusão
3. **Se ainda der erro**, me envie os logs completos da última revisão

---

**Execute os comandos acima e me avise o resultado!**

