# 🔧 Forçar CORS a Funcionar Definitivamente

## ❌ Problema: CORS Ainda Bloqueando

Mesmo após atualizar `API_ALLOWED_ORIGINS=*`, o CORS ainda está bloqueando. Isso acontece porque o Cloud Run pode não ter reiniciado com a nova configuração.

## ✅ Solução: Forçar Nova Revisão

### Opção 1: Forçar Nova Revisão (Rápido)

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

# Voltar tráfego para a nova revisão
gcloud run services update-traffic hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --to-latest

echo "✅ Nova revisão criada"
```

### Opção 2: Redeploy Completo (Garantido)

Se a Opção 1 não funcionar, faça um redeploy completo:

```bash
cd ~/portif-lio

# === CONFIGURAÇÃO ===
PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"  # Use sua senha

# === BUILD ===
echo "🔨 Fazendo build..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# === DEPLOY COM CORS=* ===
echo "🚀 Fazendo deploy..."
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

## 📋 Comandos Completos - Opção 1 (Rápido)

```bash
# === 1. ATUALIZAR CORS ===
echo "🔄 Atualizando CORS..."
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --quiet

echo "✅ CORS atualizado"
echo ""

# === 2. FORÇAR NOVA REVISÃO ===
echo "🔄 Forçando nova revisão do Cloud Run..."
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --no-traffic \
    --quiet

echo "⏳ Aguardando 10 segundos..."
sleep 10

# Voltar tráfego
gcloud run services update-traffic hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --to-latest

echo "✅ Nova revisão criada e tráfego redirecionado"
echo ""

# === 3. VERIFICAR ===
echo "📋 Verificando configuração:"
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='API_ALLOWED_ORIGINS')].value)"
echo ""

echo "⏳ Aguarde 2-3 minutos para o Cloud Run atualizar completamente..."
echo "💡 Limpe o cache do navegador (Ctrl+Shift+R) e teste novamente"
```

---

## 🧪 Testar CORS Manualmente

Após executar os comandos, teste se o CORS está funcionando:

```bash
# Obter URL do backend
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# Testar CORS
curl -H "Origin: https://storage.googleapis.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     "$BACKEND_URL/forecast/predict" \
     -v 2>&1 | grep -i "access-control"
```

**Deve retornar**:
```
< access-control-allow-origin: *
```

---

## 🔍 Verificar Logs do Backend

Se ainda não funcionar, verifique os logs:

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 30
```

Procure por mensagens relacionadas a CORS ou erros de inicialização.

---

## 🚨 Solução de Emergência: Verificar Código

Se nada funcionar, pode ser um problema no código. Vamos verificar:

```bash
cd ~/portif-lio

# Ver como o CORS está configurado
grep -A 10 "CORSMiddleware" backend/main.py
grep -A 10 "get_allowed_origins_list" backend/core/config.py
```

O código deve estar correto, mas vamos garantir.

---

## ✅ Checklist Final

- [ ] CORS atualizado para `*`
- [ ] Nova revisão criada
- [ ] Aguardou 2-3 minutos
- [ ] Limpou cache do navegador (Ctrl+Shift+R)
- [ ] Testou fazer uma previsão
- [ ] Console não mostra mais erro de CORS
- [ ] Headers da resposta mostram `Access-Control-Allow-Origin: *`

---

**Execute a Opção 1 primeiro. Se não funcionar em 5 minutos, execute a Opção 2 (Redeploy Completo)!** 🎯

