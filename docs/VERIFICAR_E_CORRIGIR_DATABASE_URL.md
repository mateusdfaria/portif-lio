# 🔍 Verificar e Corrigir DATABASE_URL

## ❌ Problema: DATABASE_URL Não Está Configurada

Se o comando não retornou nada, significa que a `DATABASE_URL` não está configurada no Cloud Run.

## ✅ Solução: Verificar e Configurar

### Passo 1: Ver Todas as Variáveis de Ambiente

```bash
# Ver todas as variáveis de ambiente
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env)"
```

### Passo 2: Ver Variáveis Individualmente

```bash
# Ver API_ALLOWED_ORIGINS
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='API_ALLOWED_ORIGINS')].value)"

# Ver DATABASE_URL
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DATABASE_URL')].value)"

# Ver LOG_LEVEL
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='LOG_LEVEL')].value)"
```

### Passo 3: Configurar DATABASE_URL

```bash
# === 1. RESETAR SENHA ===
NEW_PASSWORD="HospiCast2024!SenhaForte"  # Escolha uma senha forte

echo "🔐 Resetando senha do banco..."
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=$NEW_PASSWORD

echo "✅ Senha resetada"
echo ""

# === 2. OBTER CONNECTION NAME ===
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"
echo ""

# === 3. MONTAR DATABASE_URL ===
DB_PASSWORD="$NEW_PASSWORD"
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

echo "DATABASE_URL gerada:"
echo "$DATABASE_URL"
echo ""

# === 4. ATUALIZAR CLOUD RUN COM TODAS AS VARIÁVEIS ===
echo "🔄 Atualizando Cloud Run com todas as variáveis..."
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL},API_ALLOWED_ORIGINS=*,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" \
    --quiet

echo "✅ Cloud Run atualizado"
```

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
# === 1. VER TODAS AS VARIÁVEIS ===
echo "📋 Variáveis de ambiente atuais:"
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env)"
echo ""

# === 2. RESETAR SENHA ===
NEW_PASSWORD="HospiCast2024!SenhaForte"  # Escolha uma senha forte

echo "🔐 Resetando senha do banco..."
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=$NEW_PASSWORD

echo "✅ Senha resetada: $NEW_PASSWORD"
echo ""

# === 3. OBTER CONNECTION NAME ===
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"
echo ""

# === 4. MONTAR DATABASE_URL ===
DB_PASSWORD="$NEW_PASSWORD"
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

echo "DATABASE_URL gerada:"
echo "$DATABASE_URL"
echo ""

# === 5. ATUALIZAR CLOUD RUN ===
echo "🔄 Atualizando Cloud Run com todas as variáveis..."
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL},API_ALLOWED_ORIGINS=*,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" \
    --quiet

echo "✅ Cloud Run atualizado"
echo ""

# === 6. VERIFICAR NOVAMENTE ===
echo "📋 Verificando DATABASE_URL após atualização:"
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DATABASE_URL')].value)"
echo ""

echo "⏳ Aguarde 1-2 minutos para o Cloud Run atualizar..."
echo "💡 Depois, tente cadastrar o hospital novamente"
```

---

## 🔍 Verificar Todas as Variáveis

### Ver Formato Completo

```bash
# Ver todas as variáveis em formato legível
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="yaml(spec.template.spec.containers[0].env)"
```

### Ver Apenas Nomes das Variáveis

```bash
# Ver apenas os nomes das variáveis configuradas
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[*].name)"
```

---

## 🚨 Se Ainda Não Funcionar

### Opção 1: Redeploy Completo

```bash
cd ~/portif-lio

PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="HospiCast2024!SenhaForte"  # Use a senha que você definiu

# Build
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# Deploy com todas as variáveis
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

### Opção 2: Verificar Logs

```bash
# Ver logs para entender o problema
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 30
```

---

## ✅ Checklist

- [ ] Verificou todas as variáveis de ambiente
- [ ] DATABASE_URL não estava configurada
- [ ] Resetou senha do banco
- [ ] Montou DATABASE_URL correta
- [ ] Atualizou Cloud Run com todas as variáveis
- [ ] Verificou novamente (agora deve mostrar a URL)
- [ ] Aguardou 1-2 minutos
- [ ] Testou cadastrar hospital

---

**Execute os comandos acima para verificar e configurar a DATABASE_URL!** 🎯

