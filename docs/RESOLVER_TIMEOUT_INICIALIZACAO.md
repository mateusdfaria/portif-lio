# 🔧 Resolver Timeout de Inicialização

## ❌ Container não inicia dentro do timeout

O container pode estar demorando muito para iniciar (instalação do CmdStan, imports, etc).

## ✅ Solução: Aumentar Timeout e Verificar Logs

### Passo 1: Ver Logs Mais Recentes

```bash
# Ver logs da última revisão
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100
```

**Me envie os logs**, especialmente as últimas linhas com erros.

### Passo 2: Deploy com Timeout Maior

```bash
# 1. Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")

# 2. Definir variáveis
PROJECT_ID=$(gcloud config get-value project)
DB_PASSWORD="mateus22"
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# 3. Deploy com timeout maior e CPU boost
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

### Passo 3: Verificar se Erro de API_ALLOWED_ORIGINS Foi Resolvido

Nos logs, procure por:
- ✅ Se não aparecer mais "error parsing env var api_allowed_origins" = corrigido!
- ❌ Se ainda aparecer = precisa fazer rebuild

## 🔍 Possíveis Problemas

### 1. CmdStan Ainda Tentando Instalar

Se aparecer "Installing CmdStan" nos logs, o código ainda está tentando instalar na inicialização.

**Solução**: Verificar se o `main.py` foi atualizado corretamente.

### 2. Erro de Importação

Se aparecer "ModuleNotFoundError", faltam dependências.

### 3. Timeout Realmente Muito Curto

Aumentar timeout para 600 segundos (10 minutos).

## 📋 Comandos Completos

```bash
# 1. Ver logs
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100

# 2. Deploy com timeout maior
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

**Execute os comandos acima e me envie os logs mais recentes!**

