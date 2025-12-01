# 🔧 Corrigir Todos os Problemas de Uma Vez

## ❌ Problemas Identificados

1. **CORS ainda bloqueando** - Backend não está enviando header CORS
2. **Barra dupla na URL** - `//forecast/predict` (URL termina com `/` e código adiciona `/`)
3. **URL antiga ainda sendo usada** - `hospicast-backend-4705370248.southamerica-east1.run.app`
4. **Erro 401** - Autenticação (problema secundário)
5. **Erro 422** - Validação (problema secundário)

## ✅ Solução Completa

### Passo 1: Obter URL Correta do Backend

```bash
# Obter URL atual (sem barra final)
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# Remover barra final
BACKEND_URL=${BACKEND_URL%/}

echo "✅ URL do backend: $BACKEND_URL"
```

### Passo 2: Redeploy Completo do Backend com CORS

```bash
cd ~/portif-lio

PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"  # Use sua senha

# Build
echo "🔨 Fazendo build..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# Deploy com CORS=* e todas as variáveis
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

echo "🚀 Fazendo deploy..."
gcloud run deploy hospicast-backend \
    --image gcr.io/${PROJECT_ID}/hospicast-backend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances ${CONNECTION_NAME} \
    --set-env-vars "DATABASE_URL=${DATABASE_URL},API_ALLOWED_ORIGINS=*,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 600 \
    --max-instances 10 \
    --port 8080 \
    --cpu-boost

# Obter nova URL
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

BACKEND_URL=${BACKEND_URL%/}

echo "✅ Backend redeployado: $BACKEND_URL"
```

### Passo 3: Atualizar Frontend com URL Correta (Sem Barra Final)

```bash
# Atualizar .env.production (sem barra final)
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

echo "✅ .env.production atualizado:"
cat frontend/.env.production
```

### Passo 4: Rebuild e Reupload do Frontend

```bash
# Rebuild
cd frontend
npm run build
cd ..

# Reupload
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

echo "✅ Frontend atualizado"
```

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
cd ~/portif-lio

# === 1. CONFIGURAÇÃO ===
PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"  # Use sua senha
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# === 2. BUILD BACKEND ===
echo "🔨 Fazendo build do backend..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# === 3. DEPLOY BACKEND COM CORS=* ===
echo "🚀 Fazendo deploy do backend..."
gcloud run deploy hospicast-backend \
    --image gcr.io/${PROJECT_ID}/hospicast-backend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances ${CONNECTION_NAME} \
    --set-env-vars "DATABASE_URL=${DATABASE_URL},API_ALLOWED_ORIGINS=*,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 600 \
    --max-instances 10 \
    --port 8080 \
    --cpu-boost

# === 4. OBTER URL DO BACKEND (SEM BARRA FINAL) ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

BACKEND_URL=${BACKEND_URL%/}

echo ""
echo "✅ Backend deployado: $BACKEND_URL"
echo ""

# === 5. ATUALIZAR FRONTEND ===
echo "🔄 Atualizando frontend..."
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

echo "✅ .env.production:"
cat frontend/.env.production
echo ""

# === 6. REBUILD FRONTEND ===
echo "🏗️  Fazendo build do frontend..."
cd frontend
npm run build
cd ..

# === 7. REUPLOAD FRONTEND ===
echo "📤 Fazendo upload do frontend..."
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

# === 8. RESULTADO ===
echo ""
echo "✅ Tudo atualizado!"
echo ""
echo "📋 URLs:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: https://storage.googleapis.com/hospicast-frontend/index.html"
echo ""
echo "⏳ Aguarde 2-3 minutos para o backend inicializar..."
echo "💡 Limpe o cache do navegador (Ctrl+Shift+R) e teste novamente"
```

---

## 🧪 Testar CORS Após Deploy

```bash
# Obter URL do backend
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

BACKEND_URL=${BACKEND_URL%/}

# Testar CORS
echo "🧪 Testando CORS..."
curl -H "Origin: https://storage.googleapis.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     "$BACKEND_URL/forecast/predict" \
     -v 2>&1 | grep -i "access-control"
```

**Deve retornar**: `< access-control-allow-origin: *`

---

## ✅ Verificar se Funcionou

### 1. No Navegador (F12 → Network)

1. Limpe o cache: `Ctrl+Shift+R`
2. Tente fazer uma previsão
3. Veja a URL da requisição:
   - ✅ Deve ser: `https://hospicast-backend-...a.run.app/forecast/predict`
   - ❌ NÃO deve ser: `https://hospicast-backend-...a.run.app//forecast/predict` (barra dupla)
   - ❌ NÃO deve ser: `https://hospicast-backend-4705370248...` (URL antiga)

### 2. Verificar Headers

1. Clique na requisição
2. Vá em "Headers"
3. Procure por `Access-Control-Allow-Origin`
4. Deve ter: `*`

### 3. Verificar Console

1. Console (F12)
2. Não deve aparecer:
   - ❌ Erro de CORS
   - ❌ "Failed to fetch"
   - ❌ Barra dupla na URL

---

## 🔍 Sobre os Erros 401 e 422

Esses são problemas diferentes:

- **401 (Unauthorized)**: Credenciais incorretas ou token inválido
- **422 (Unprocessable Entity)**: Dados de validação incorretos no registro

Esses erros são normais se:
- Você está tentando fazer login com credenciais erradas
- Está tentando registrar um hospital com dados inválidos

**Foque primeiro em resolver o CORS e a barra dupla. Depois podemos tratar os erros 401/422.**

---

**Execute os comandos acima para corrigir tudo de uma vez!** 🎯

