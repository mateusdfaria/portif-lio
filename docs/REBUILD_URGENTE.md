# 🚨 REBUILD URGENTE - Corrigir Erro API_ALLOWED_ORIGINS

## ⚠️ Problema

O erro `error parsing env var "api_allowed_origins"` ainda aparece porque **a imagem Docker não foi reconstruída** com a correção.

## ✅ Solução: Rebuild da Imagem Docker

Você precisa fazer **rebuild da imagem Docker** para incluir a correção no código.

### Passo 1: Verificar se está no diretório correto

```bash
# No Cloud Shell
pwd
# Deve mostrar: /home/mateusfarias2308/portif-lio

# Se não estiver, navegue até lá
cd /home/mateusfarias2308/portif-lio
# ou
cd ~/portif-lio
```

### Passo 2: Fazer Rebuild da Imagem

```bash
# Obter PROJECT_ID
PROJECT_ID=$(gcloud config get-value project)
echo "Project ID: $PROJECT_ID" 

# Fazer build e push da nova imagem
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend
```

**⏱️ Isso vai demorar 5-10 minutos** - aguarde a conclusão!

### Passo 3: Deploy no Cloud Run

Após o build completar com sucesso:

```bash
# 1. Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection name: $CONNECTION_NAME"

# 2. Definir variáveis
PROJECT_ID=$(gcloud config get-value project)
DB_PASSWORD="mateus22"
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# 3. Deploy no Cloud Run
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

### Passo 4: Verificar Logs

Após o deploy, aguarde 1-2 minutos e verifique os logs:

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

**✅ SUCESSO**: Não deve aparecer mais `error parsing env var "api_allowed_origins"`

**❌ ERRO**: Se ainda aparecer, me envie os logs completos

## 📋 Comandos Completos (Copiar e Colar)

```bash
# === 1. REBUILD ===
cd /home/mateusfarias2308/portif-lio
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
```

## 🔍 O que foi corrigido?

O arquivo `backend/core/config.py` agora tem um validator que força `allowed_origins` a ser sempre string:

```python
@validator("allowed_origins", pre=True)
def _validate_allowed_origins(cls, value: str | list[str] | None) -> str:
    """Força allowed_origins a ser sempre string, evitando parse JSON do Pydantic."""
    if value is None:
        return "*"
    if isinstance(value, list):
        return ",".join(str(v) for v in value)
    return str(value)
```

Mas essa correção só funciona se a imagem Docker for reconstruída!

---

**Execute o rebuild agora e me avise o resultado!**

