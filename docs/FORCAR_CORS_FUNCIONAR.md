# 🔧 Forçar CORS a Funcionar

## ❌ Problema: CORS Ainda Não Funciona

Mesmo após atualizar a variável de ambiente, o CORS ainda está bloqueando. Isso pode acontecer porque:

1. O Cloud Run precisa ser reiniciado para pegar a nova configuração
2. A variável não foi atualizada corretamente
3. O código precisa ser ajustado

## ✅ Solução: Forçar Atualização e Redeploy

### Passo 1: Verificar Variável Atual

```bash
# Ver qual valor está configurado
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='API_ALLOWED_ORIGINS')].value)"
```

### Passo 2: Atualizar com Wildcard (Garantir que Funciona)

```bash
# Usar wildcard para garantir que funciona
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --quiet

echo "✅ CORS atualizado para * (todas as origens)"
```

### Passo 3: Forçar Nova Revisão (Redeploy)

```bash
# Forçar criação de nova revisão
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --no-traffic \
    --quiet

# Depois voltar o tráfego
gcloud run services update-traffic hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --to-latest

echo "✅ Nova revisão criada e tráfego redirecionado"
```

### Passo 4: Aguardar e Testar

Aguarde 2-3 minutos e teste novamente.

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
# === 1. VERIFICAR VARIÁVEL ATUAL ===
echo "📋 CORS atual:"
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='API_ALLOWED_ORIGINS')].value)"
echo ""

# === 2. ATUALIZAR COM WILDCARD ===
echo "🔄 Atualizando CORS para * (todas as origens)..."
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --quiet

echo "✅ CORS atualizado"
echo ""

# === 3. FORÇAR NOVA REVISÃO ===
echo "🔄 Forçando nova revisão..."
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --no-traffic \
    --quiet

sleep 5

gcloud run services update-traffic hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --to-latest

echo "✅ Nova revisão criada"
echo ""

# === 4. VERIFICAR ===
echo "📋 Verificando nova configuração:"
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='API_ALLOWED_ORIGINS')].value)"
echo ""

echo "⏳ Aguarde 2-3 minutos..."
echo "💡 Limpe o cache do navegador (Ctrl+Shift+R) e teste novamente"
```

---

## 🔍 Alternativa: Verificar Código do CORS

Se ainda não funcionar, pode ser um problema no código. Vamos verificar:

```bash
cd ~/portif-lio

# Ver como o CORS está configurado
grep -A 5 "CORSMiddleware" backend/main.py
grep -A 10 "get_allowed_origins_list" backend/core/config.py
```

---

## 🚨 Solução de Emergência: Redeploy Completo

Se nada funcionar, faça um redeploy completo:

```bash
cd ~/portif-lio

# === CONFIGURAÇÃO ===
PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"  # Use sua senha

# === BUILD ===
echo "🔨 Fazendo build..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# === DEPLOY COM CORS CORRETO ===
echo "🚀 Fazendo deploy..."
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

### 1. Testar CORS Manualmente

```bash
# Testar se CORS está funcionando
curl -H "Origin: https://storage.googleapis.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://hospicast-backend-4705370248.southamerica-east1.run.app/forecast/predict \
     -v 2>&1 | grep -i "access-control"
```

**Deve retornar**:
```
< access-control-allow-origin: *
```

### 2. Verificar no Navegador

1. Limpe o cache: `Ctrl+Shift+R`
2. Abra o console (F12)
3. Tente fazer uma previsão
4. **Não deve mais aparecer erro de CORS**

---

**Execute os comandos acima. Se ainda não funcionar, faça o redeploy completo!** 🎯

