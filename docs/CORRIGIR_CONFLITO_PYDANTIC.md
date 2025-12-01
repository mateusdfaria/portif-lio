# 🔧 Corrigir Conflito de Dependências Pydantic

## ❌ Problema Identificado

**Erro**: Conflito entre `pydantic<2.0.0` e `pydantic-settings>=2.0.0`

- `pydantic<2.0.0` força Pydantic v1
- `pydantic-settings>=2.0.0` requer Pydantic v2

## ✅ Correção Aplicada

Atualizei `backend/requirements.txt` para usar Pydantic v2:

```diff
- pydantic>=1.10.15,<2.0.0
+ pydantic>=2.0.0
```

O código já está preparado para Pydantic v2 (usa `field_validator` e `pydantic-settings`).

## 🔄 Próximos Passos

### 1. Fazer Commit e Push da Correção

```bash
# No Cloud Shell ou localmente
cd ~/portif-lio

# Verificar mudanças
git status
git diff backend/requirements.txt

# Commit e push
git add backend/requirements.txt
git commit -m "fix: atualizar para Pydantic v2 para resolver conflito de dependências"
git push origin main
```

### 2. Rebuild da Imagem Docker

```bash
# No Cloud Shell
cd ~/portif-lio

PROJECT_ID=$(gcloud config get-value project)

# Rebuild
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend
```

**⏱️ Isso vai demorar 5-10 minutos** - não cancele!

### 3. Deploy no Cloud Run

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

### 4. Verificar se Funcionou

```bash
# Aguardar 1-2 minutos e verificar
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "Backend URL: $BACKEND_URL"

# Testar
curl $BACKEND_URL/
```

## 📋 Comandos Completos

```bash
# === 1. COMMIT E PUSH ===
cd ~/portif-lio
git add backend/requirements.txt
git commit -m "fix: atualizar para Pydantic v2"
git push origin main

# === 2. REBUILD ===
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
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")
echo "Backend URL: $BACKEND_URL"
curl $BACKEND_URL/
```

---

**Execute os comandos acima para corrigir o problema!**



