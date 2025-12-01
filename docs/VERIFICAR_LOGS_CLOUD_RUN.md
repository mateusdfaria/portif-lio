# 🔍 Verificar Logs do Cloud Run

## ❌ Container não está iniciando

Precisamos ver os logs para entender o problema.

## ✅ Ver Logs

### Opção 1: Via gcloud

```bash
# Ver últimos logs
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100
```

### Opção 2: Via Console Web

Acesse o link que apareceu no erro:
```
https://console.cloud.google.com/logs/viewer?project=hospicast-prod&resource=cloud_run_revision/service_name/hospicast-backend/revision_name/hospicast-backend-00005-9dz
```

## 🔍 Problemas Comuns

### 1. Erro de Importação de Módulos

Se aparecer "ModuleNotFoundError", significa que faltam dependências no requirements.txt.

### 2. Erro de Conexão com Banco

Se aparecer erro de conexão, verificar se DATABASE_URL está correta.

### 3. Erro no Código

Pode haver erro de sintaxe ou lógica no código.

### 4. Timeout Muito Curto

O container pode estar demorando muito para iniciar (instalação do CmdStan).

## ✅ Solução: Aumentar Timeout de Inicialização

```bash
# Deploy com timeout maior
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
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --port 8080 \
    --timeout 600 \
    --cpu-boost
```

## 🔧 Verificar Logs e Me Enviar

Execute:

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100
```

E me envie o resultado para eu identificar o problema específico.

---

**Execute o comando acima e me envie os logs!**

