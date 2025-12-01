# 🔍 Diagnosticar Erro 500 (Internal Server Error)

## ❌ Erro: 500 Internal Server Error

O backend está retornando erro 500 ao processar `/forecast/predict`. Precisamos ver os logs para identificar o problema.

## ✅ Solução: Verificar Logs e Corrigir

### Passo 1: Ver Logs Detalhados

```bash
# Ver logs recentes do backend
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

### Passo 2: Ver Logs em Tempo Real (Opcional)

```bash
# Ver logs em tempo real (Ctrl+C para parar)
gcloud run services logs tail hospicast-backend \
    --platform managed \
    --region southamerica-east1
```

### Passo 3: Filtrar Logs por Erro

```bash
# Ver apenas erros
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100 | grep -i "error\|exception\|traceback\|failed"
```

---

## 🔍 Problemas Comuns e Soluções

### Problema 1: Erro de Conexão com Banco

**Sintoma nos logs**: `password authentication failed` ou `connection failed`

**Solução**:
```bash
# Resetar senha
NEW_PASSWORD="SuaNovaSenhaForte123!"
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=$NEW_PASSWORD

# Atualizar Cloud Run
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DATABASE_URL="postgresql://hospicast_user:${NEW_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL},API_ALLOWED_ORIGINS=*,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" \
    --quiet
```

### Problema 2: Erro de CmdStan/Prophet

**Sintoma nos logs**: `CmdStan` ou `Prophet` ou `make build failed`

**Solução**: O CmdStan já deve estar instalado no Dockerfile, mas pode ter falhado. Verifique se o build foi bem-sucedido.

### Problema 3: Erro de Memória

**Sintoma nos logs**: `MemoryError` ou `out of memory`

**Solução**: Aumentar memória do Cloud Run:
```bash
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --memory 4Gi \
    --quiet
```

### Problema 4: Erro de Timeout

**Sintoma nos logs**: `timeout` ou requisição demora muito

**Solução**: Aumentar timeout:
```bash
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --timeout 900 \
    --quiet
```

### Problema 5: Erro de Validação de Dados

**Sintoma nos logs**: `ValidationError` ou `ValueError`

**Solução**: Verificar os dados enviados pelo frontend. Pode ser necessário ajustar o código.

---

## 📋 Comandos Completos para Diagnóstico

```bash
# === 1. VER LOGS RECENTES ===
echo "📋 Logs recentes do backend:"
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50

echo ""
echo "🔍 Procure por:"
echo "   - 'error' ou 'Error'"
echo "   - 'exception' ou 'Exception'"
echo "   - 'traceback' ou 'Traceback'"
echo "   - 'failed' ou 'Failed'"
echo ""

# === 2. VER APENAS ERROS ===
echo "📋 Apenas erros:"
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100 | grep -i "error\|exception\|traceback\|failed" | head -20

echo ""
echo "💡 Copie os erros acima e me envie para eu ajudar melhor!"
```

---

## 🧪 Testar Endpoint Diretamente

```bash
# Testar endpoint diretamente
BACKEND_URL="https://hospicast-backend-fbuqwglmsq-rj.a.run.app"

# Testar endpoint raiz
curl -v "$BACKEND_URL/"

# Testar endpoint de previsão (vai dar erro, mas vamos ver qual)
curl -X POST "$BACKEND_URL/forecast/predict" \
     -H "Content-Type: application/json" \
     -d '{"series_id":"test","horizon":14,"latitude":-26.3044,"longitude":-48.8456}' \
     -v
```

---

## 🔄 Redeploy Completo (Se Nada Funcionar)

Se não conseguir identificar o problema, faça um redeploy completo:

```bash
cd ~/portif-lio

PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"  # Use a senha correta

# Build
echo "🔨 Fazendo build..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# Deploy
echo "🚀 Fazendo deploy..."
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

gcloud run deploy hospicast-backend \
    --image gcr.io/${PROJECT_ID}/hospicast-backend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances ${CONNECTION_NAME} \
    --set-env-vars "DATABASE_URL=${DATABASE_URL},API_ALLOWED_ORIGINS=*,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" \
    --memory 4Gi \
    --cpu 2 \
    --timeout 900 \
    --max-instances 10 \
    --port 8080 \
    --cpu-boost

echo "✅ Redeploy completo concluído"
```

---

## ✅ Após Ver os Logs

**Me envie**:
1. Os erros que apareceram nos logs
2. A mensagem de erro completa
3. Qualquer traceback que aparecer

Com essas informações, posso ajudar a corrigir o problema específico!

---

**Execute os comandos acima para ver os logs e me envie o que aparecer!** 🎯

