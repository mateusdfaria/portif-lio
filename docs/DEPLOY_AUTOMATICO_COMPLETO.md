# 🚀 Deploy Automático Completo - HospiCast

Guia passo a passo para fazer deploy automático no Google Cloud Run.

## 📋 Pré-requisitos

- ✅ Cloud SQL configurado (já feito!)
- ✅ Banco inicializado (já feito!)
- ✅ gcloud instalado e configurado
- ✅ Projeto Google Cloud configurado

## 🎯 Deploy Automático - Passo a Passo

### Passo 1: Verificar Configuração

```bash
# Verificar projeto
gcloud config get-value project

# Se não estiver configurado:
gcloud config set project hospicast-prod
```

### Passo 2: Habilitar APIs Necessárias

```bash
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Passo 3: Configurar Docker

```bash
gcloud auth configure-docker
```

### Passo 4: Build e Push da Imagem

```bash
# Build e push da imagem Docker
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/hospicast-backend:latest ./backend
```

**⏱️ Isso pode levar 5-10 minutos**

### Passo 5: Obter Connection Name do Cloud SQL

```bash
# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection name: $CONNECTION_NAME"
```

### Passo 6: Preparar Variáveis

```bash
# Definir PROJECT_ID
PROJECT_ID=$(gcloud config get-value project)

# Você precisará da senha do banco (a mesma que usou no DATABASE_URL)
# Substitua SUA_SENHA pela senha real
DB_PASSWORD="SUA_SENHA"

# Construir DATABASE_URL para Cloud Run
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# Origens permitidas (CORS)
ALLOWED_ORIGINS="*"  # Ou coloque a URL do seu frontend
```

### Passo 7: Deploy no Cloud Run

```bash
gcloud run deploy hospicast-backend \
    --image gcr.io/${PROJECT_ID}/hospicast-backend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances ${CONNECTION_NAME} \
    --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
    --set-env-vars "API_ALLOWED_ORIGINS=${ALLOWED_ORIGINS}" \
    --set-env-vars "LOG_LEVEL=INFO" \
    --set-env-vars "PROMETHEUS_ENABLED=true" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0
```

### Passo 8: Obter URL do Serviço

```bash
# Obter URL
SERVICE_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "✅ Deploy concluído!"
echo "🌐 URL do serviço: $SERVICE_URL"
```

### Passo 9: Testar

```bash
# Testar endpoint
curl $SERVICE_URL/

# Deve retornar: {"message": "HospiCast API funcionando!"}
```

## 📝 Script Completo (Copie e Cole)

```bash
#!/bin/bash
# Deploy Automático HospiCast

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy automático..."

# 1. Verificar projeto
PROJECT_ID=$(gcloud config get-value project)
echo "✅ Projeto: $PROJECT_ID"

# 2. Habilitar APIs
echo "📦 Habilitando APIs..."
gcloud services enable run.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

# 3. Configurar Docker
echo "🐳 Configurando Docker..."
gcloud auth configure-docker --quiet

# 4. Build e push
echo "🔨 Fazendo build da imagem..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# 5. Obter connection name
echo "🗄️  Obtendo connection name..."
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "✅ Connection name: $CONNECTION_NAME"

# 6. Solicitar senha
read -sp "Digite a senha do banco de dados: " DB_PASSWORD
echo ""

read -p "Digite as origens permitidas (CORS) [*]: " ALLOWED_ORIGINS
ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-"*"}

# 7. Construir DATABASE_URL
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# 8. Deploy
echo "🚀 Fazendo deploy no Cloud Run..."
gcloud run deploy hospicast-backend \
    --image gcr.io/${PROJECT_ID}/hospicast-backend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances ${CONNECTION_NAME} \
    --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
    --set-env-vars "API_ALLOWED_ORIGINS=${ALLOWED_ORIGINS}" \
    --set-env-vars "LOG_LEVEL=INFO" \
    --set-env-vars "PROMETHEUS_ENABLED=true" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0

# 9. Obter URL
SERVICE_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo ""
echo "✅ Deploy concluído!"
echo "🌐 URL do serviço: $SERVICE_URL"
echo ""
echo "Teste o endpoint:"
echo "curl $SERVICE_URL/"
echo ""
echo "Atualize o frontend para usar esta URL!"
```

## 🎯 Executar Deploy

### Opção 1: Executar Passo a Passo

Execute os comandos acima um por um no Cloud Shell ou terminal com gcloud.

### Opção 2: Salvar como Script

1. Salve o script acima em um arquivo `deploy.sh`
2. Dê permissão de execução:
   ```bash
   chmod +x deploy.sh
   ```
3. Execute:
   ```bash
   ./deploy.sh
   ```

## ⚠️ Importante

- **Senha do banco**: Use a mesma senha que você configurou no `hospicast_user`
- **Tempo de build**: O build da imagem pode levar 5-10 minutos
- **Custos**: Cloud Run cobra por uso, Cloud SQL tem custo fixo

## ✅ Depois do Deploy

1. Anote a URL do serviço
2. Atualize o frontend para usar essa URL
3. Teste os endpoints da API

---

**Execute os comandos acima para fazer o deploy automático!**

