# 🔧 Resolver Erro: Container não inicia no Cloud Run

## ❌ Erro: "container failed to start and listen on the port"

O Cloud Run espera que a aplicação escute na porta definida pela variável `PORT` (padrão: 8080), mas o container pode estar configurado para outra porta.

## ✅ Solução: Corrigir Dockerfile

O Dockerfile já foi corrigido para usar `PORT=8080`. Agora você precisa:

### Opção 1: Rebuild e Redeploy (Recomendado)

```bash
# 1. Rebuild da imagem com Dockerfile corrigido
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/hospicast-backend:latest ./backend

# 2. Aguardar build terminar

# 3. Fazer deploy novamente
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
    --port 8080
```

### Opção 2: Verificar Logs para Mais Detalhes

```bash
# Ver logs do Cloud Run
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

Ou acesse o link dos logs que apareceu no erro.

## 🔍 Verificar o que foi corrigido

O Dockerfile agora:
- ✅ Usa `ENV PORT=8080` (porta padrão do Cloud Run)
- ✅ Usa `${PORT:-8080}` no CMD (usa PORT se definido, senão 8080)
- ✅ Health check usa a porta correta

## 📋 Comandos Completos para Rebuild

```bash
# 1. Rebuild
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/hospicast-backend:latest ./backend

# 2. Aguardar SUCCESS

# 3. Deploy novamente
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
    --port 8080
```

## 🐛 Outros Problemas Possíveis

### Se ainda der erro, verificar logs:

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100
```

### Verificar se há erros de importação:

Os logs podem mostrar erros como:
- "ModuleNotFoundError"
- "ImportError"
- Erros de conexão com banco

---

**Faça rebuild da imagem e deploy novamente!**

