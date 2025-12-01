# 🔧 Corrigir Erros Finais - CORS, 500 e 401

## ❌ Problemas Identificados

1. **CORS ainda bloqueando** - Backend não está enviando header CORS
2. **Erro 500 (Internal Server Error)** - Backend está com erro ao processar
3. **Erro 401** - Autenticação (problema secundário)

## ✅ Solução Completa

### Passo 1: Verificar Logs do Backend (Para Ver Erro 500)

```bash
# Ver logs recentes para identificar o erro 500
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

### Passo 2: Forçar Nova Revisão com CORS

```bash
# === 1. ATUALIZAR CORS ===
echo "🔄 Atualizando CORS..."
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --quiet

# === 2. FORÇAR NOVA REVISÃO ===
echo "🔄 Forçando nova revisão..."
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --no-traffic \
    --quiet

sleep 10

# Voltar tráfego
gcloud run services update-traffic hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --to-latest

echo "✅ Nova revisão criada"
```

### Passo 3: Verificar Todas as Variáveis de Ambiente

```bash
# Ver todas as variáveis de ambiente
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env)"
```

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
# === 1. VER LOGS (PARA IDENTIFICAR ERRO 500) ===
echo "📋 Verificando logs do backend..."
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 30

echo ""
echo "🔍 Procure por erros acima. Se houver erro de senha do banco, execute o passo 2."
echo ""

# === 2. ATUALIZAR CORS E FORÇAR NOVA REVISÃO ===
echo "🔄 Atualizando CORS e forçando nova revisão..."
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --quiet

sleep 5

gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --no-traffic \
    --quiet

sleep 10

gcloud run services update-traffic hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --to-latest

echo "✅ Nova revisão criada"
echo ""

# === 3. VERIFICAR CONFIGURAÇÃO ===
echo "📋 Verificando configuração:"
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='API_ALLOWED_ORIGINS')].value)"
echo ""

echo "⏳ Aguarde 2-3 minutos para o Cloud Run atualizar completamente..."
echo "💡 Depois, limpe o cache do navegador (Ctrl+Shift+R) e teste novamente"
```

---

## 🔍 Se o Erro 500 for de Senha do Banco

Se nos logs aparecer `password authentication failed`, execute:

```bash
# === RESETAR SENHA ===
NEW_PASSWORD="SuaNovaSenhaForte123!"  # Escolha uma senha forte

gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=$NEW_PASSWORD

# === ATUALIZAR CLOUD RUN ===
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DATABASE_URL="postgresql://hospicast_user:${NEW_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL},API_ALLOWED_ORIGINS=*,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" \
    --quiet

echo "✅ Senha resetada e Cloud Run atualizado"
```

---

## 🧪 Testar CORS Após Atualizar

```bash
# Testar CORS
curl -H "Origin: https://storage.googleapis.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://hospicast-backend-fbuqwglmsq-rj.a.run.app/forecast/predict \
     -v 2>&1 | grep -i "access-control"
```

**Deve retornar**: `< access-control-allow-origin: *`

---

## 🔄 Redeploy Completo (Se Nada Funcionar)

Se após 5 minutos ainda não funcionar, faça um redeploy completo:

```bash
cd ~/portif-lio

PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"  # Use a senha correta

# Build
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# Deploy
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

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

echo "✅ Redeploy completo concluído"
```

---

## ✅ Verificar se Funcionou

### 1. Aguardar Atualização

Aguarde 2-3 minutos para o Cloud Run atualizar completamente.

### 2. Limpar Cache do Navegador

`Ctrl+Shift+R` (ou `Cmd+Shift+R` no Mac)

### 3. Testar no Navegador

1. Acesse o frontend
2. Tente fazer uma previsão
3. Verifique o console (F12)
4. **Não deve mais aparecer**:
   - ❌ Erro de CORS
   - ❌ Erro 500
   - ❌ "Failed to fetch"

### 4. Verificar Logs

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 20
```

---

**Execute os comandos acima e me envie os logs se o erro 500 persistir!** 🎯

