# 🚀 Guia de Deploy no Google Cloud - HospiCast

Este guia explica como fazer o deploy do HospiCast no Google Cloud Platform (GCP).

## 📋 Pré-requisitos

1. Conta no Google Cloud Platform
2. Google Cloud SDK instalado (`gcloud`)
3. Projeto criado no GCP
4. Billing habilitado no projeto

## 🏗️ Arquitetura Recomendada

```
┌─────────────────┐
│  Cloud Run      │  ← Backend (FastAPI)
│  (Container)    │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
┌────────▼────────┐  ┌─────▼──────┐
│  Cloud SQL       │  │ Cloud      │
│  (PostgreSQL)    │  │ Storage    │
│                  │  │ (Models)   │
└──────────────────┘  └────────────┘
```

## 📦 Opção 1: Cloud Run + Cloud SQL (Recomendado)

### Passo 1: Criar Instância Cloud SQL (PostgreSQL)

```bash
# Configurar projeto
gcloud config set project SEU_PROJECT_ID

# Criar instância Cloud SQL
gcloud sql instances create hospicast-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=southamerica-east1 \
    --root-password=SUA_SENHA_FORTE

# Criar banco de dados
gcloud sql databases create hospicast --instance=hospicast-db

# Criar usuário
gcloud sql users create hospicast_user \
    --instance=hospicast-db \
    --password=SUA_SENHA_FORTE
```

### Passo 2: Configurar Schema do Banco

```bash
# Obter IP público da instância
gcloud sql instances describe hospicast-db --format="get(ipAddresses[0].ipAddress)"

# Conectar e executar schema
psql -h [IP_PUBLICO] -U hospicast_user -d hospicast -f database/init.sql
```

**OU** usar o script Python:

```bash
# Configurar variável de ambiente
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA@[IP_PUBLICO]:5432/hospicast"

# Executar script de inicialização
cd backend
python scripts/init_database.py
```

### Passo 3: Preparar Dockerfile para Cloud Run

O Dockerfile já está otimizado. Verifique se está correto:

```dockerfile
# backend/Dockerfile já está configurado
```

### Passo 4: Build e Push da Imagem

```bash
# Configurar Docker para usar gcloud
gcloud auth configure-docker

# Build da imagem
gcloud builds submit --tag gcr.io/SEU_PROJECT_ID/hospicast-backend:latest ./backend

# OU usar Cloud Build diretamente
gcloud builds submit --config cloudbuild.yaml
```

### Passo 5: Deploy no Cloud Run

```bash
# Deploy do backend
gcloud run deploy hospicast-backend \
    --image gcr.io/SEU_PROJECT_ID/hospicast-backend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances SEU_PROJECT_ID:southamerica-east1:hospicast-db \
    --set-env-vars "DATABASE_URL=postgresql://hospicast_user:SUA_SENHA@/hospicast?host=/cloudsql/SEU_PROJECT_ID:southamerica-east1:hospicast-db" \
    --set-env-vars "API_ALLOWED_ORIGINS=https://seu-frontend.netlify.app" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10
```

### Passo 6: Configurar Variáveis de Ambiente

No console do Cloud Run, configure:

- `DATABASE_URL`: URL de conexão do Cloud SQL
- `API_ALLOWED_ORIGINS`: URL do frontend
- `LOG_LEVEL`: INFO ou DEBUG
- `PROMETHEUS_ENABLED`: true

## 📦 Opção 2: App Engine (Alternativa)

### Passo 1: Criar app.yaml

```yaml
# app.yaml
runtime: python311

env_variables:
  DATABASE_URL: "postgresql://user:pass@/hospicast?host=/cloudsql/PROJECT_ID:REGION:INSTANCE"
  API_ALLOWED_ORIGINS: "https://seu-frontend.netlify.app"
  LOG_LEVEL: "INFO"

beta_settings:
  cloud_sql_instances: "PROJECT_ID:REGION:INSTANCE"

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

### Passo 2: Deploy

```bash
gcloud app deploy app.yaml
```

## 🔐 Segurança

### 1. Usar Cloud SQL Proxy (Recomendado)

Para conexões locais:

```bash
# Instalar Cloud SQL Proxy
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.linux.amd64
chmod +x cloud-sql-proxy

# Executar proxy
./cloud-sql-proxy SEU_PROJECT_ID:southamerica-east1:hospicast-db
```

### 2. Variáveis de Ambiente Secretas

Use Secret Manager:

```bash
# Criar secret
echo -n "sua-senha-forte" | gcloud secrets create db-password --data-file=-

# Atualizar app.yaml ou Cloud Run para usar secret
```

### 3. IAM e Permissões

```bash
# Dar permissão ao Cloud Run
gcloud projects add-iam-policy-binding SEU_PROJECT_ID \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/cloudsql.client"
```

## 📊 Monitoramento

### Cloud Monitoring

```bash
# Habilitar APIs necessárias
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
```

### Logs

```bash
# Ver logs do Cloud Run
gcloud run services logs read hospicast-backend --limit 50
```

## 💰 Custos Estimados

- **Cloud SQL (db-f1-micro)**: ~$7-10/mês
- **Cloud Run**: Pay-per-use (primeiros 2 milhões de requisições grátis)
- **Cloud Storage** (se usar para modelos): ~$0.02/GB/mês

## 🔄 CI/CD com Cloud Build

Crie `.cloudbuild.yaml`:

```yaml
steps:
  # Build da imagem
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/hospicast-backend:$SHORT_SHA', './backend']
  
  # Push da imagem
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/hospicast-backend:$SHORT_SHA']
  
  # Deploy no Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'hospicast-backend'
      - '--image'
      - 'gcr.io/$PROJECT_ID/hospicast-backend:$SHORT_SHA'
      - '--region'
      - 'southamerica-east1'
      - '--platform'
      - 'managed'
```

## 🐛 Troubleshooting

### Erro de Conexão com Banco

1. Verificar se Cloud SQL está rodando
2. Verificar permissões IAM
3. Verificar se a conexão usa Unix socket (Cloud Run) ou IP público

### Erro de Memória

Aumentar memória no Cloud Run:

```bash
gcloud run services update hospicast-backend \
    --memory 4Gi \
    --region southamerica-east1
```

### Timeout

Aumentar timeout:

```bash
gcloud run services update hospicast-backend \
    --timeout 600 \
    --region southamerica-east1
```

## 📝 Checklist de Deploy

- [ ] Cloud SQL criado e configurado
- [ ] Schema do banco executado
- [ ] Imagem Docker buildada e enviada
- [ ] Cloud Run configurado com variáveis de ambiente
- [ ] Permissões IAM configuradas
- [ ] Frontend apontando para URL do Cloud Run
- [ ] Testes de integração realizados
- [ ] Monitoramento configurado
- [ ] Backup do banco configurado

## 🔗 Links Úteis

- [Documentação Cloud Run](https://cloud.google.com/run/docs)
- [Documentação Cloud SQL](https://cloud.google.com/sql/docs/postgres)
- [Cloud Build](https://cloud.google.com/build/docs)

---

**Última atualização**: Janeiro 2025

