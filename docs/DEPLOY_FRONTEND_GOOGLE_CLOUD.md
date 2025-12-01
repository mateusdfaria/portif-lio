# 🚀 Deploy do Frontend no Google Cloud

## 📋 Opções no Google Cloud

Existem várias formas de fazer deploy do frontend no Google Cloud:

1. **Cloud Storage + Cloud CDN** (Recomendado - mais simples)
2. **Cloud Run** (servir arquivos estáticos)
3. **App Engine** (servir arquivos estáticos)
4. **Firebase Hosting** (parte do Google Cloud)

## ✅ Opção 1: Cloud Storage + Cloud CDN (Recomendado)

### Vantagens:
- ✅ Gratuito para começar
- ✅ CDN global
- ✅ SSL automático
- ✅ Integração com Google Cloud
- ✅ Fácil de configurar

### Passo 1: Criar Bucket no Cloud Storage

```bash
PROJECT_ID="hospicast-prod"
BUCKET_NAME="hospicast-frontend"

# Criar bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l southamerica-east1 gs://$BUCKET_NAME

# Configurar bucket para hospedar site estático
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME
```

### Passo 2: Configurar Permissões Públicas

```bash
# Dar permissão de leitura pública
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
```

### Passo 3: Build do Frontend

```bash
# Obter URL do backend
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# Criar .env.production
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

# Build
cd frontend
npm install
npm run build
cd ..
```

### Passo 4: Upload dos Arquivos

```bash
# Upload da pasta dist para o bucket
gsutil -m cp -r frontend/dist/* gs://$BUCKET_NAME/

# Ou usar rsync (mais eficiente)
gsutil -m rsync -r -d frontend/dist gs://$BUCKET_NAME
```

### Passo 5: Configurar Cloud CDN (Opcional mas Recomendado)

```bash
# Criar backend bucket
gcloud compute backend-buckets create hospicast-frontend-backend \
    --gcs-bucket-name=$BUCKET_NAME

# Criar URL map
gcloud compute url-maps create hospicast-frontend-map \
    --default-backend-bucket=hospicast-frontend-backend

# Criar proxy
gcloud compute target-http-proxies create hospicast-frontend-proxy \
    --url-map=hospicast-frontend-map

# Criar forwarding rule (IP público)
gcloud compute forwarding-rules create hospicast-frontend-rule \
    --global \
    --target-http-proxy=hospicast-frontend-proxy \
    --ports=80

# Obter IP
gcloud compute forwarding-rules describe hospicast-frontend-rule \
    --global \
    --format="value(IPAddress)"
```

### Passo 6: Acessar o Site

**Opção A: Direto do Cloud Storage**
```
http://storage.googleapis.com/hospicast-frontend/index.html
```

**Opção B: Via Cloud CDN (após configurar)**
```
http://[IP_OBTIDO]/index.html
```

## ✅ Opção 2: Cloud Run (Servir Arquivos Estáticos)

### Criar Dockerfile para Frontend Estático

Criar `frontend/Dockerfile.static`:

```dockerfile
FROM nginx:alpine
COPY dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Build e Deploy

```bash
# Build da imagem
gcloud builds submit --tag gcr.io/$PROJECT_ID/hospicast-frontend:latest ./frontend

# Deploy no Cloud Run
gcloud run deploy hospicast-frontend \
    --image gcr.io/$PROJECT_ID/hospicast-frontend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --port 80
```

## ✅ Opção 3: App Engine

### Criar `app.yaml` na raiz:

```yaml
runtime: python39

handlers:
- url: /
  static_files: frontend/dist/index.html
  upload: frontend/dist/index.html

- url: /(.*)
  static_files: frontend/dist/\1
  upload: frontend/dist/(.*)
```

### Deploy:

```bash
gcloud app deploy
```

## 📋 Comandos Completos - Cloud Storage (Recomendado)

```bash
# === 1. DEFINIR VARIÁVEIS ===
PROJECT_ID="hospicast-prod"
BUCKET_NAME="hospicast-frontend"

# === 2. CRIAR BUCKET ===
gsutil mb -p $PROJECT_ID -c STANDARD -l southamerica-east1 gs://$BUCKET_NAME

# === 3. CONFIGURAR PARA SITE ESTÁTICO ===
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME

# === 4. PERMISSÕES PÚBLICAS ===
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# === 5. OBTER URL DO BACKEND ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# === 6. CONFIGURAR .env.production ===
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

# === 7. BUILD ===
cd frontend
npm install
npm run build
cd ..

# === 8. UPLOAD ===
gsutil -m rsync -r -d frontend/dist gs://$BUCKET_NAME

# === 9. VER URL ===
echo "Frontend URL: http://storage.googleapis.com/$BUCKET_NAME/index.html"
```

## 🔄 Deploy Automático via GitHub Actions

Criar `.github/workflows/deploy-frontend-gcs.yml`:

```yaml
name: Deploy Frontend to Google Cloud Storage

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend-gcs.yml'
  workflow_dispatch:

env:
  PROJECT_ID: hospicast-prod
  BUCKET_NAME: hospicast-frontend

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Get Backend URL
        id: backend-url
        run: |
          BACKEND_URL=$(gcloud run services describe hospicast-backend \
            --platform managed \
            --region southamerica-east1 \
            --format="value(status.url)")
          echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production
          echo "url=$BACKEND_URL" >> $GITHUB_OUTPUT

      - name: Install dependencies
        working-directory: frontend
        run: npm ci

      - name: Build frontend
        working-directory: frontend
        run: npm run build

      - name: Upload to Cloud Storage
        run: |
          gsutil -m rsync -r -d frontend/dist gs://${{ env.BUCKET_NAME }}
```

## 🔍 Verificar Deploy

```bash
# Listar arquivos no bucket
gsutil ls -r gs://hospicast-frontend

# Ver URL do site
echo "Frontend URL: http://storage.googleapis.com/hospicast-frontend/index.html"
```

## ⚠️ Configurar CORS no Backend

Se o frontend estiver em um domínio diferente, configurar CORS:

```bash
# Atualizar API_ALLOWED_ORIGINS no Cloud Run
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=http://storage.googleapis.com/hospicast-frontend,https://storage.googleapis.com/hospicast-frontend,*"
```

## 🎯 Comparação das Opções

| Opção | Custo | Facilidade | Performance | CDN |
|-------|-------|------------|-------------|-----|
| Cloud Storage + CDN | ✅ Gratuito | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ |
| Cloud Run | 💰 Pago | ⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ |
| App Engine | 💰 Pago | ⭐⭐⭐ | ⭐⭐⭐ | ❌ |
| Firebase Hosting | ✅ Gratuito | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ |

## 📋 Recomendação

**Cloud Storage + Cloud CDN** é a melhor opção para frontend estático no Google Cloud:
- ✅ Gratuito para começar
- ✅ CDN global
- ✅ Fácil de configurar
- ✅ Integração nativa com Google Cloud

---

**Execute os comandos acima para fazer deploy no Cloud Storage!**



