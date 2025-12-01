# 🚀 Deploy Completo - Backend + Frontend no Google Cloud

## 📋 Visão Geral

Este guia faz o deploy completo do HospiCast:
- ✅ **Backend (FastAPI)**: Google Cloud Run
- ✅ **Frontend (React)**: Google Cloud Storage
- ✅ **Banco de Dados**: Cloud SQL (PostgreSQL)
- ✅ **Integração**: Frontend conectado ao Backend

---

## 🎯 Passo 1: Verificar/Deploy do Backend

### 1.1. Verificar se o Backend está Deployado

```bash
# Verificar serviços do Cloud Run
gcloud run services list --region southamerica-east1
```

**Se o backend NÃO estiver deployado**, execute:

```bash
# === CONFIGURAÇÃO ===
PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"  # Use sua senha real
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# === BUILD ===
cd ~/portif-lio
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# === DEPLOY ===
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

### 1.2. Obter URL do Backend

```bash
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "✅ Backend URL: $BACKEND_URL"

# Testar backend
curl $BACKEND_URL/
```

**Guarde essa URL!** Você vai precisar dela no próximo passo.

---

## 🌐 Passo 2: Deploy do Frontend

### 2.1. Criar Bucket no Cloud Storage

```bash
PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME="hospicast-frontend"

# Criar bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l southamerica-east1 gs://$BUCKET_NAME

# Configurar como site estático
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME

# Dar permissão pública (para acesso via navegador)
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

echo "✅ Bucket criado: gs://$BUCKET_NAME"
```

### 2.2. Configurar Variável de Ambiente do Frontend

```bash
cd ~/portif-lio

# Obter URL do backend (se ainda não tiver)
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# Criar arquivo .env.production com a URL do backend
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

# Verificar
cat frontend/.env.production
echo ""
echo "✅ Frontend configurado para usar: $BACKEND_URL"
```

### 2.3. Build do Frontend

```bash
cd ~/portif-lio/frontend

# Instalar dependências
npm install

# Build para produção
npm run build

# Verificar se a pasta dist foi criada
ls -la dist/

cd ..
```

**⏱️ Isso pode levar 1-2 minutos**

### 2.4. Upload do Frontend para Cloud Storage

```bash
cd ~/portif-lio

# Upload dos arquivos do build
gsutil -m rsync -r -d frontend/dist gs://$BUCKET_NAME

# Verificar upload
gsutil ls -r gs://$BUCKET_NAME | head -20
```

### 2.5. Obter URL do Frontend

```bash
FRONTEND_URL="https://storage.googleapis.com/$BUCKET_NAME/index.html"
echo "✅ Frontend URL: $FRONTEND_URL"
echo ""
echo "🌐 Acesse seu frontend em:"
echo "   $FRONTEND_URL"
```

---

## 🔗 Passo 3: Integrar Frontend com Backend

### 3.1. Configurar CORS no Backend

O backend precisa permitir requisições do frontend:

```bash
# Obter URL do frontend
BUCKET_NAME="hospicast-frontend"
FRONTEND_URL="https://storage.googleapis.com/$BUCKET_NAME"

# Atualizar CORS no backend
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=$FRONTEND_URL,https://storage.googleapis.com/$BUCKET_NAME,http://storage.googleapis.com/$BUCKET_NAME,*"

echo "✅ CORS configurado no backend"
```

### 3.2. Verificar Integração

```bash
# Obter URLs
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

FRONTEND_URL="https://storage.googleapis.com/hospicast-frontend/index.html"

echo "📋 URLs Configuradas:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: $FRONTEND_URL"
echo ""
echo "✅ Frontend está configurado para usar o backend automaticamente!"
```

---

## ✅ Passo 4: Testar Tudo

### 4.1. Testar Backend

```bash
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# Testar endpoint raiz
curl $BACKEND_URL/

# Testar busca de cidades
curl "$BACKEND_URL/api/cities/search?q=joinville"
```

### 4.2. Testar Frontend

1. **Abrir no navegador**:
   ```
   https://storage.googleapis.com/hospicast-frontend/index.html
   ```

2. **Verificar se carrega**: A página deve abrir normalmente

3. **Testar conexão com backend**:
   - Abrir o Console do Navegador (F12)
   - Tentar fazer uma busca de cidade
   - Verificar se não há erros de CORS

### 4.3. Verificar Logs

```bash
# Logs do backend
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 20
```

---

## 🔄 Passo 5: Atualizar Frontend (Quando Fizer Mudanças)

Sempre que você alterar o frontend:

```bash
cd ~/portif-lio

# 1. Atualizar código (se necessário)
git pull origin main

# 2. Build
cd frontend
npm run build
cd ..

# 3. Upload
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

echo "✅ Frontend atualizado!"
```

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
# === CONFIGURAÇÃO INICIAL ===
PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME="hospicast-frontend"

# === 1. VERIFICAR BACKEND ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)" 2>/dev/null)

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Backend não encontrado. Execute o deploy do backend primeiro!"
    exit 1
fi

echo "✅ Backend URL: $BACKEND_URL"

# === 2. CRIAR BUCKET ===
gsutil mb -p $PROJECT_ID -c STANDARD -l southamerica-east1 gs://$BUCKET_NAME 2>/dev/null || echo "Bucket já existe"
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# === 3. CONFIGURAR FRONTEND ===
cd ~/portif-lio
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

# === 4. BUILD FRONTEND ===
cd frontend
npm install
npm run build
cd ..

# === 5. UPLOAD ===
gsutil -m rsync -r -d frontend/dist gs://$BUCKET_NAME

# === 6. CONFIGURAR CORS ===
FRONTEND_URL="https://storage.googleapis.com/$BUCKET_NAME"
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=$FRONTEND_URL,https://storage.googleapis.com/$BUCKET_NAME,http://storage.googleapis.com/$BUCKET_NAME,*"

# === 7. MOSTRAR URLs ===
echo ""
echo "🎉 Deploy Completo!"
echo ""
echo "📋 URLs:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: https://storage.googleapis.com/$BUCKET_NAME/index.html"
echo ""
echo "🌐 Acesse seu frontend no navegador!"
```

---

## 🔍 Verificar Status

### Ver Backend:

```bash
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)"
```

### Ver Frontend:

```bash
gsutil ls -r gs://hospicast-frontend
```

### Ver Logs do Backend:

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

---

## 🎯 Checklist Final

- [ ] Backend deployado no Cloud Run
- [ ] Backend respondendo corretamente
- [ ] Bucket criado no Cloud Storage
- [ ] Frontend buildado com sucesso
- [ ] Frontend uploadado para Cloud Storage
- [ ] Variável `VITE_API_BASE_URL` configurada
- [ ] CORS configurado no backend
- [ ] Frontend acessível no navegador
- [ ] Frontend conectado ao backend
- [ ] Tudo funcionando! 🎉

---

## 🚀 Próximos Passos (Opcional)

1. **Domínio Customizado**: Configurar um domínio próprio
2. **HTTPS**: Configurar SSL/HTTPS
3. **Deploy Automático**: Configurar GitHub Actions
4. **Monitoramento**: Configurar Cloud Monitoring
5. **Backup**: Configurar backup automático do banco

---

**Execute os comandos acima para fazer deploy completo!** 🎯

