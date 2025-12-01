# 🚀 Deploy Completo no Google Cloud - Frontend + Backend

## 📋 Visão Geral

Este guia faz o deploy completo do projeto HospiCast no Google Cloud:
- ✅ **Backend**: Cloud Run (FastAPI)
- ✅ **Frontend**: Cloud Storage + Cloud CDN (React)
- ✅ **Banco de Dados**: Cloud SQL (PostgreSQL)
- ✅ **Deploy Automático**: GitHub Actions

## 🎯 Arquitetura Final

```
GitHub → GitHub Actions → Cloud Build → Cloud Run (Backend)
                              ↓
                    Cloud Storage (Frontend)
                              ↓
                    Cloud CDN (CDN Global)
```

## 📦 Passo 1: Verificar Backend (Já Deployado)

### Verificar se o backend está funcionando:

```bash
# Obter URL do backend
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "Backend URL: $BACKEND_URL"

# Testar
curl $BACKEND_URL/
```

**Se não estiver deployado**, seguir: `docs/REBUILD_COM_CORRECAO_FINAL.md`

## 🌐 Passo 2: Deploy do Frontend no Cloud Storage

### 2.1. Criar Bucket

```bash
PROJECT_ID="hospicast-prod"
BUCKET_NAME="hospicast-frontend"

# Criar bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l southamerica-east1 gs://$BUCKET_NAME

# Configurar para site estático
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME

# Dar permissão pública
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
```

### 2.2. Configurar Variável de Ambiente do Frontend

```bash
# Obter URL do backend
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# Criar .env.production
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

# Verificar
cat frontend/.env.production
```

### 2.3. Build do Frontend

```bash
# Instalar dependências
cd frontend
npm install

# Build
npm run build

# Verificar se dist foi criado
ls -la dist/

cd ..
```

### 2.4. Upload para Cloud Storage

```bash
# Upload dos arquivos
gsutil -m rsync -r -d frontend/dist gs://$BUCKET_NAME

# Verificar upload
gsutil ls -r gs://$BUCKET_NAME
```

### 2.5. Obter URL do Frontend

```bash
FRONTEND_URL="http://storage.googleapis.com/$BUCKET_NAME/index.html"
echo "Frontend URL: $FRONTEND_URL"
```

## 🔗 Passo 3: Configurar CORS no Backend

O backend precisa permitir requisições do frontend:

```bash
# Obter URL do frontend
FRONTEND_URL="http://storage.googleapis.com/hospicast-frontend"

# Atualizar CORS no backend
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=$FRONTEND_URL,https://storage.googleapis.com/hospicast-frontend,*"
```

## 🌍 Passo 4: Configurar Cloud CDN (Opcional mas Recomendado)

Para melhor performance global:

```bash
# Criar backend bucket
gcloud compute backend-buckets create hospicast-frontend-backend \
    --gcs-bucket-name=$BUCKET_NAME

# Criar URL map
gcloud compute url-maps create hospicast-frontend-map \
    --default-backend-bucket=hospicast-frontend-backend

# Criar proxy HTTP
gcloud compute target-http-proxies create hospicast-frontend-proxy \
    --url-map=hospicast-frontend-map

# Criar forwarding rule (IP público)
gcloud compute forwarding-rules create hospicast-frontend-rule \
    --global \
    --target-http-proxy=hospicast-frontend-proxy \
    --ports=80

# Obter IP
FRONTEND_IP=$(gcloud compute forwarding-rules describe hospicast-frontend-rule \
    --global \
    --format="value(IPAddress)")

echo "Frontend IP: $FRONTEND_IP"
echo "Acesse em: http://$FRONTEND_IP"
```

## 🔄 Passo 5: Configurar Deploy Automático

### 5.1. Criar Service Account (se ainda não fez)

```bash
PROJECT_ID="hospicast-prod"

# Criar service account
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions Deploy" \
    --project=$PROJECT_ID

# Dar permissões
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# Criar chave JSON
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com

# Ver chave
cat github-actions-key.json
```

### 5.2. Adicionar Secrets no GitHub

1. Ir para: https://github.com/mateusdfaria/portif-lio/settings/secrets/actions
2. Adicionar secret:
   - **Nome**: `GCP_SA_KEY`
   - **Valor**: Todo o conteúdo do arquivo `github-actions-key.json`

### 5.3. Workflows já criados

Os workflows já estão criados:
- ✅ `.github/workflows/deploy-cloud-run.yml` (Backend)
- ✅ `.github/workflows/deploy-frontend-gcs.yml` (Frontend)

## ✅ Passo 6: Testar Tudo

### 6.1. Testar Backend

```bash
# Obter URL
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# Testar
curl $BACKEND_URL/
curl "$BACKEND_URL/api/cities/search?q=joinville"
```

### 6.2. Testar Frontend

```bash
# Abrir no navegador
FRONTEND_URL="http://storage.googleapis.com/hospicast-frontend/index.html"
echo "Acesse: $FRONTEND_URL"
```

### 6.3. Testar Integração

1. Abrir frontend no navegador
2. Verificar se carrega
3. Testar uma requisição para o backend
4. Verificar console do navegador (F12) para erros

## 📋 Comandos Completos (Copiar e Colar)

```bash
# === CONFIGURAÇÃO INICIAL ===
PROJECT_ID="hospicast-prod"
BUCKET_NAME="hospicast-frontend"

# === 1. CRIAR BUCKET ===
gsutil mb -p $PROJECT_ID -c STANDARD -l southamerica-east1 gs://$BUCKET_NAME
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# === 2. OBTER URL DO BACKEND ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# === 3. CONFIGURAR FRONTEND ===
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

# === 4. BUILD FRONTEND ===
cd frontend
npm install
npm run build
cd ..

# === 5. UPLOAD ===
gsutil -m rsync -r -d frontend/dist gs://$BUCKET_NAME

# === 6. CONFIGURAR CORS ===
FRONTEND_URL="http://storage.googleapis.com/$BUCKET_NAME"
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=$FRONTEND_URL,https://storage.googleapis.com/$BUCKET_NAME,*"

# === 7. VER URLS ===
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: http://storage.googleapis.com/$BUCKET_NAME/index.html"
```

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

### Ver Logs:

```bash
# Backend
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

## 🎯 Checklist Final

- [ ] Backend deployado no Cloud Run
- [ ] Frontend deployado no Cloud Storage
- [ ] CORS configurado no backend
- [ ] Variável de ambiente do frontend configurada
- [ ] Service account criada para GitHub Actions
- [ ] Secrets adicionados no GitHub
- [ ] Testes realizados
- [ ] Tudo funcionando!

## 🚀 Próximos Passos (Opcional)

1. **Domínio Customizado**: Configurar domínio próprio
2. **HTTPS**: Configurar SSL/HTTPS
3. **Monitoramento**: Configurar Cloud Monitoring
4. **Logs**: Configurar Cloud Logging
5. **Backup**: Configurar backup do banco de dados

---

**Execute os comandos acima para fazer deploy completo no Google Cloud!**



