# 🔧 Solução: Erro "error parsing env var api_allowed_origins"

## ❌ Problema Identificado

O erro é:
```
pydantic.env_settings.SettingsError: error parsing env var "api_allowed_origins"
```

**Causa**: O Pydantic está tentando fazer parse de `API_ALLOWED_ORIGINS` como JSON porque o tipo era `list[str]`, mas o valor `*` não é JSON válido.

## ✅ Correções Aplicadas

1. **config.py** - Mudado `allowed_origins` de `list[str]` para `str`
2. **main.py** - Atualizado para usar `settings.get_allowed_origins_list()`
3. **Dockerfile** - Adicionado `make` para CmdStan funcionar

## 🔨 Rebuild e Deploy

### Passo 1: Rebuild da Imagem

```bash
# Rebuild com correções
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/hospicast-backend:latest ./backend
```

**⏱️ Aguarde o build terminar (5-10 minutos)**

### Passo 2: Deploy no Cloud Run

```bash
# 1. Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")

# 2. Definir variáveis
PROJECT_ID=$(gcloud config get-value project)
DB_PASSWORD="mateus22"
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# 3. Deploy
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
    --timeout 300 \
    --max-instances 10 \
    --port 8080
```

## ✅ O que foi corrigido

1. ✅ `allowed_origins` agora é `str` (não `list[str]`)
2. ✅ Método `get_allowed_origins_list()` para converter para lista
3. ✅ `main.py` usa o método correto
4. ✅ Dockerfile tem `make` para CmdStan

## 🚀 Depois do Deploy

```bash
# Obter URL
SERVICE_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "✅ URL: $SERVICE_URL"

# Testar
curl $SERVICE_URL/
```

---

**Faça rebuild e deploy novamente com as correções!**

