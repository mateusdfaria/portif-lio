# 📝 Criar Script no Cloud Shell

## ❌ Problema: Script não encontrado

O arquivo `scripts/deploy_completo_gcloud.sh` não existe no Cloud Shell porque ainda não foi commitado e enviado para o GitHub.

## ✅ Solução: Criar Script Diretamente no Cloud Shell

Execute estes comandos no Cloud Shell para criar o script:

```bash
cd ~/portif-lio

# Criar diretório se não existir
mkdir -p scripts

# Criar o script
cat > scripts/deploy_completo_gcloud.sh << 'SCRIPT_END'
#!/bin/bash

# 🚀 Script de Deploy Completo - Backend + Frontend no Google Cloud
# Uso: ./scripts/deploy_completo_gcloud.sh

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy completo do HospiCast..."

# === CONFIGURAÇÃO ===
PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME="hospicast-frontend"
REGION="southamerica-east1"
SERVICE_NAME="hospicast-backend"

# === CORES ===
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# === 1. VERIFICAR BACKEND ===
echo ""
echo "📋 Passo 1: Verificando backend..."
BACKEND_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format="value(status.url)" 2>/dev/null || echo "")

if [ -z "$BACKEND_URL" ]; then
    echo_warning "Backend não encontrado. Fazendo deploy do backend..."
    
    # Obter connection name
    CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)" 2>/dev/null || echo "")
    
    if [ -z "$CONNECTION_NAME" ]; then
        echo_error "Instância do Cloud SQL não encontrada!"
        exit 1
    fi
    
    echo "Digite a senha do banco de dados:"
    read -s DB_PASSWORD
    
    DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"
    
    # Build
    echo "🔨 Fazendo build da imagem..."
    cd ~/portif-lio
    gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend
    
    # Deploy
    echo "🚀 Fazendo deploy do backend..."
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/${PROJECT_ID}/hospicast-backend:latest \
        --platform managed \
        --region $REGION \
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
    
    BACKEND_URL=$(gcloud run services describe $SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --format="value(status.url)")
else
    echo_success "Backend já está deployado!"
fi

echo_success "Backend URL: $BACKEND_URL"

# === 2. CRIAR BUCKET ===
echo ""
echo "📋 Passo 2: Criando bucket para frontend..."
if gsutil ls -b gs://$BUCKET_NAME >/dev/null 2>&1; then
    echo_warning "Bucket já existe: gs://$BUCKET_NAME"
else
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME
    echo_success "Bucket criado: gs://$BUCKET_NAME"
fi

# Configurar como site estático
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
echo_success "Bucket configurado como site estático"

# === 3. CONFIGURAR FRONTEND ===
echo ""
echo "📋 Passo 3: Configurando frontend..."
cd ~/portif-lio

# Criar .env.production
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production
echo_success "Variável de ambiente configurada: VITE_API_BASE_URL=$BACKEND_URL"

# === 4. BUILD FRONTEND ===
echo ""
echo "📋 Passo 4: Fazendo build do frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
fi

echo "🔨 Fazendo build..."
npm run build

if [ ! -d "dist" ]; then
    echo_error "Build falhou! Pasta dist não foi criada."
    exit 1
fi

echo_success "Build concluído!"
cd ..

# === 5. UPLOAD ===
echo ""
echo "📋 Passo 5: Fazendo upload do frontend..."
gsutil -m rsync -r -d frontend/dist gs://$BUCKET_NAME
echo_success "Upload concluído!"

# === 6. CONFIGURAR CORS ===
echo ""
echo "📋 Passo 6: Configurando CORS no backend..."
FRONTEND_URL="https://storage.googleapis.com/$BUCKET_NAME"
gcloud run services update $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --set-env-vars "API_ALLOWED_ORIGINS=$FRONTEND_URL,https://storage.googleapis.com/$BUCKET_NAME,http://storage.googleapis.com/$BUCKET_NAME,*" \
    --quiet

echo_success "CORS configurado!"

# === 7. RESULTADO FINAL ===
echo ""
echo "🎉 Deploy completo concluído!"
echo ""
echo "📋 URLs:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: https://storage.googleapis.com/$BUCKET_NAME/index.html"
echo ""
echo "🌐 Acesse seu frontend no navegador:"
echo "   https://storage.googleapis.com/$BUCKET_NAME/index.html"
echo ""
SCRIPT_END

# Dar permissão de execução
chmod +x scripts/deploy_completo_gcloud.sh

echo "✅ Script criado!"
echo ""
echo "Agora execute:"
echo "  ./scripts/deploy_completo_gcloud.sh"
```

---

## 🚀 Alternativa: Executar Comandos Diretamente

Se preferir não usar o script, execute os comandos diretamente:

```bash
cd ~/portif-lio

# === CONFIGURAÇÃO ===
PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME="hospicast-frontend"

# === 1. VERIFICAR BACKEND ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)" 2>/dev/null || echo "")

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
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

# === 4. BUILD ===
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
echo "Backend:  $BACKEND_URL"
echo "Frontend: https://storage.googleapis.com/$BUCKET_NAME/index.html"
```

---

**Execute os comandos acima no Cloud Shell!** 🎯

