# 💻 Comandos Cloud Shell - Configurar Backend

## 📋 Passo a Passo Completo

### 1. Verificar Configuração Inicial

```bash
# Ver projeto atual
gcloud config get-value project

# Se não estiver no projeto correto, configurar
gcloud config set project hospicast-prod

# Verificar se está logado
gcloud auth list
```

### 2. Navegar para o Diretório do Projeto

```bash
# Ir para o diretório do projeto
cd ~/portif-lio

# Verificar se está no lugar certo
pwd
ls -la
```

### 3. Verificar Status do Backend

```bash
# Ver se o serviço existe
gcloud run services list --region southamerica-east1

# Ver detalhes do serviço
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1
```

### 4. Ver Logs (Para Diagnosticar Problemas)

```bash
# Ver logs recentes
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100
```

### 5. Rebuild da Imagem Docker

```bash
# Obter PROJECT_ID
PROJECT_ID=$(gcloud config get-value project)
echo "Project ID: $PROJECT_ID"

# Fazer build e push da imagem
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend
```

**⏱️ Isso demora 5-10 minutos - não cancele!**

### 6. Obter Informações do Banco de Dados

```bash
# Obter connection name do Cloud SQL
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection name: $CONNECTION_NAME"

# Verificar se o banco existe
gcloud sql instances describe hospicast-db
```

### 7. Deploy no Cloud Run

```bash
# Definir variáveis
PROJECT_ID=$(gcloud config get-value project)
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# Fazer deploy
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
```

### 8. Verificar se Funcionou

```bash
# Obter URL do backend
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "Backend URL: $BACKEND_URL"

# Testar se está funcionando
curl $BACKEND_URL/
```

### 9. Ver Logs Após Deploy

```bash
# Aguardar 1-2 minutos e verificar logs
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

## 📋 Comandos Completos (Copiar e Colar)

```bash
# === 1. CONFIGURAR PROJETO ===
gcloud config set project hospicast-prod
cd ~/portif-lio

# === 2. VERIFICAR STATUS ===
gcloud run services list --region southamerica-east1

# === 3. VER LOGS (se necessário) ===
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100

# === 4. REBUILD DA IMAGEM ===
PROJECT_ID=$(gcloud config get-value project)
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend

# === 5. DEPLOY ===
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASSWORD="mateus22"
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

# === 6. VERIFICAR ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")
echo "Backend URL: $BACKEND_URL"
curl $BACKEND_URL/
```

## 🔍 Comandos Úteis

### Ver Status do Serviço

```bash
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1
```

### Ver Logs em Tempo Real

```bash
gcloud run services logs tail hospicast-backend \
    --platform managed \
    --region southamerica-east1
```

### Atualizar Variáveis de Ambiente

```bash
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "NOVA_VARIAVEL=valor"
```

### Ver Todas as Revisões

```bash
gcloud run revisions list \
    --service hospicast-backend \
    --region southamerica-east1
```

### Deletar Serviço (se necessário)

```bash
gcloud run services delete hospicast-backend \
    --platform managed \
    --region southamerica-east1
```

## ⚠️ Importante

- **Sempre verifique o projeto**: `gcloud config get-value project`
- **Aguarde o build completar**: Não cancele o `gcloud builds submit`
- **Verifique os logs**: Se algo der errado, veja os logs primeiro

---

**Execute os comandos na ordem acima para configurar o backend!**



