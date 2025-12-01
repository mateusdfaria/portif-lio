# 🔧 Corrigir Variáveis para Deploy

## ❌ Problema na Sintaxe

Você escreveu:
```bash
DATABASE_URL="postgresql://hospicast_user:${mateus22}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"
```

**Problemas:**
1. `${mateus22}` está errado - deve ser apenas a senha sem `${}`
2. Precisa definir `CONNECTION_NAME` primeiro
3. Precisa executar o build antes

## ✅ Solução: Passo a Passo Correto

### Passo 1: Verificar se Build Foi Executado

```bash
# Verificar se a imagem foi criada
gcloud container images list --repository=gcr.io/$(gcloud config get-value project)
```

Se não aparecer nada, você precisa fazer o build primeiro:

```bash
# Build e push da imagem (pode levar 5-10 minutos)
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/hospicast-backend:latest ./backend
```

### Passo 2: Obter Connection Name

```bash
# Obter connection name do Cloud SQL
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection name: $CONNECTION_NAME"
```

### Passo 3: Definir Variáveis Corretamente

```bash
# Definir PROJECT_ID
PROJECT_ID=$(gcloud config get-value project)

# Definir senha (substitua mateus22 pela senha real, SEM ${})
DB_PASSWORD="mateus22"

# Construir DATABASE_URL corretamente
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# Verificar se está correto
echo "DATABASE_URL: $DATABASE_URL"
```

### Passo 4: Deploy no Cloud Run

```bash
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
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10
```

## 📋 Script Completo (Copie e Cole)

```bash
#!/bin/bash

# 1. Verificar projeto
PROJECT_ID=$(gcloud config get-value project)
echo "✅ Projeto: $PROJECT_ID"

# 2. Verificar se build foi feito
echo "🔍 Verificando se imagem existe..."
gcloud container images list --repository=gcr.io/${PROJECT_ID} | grep hospicast-backend

# Se não existir, fazer build
if [ $? -ne 0 ]; then
    echo "🔨 Fazendo build da imagem..."
    gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend
fi

# 3. Obter connection name
echo "🗄️  Obtendo connection name..."
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "✅ Connection name: $CONNECTION_NAME"

# 4. Definir variáveis
DB_PASSWORD="mateus22"  # Substitua pela senha real
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# 5. Verificar variáveis
echo "📋 Variáveis configuradas:"
echo "   DATABASE_URL: postgresql://hospicast_user:***@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# 6. Deploy
echo "🚀 Fazendo deploy no Cloud Run..."
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
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10

# 7. Obter URL
SERVICE_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo ""
echo "✅ Deploy concluído!"
echo "🌐 URL do serviço: $SERVICE_URL"
```

## ⚠️ Importante

- **Senha**: Use apenas a senha, sem `${}` ao redor
- **Connection Name**: Precisa ser obtido primeiro
- **Build**: Precisa ser feito antes do deploy

---

**Execute os comandos acima na ordem correta!**

