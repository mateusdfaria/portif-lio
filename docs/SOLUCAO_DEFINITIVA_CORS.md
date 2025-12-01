# 🔧 Solução Definitiva para CORS

## ❌ Problema: CORS Ainda Bloqueando Após Múltiplas Tentativas

O CORS continua bloqueando mesmo após atualizar `API_ALLOWED_ORIGINS=*`. Isso indica que:
1. A configuração não está sendo aplicada corretamente
2. O Cloud Run precisa ser completamente redeployado
3. Pode haver um problema no código do CORS

## ✅ Solução Definitiva: Redeploy Completo

### Passo 1: Verificar Código do CORS

```bash
cd ~/portif-lio

# Verificar como o CORS está configurado
grep -A 10 "CORSMiddleware" backend/main.py
grep -A 10 "get_allowed_origins_list" backend/core/config.py
```

### Passo 2: Redeploy Completo com Todas as Configurações

```bash
cd ~/portif-lio

# === CONFIGURAÇÃO ===
PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"  # Use a senha correta

# === BUILD ===
echo "🔨 Fazendo build do backend..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# === DEPLOY COMPLETO ===
echo "🚀 Fazendo deploy completo..."
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
    --memory 4Gi \
    --cpu 2 \
    --timeout 900 \
    --max-instances 10 \
    --port 8080 \
    --cpu-boost

# === OBTER NOVA URL ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

BACKEND_URL=${BACKEND_URL%/}

echo ""
echo "✅ Backend redeployado: $BACKEND_URL"
```

### Passo 3: Aguardar e Testar CORS

```bash
# Aguardar 2 minutos
echo "⏳ Aguardando 2 minutos para o backend inicializar..."
sleep 120

# Testar CORS
echo "🧪 Testando CORS..."
curl -H "Origin: https://storage.googleapis.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     "$BACKEND_URL/forecast/predict" \
     -v 2>&1 | grep -i "access-control"
```

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
cd ~/portif-lio

# === CONFIGURAÇÃO ===
PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"  # Use a senha correta do banco
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# === BUILD ===
echo "🔨 Fazendo build do backend..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# === DEPLOY COMPLETO ===
echo "🚀 Fazendo deploy completo do backend..."
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
    --memory 4Gi \
    --cpu 2 \
    --timeout 900 \
    --max-instances 10 \
    --port 8080 \
    --cpu-boost

# === OBTER NOVA URL ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

BACKEND_URL=${BACKEND_URL%/}

echo ""
echo "✅ Backend redeployado: $BACKEND_URL"
echo ""

# === ATUALIZAR FRONTEND ===
echo "🔄 Atualizando frontend com nova URL..."
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

cd frontend
npm run build
cd ..

gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

echo ""
echo "✅ Frontend atualizado"
echo ""

# === TESTAR CORS ===
echo "⏳ Aguardando 2 minutos para o backend inicializar..."
sleep 120

echo "🧪 Testando CORS..."
curl -H "Origin: https://storage.googleapis.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     "$BACKEND_URL/forecast/predict" \
     -v 2>&1 | grep -i "access-control"

echo ""
echo "📋 URLs:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: https://storage.googleapis.com/hospicast-frontend/index.html"
echo ""
echo "💡 Limpe o cache do navegador (Ctrl+Shift+R) e teste novamente"
```

---

## 🔍 Verificar se CORS Está Funcionando

### 1. Testar CORS Manualmente

```bash
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

BACKEND_URL=${BACKEND_URL%/}

curl -H "Origin: https://storage.googleapis.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     "$BACKEND_URL/forecast/predict" \
     -v 2>&1 | grep -i "access-control"
```

**Deve retornar**: `< access-control-allow-origin: *`

### 2. Verificar no Navegador

1. Limpe o cache: `Ctrl+Shift+R`
2. Abra o console: `F12`
3. Tente fazer uma previsão
4. **Não deve aparecer erro de CORS**

### 3. Verificar Headers da Resposta

No DevTools (F12) → Network:
1. Clique na requisição
2. Vá em "Headers" → "Response Headers"
3. Deve ter: `access-control-allow-origin: *`

---

## 🚨 Se Ainda Não Funcionar

### Verificar Código do CORS

```bash
cd ~/portif-lio

# Ver código do CORS
cat backend/main.py | grep -A 10 "CORSMiddleware"
cat backend/core/config.py | grep -A 10 "get_allowed_origins_list"
```

O código deve estar correto, mas vamos verificar.

### Verificar Variáveis de Ambiente

```bash
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env)"
```

**Deve ter**: `API_ALLOWED_ORIGINS=*`

---

## ✅ Sobre os Outros Erros

- **401 (Unauthorized)**: Credenciais incorretas - normal se você não está logado
- **400 (Bad Request)**: Dados inválidos na requisição - verifique os dados enviados
- **422 (Unprocessable Entity)**: Validação falhou - verifique os dados do formulário

Esses erros são diferentes do CORS e podem ser normais dependendo do que você está tentando fazer.

---

**Execute o redeploy completo acima. Isso deve resolver o problema de CORS definitivamente!** 🎯

