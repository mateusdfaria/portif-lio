# 🚀 Deploy do Backend Primeiro

## ❌ Problema: Backend não encontrado

O backend ainda não foi deployado no Cloud Run. Vamos fazer o deploy agora!

## ✅ Solução: Deploy do Backend

### Passo 1: Verificar Instância do Cloud SQL

```bash
# Verificar se a instância existe
gcloud sql instances list
```

### Passo 2: Obter Connection Name

```bash
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"
```

### Passo 3: Fazer Build da Imagem

```bash
cd ~/portif-lio
PROJECT_ID=$(gcloud config get-value project)

echo "🔨 Fazendo build da imagem Docker..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend
```

**⏱️ Isso pode levar 10-15 minutos** (instalação do CmdStan)

### Passo 4: Deploy no Cloud Run

```bash
# Configurar variáveis
PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"  # Use sua senha real do banco
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

### Passo 5: Verificar Deploy

```bash
# Obter URL do backend
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "✅ Backend URL: $BACKEND_URL"

# Testar
curl $BACKEND_URL/
```

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
cd ~/portif-lio

# === CONFIGURAÇÃO ===
PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"  # Use sua senha real
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# === BUILD ===
echo "🔨 Fazendo build da imagem..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# === DEPLOY ===
echo "🚀 Fazendo deploy do backend..."
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

# === VERIFICAR ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo ""
echo "✅ Backend deployado com sucesso!"
echo "URL: $BACKEND_URL"
echo ""
echo "🧪 Testar:"
echo "curl $BACKEND_URL/"
```

---

## 🔄 Depois do Backend, Fazer Deploy do Frontend

Após o backend estar funcionando, execute:

```bash
cd ~/portif-lio

# === CONFIGURAÇÃO ===
PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME="hospicast-frontend"

# === OBTER URL DO BACKEND ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "✅ Backend URL: $BACKEND_URL"

# === CRIAR BUCKET ===
gsutil mb -p $PROJECT_ID -c STANDARD -l southamerica-east1 gs://$BUCKET_NAME 2>/dev/null || echo "Bucket já existe"
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# === CONFIGURAR FRONTEND ===
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

# === BUILD ===
cd frontend
npm install
npm run build
cd ..

# === UPLOAD ===
gsutil -m rsync -r -d frontend/dist gs://$BUCKET_NAME

# === CONFIGURAR CORS ===
FRONTEND_URL="https://storage.googleapis.com/$BUCKET_NAME"
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=$FRONTEND_URL,https://storage.googleapis.com/$BUCKET_NAME,http://storage.googleapis.com/$BUCKET_NAME,*"

# === RESULTADO ===
echo ""
echo "🎉 Deploy Completo!"
echo "Backend:  $BACKEND_URL"
echo "Frontend: https://storage.googleapis.com/$BUCKET_NAME/index.html"
```

---

**Execute os comandos acima para fazer o deploy do backend primeiro!** 🎯

