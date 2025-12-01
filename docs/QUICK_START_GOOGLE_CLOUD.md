# ⚡ Quick Start - Google Cloud

Guia rápido para fazer deploy no Google Cloud em 10 minutos.

## 🎯 Passos Rápidos

### 1. Instalar Google Cloud SDK

**Windows:**
```powershell
# Baixar de: https://cloud.google.com/sdk/docs/install
# Ou usar Chocolatey:
choco install gcloudsdk
```

**Linux/Mac:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 2. Autenticar e Criar Projeto

```bash
# Login
gcloud auth login

# Criar projeto
gcloud projects create hospicast-prod --name="HospiCast"

# Configurar projeto
gcloud config set project hospicast-prod
```

**Anote o PROJECT_ID** (ex: `hospicast-prod-123456`)

### 3. Habilitar Billing

1. Acesse: https://console.cloud.google.com/billing
2. Vincule uma conta de billing ao projeto

### 4. Criar Banco de Dados

```bash
# Criar instância PostgreSQL
gcloud sql instances create hospicast-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=southamerica-east1 \
    --root-password=SUA_SENHA_FORTE

# Criar banco
gcloud sql databases create hospicast --instance=hospicast-db

# Criar usuário
gcloud sql users create hospicast_user \
    --instance=hospicast-db \
    --password=OUTRA_SENHA_FORTE
```

### 5. Configurar Schema

```bash
# Obter IP público
gcloud sql instances describe hospicast-db --format="get(ipAddresses[0].ipAddress)"

# Configurar variável (substitua IP e SENHA)
export DATABASE_URL="postgresql://hospicast_user:SENHA@[IP]:5432/hospicast"

# Inicializar banco
cd backend
python scripts/init_database.py
```

### 6. Deploy Automático

**Windows (PowerShell):**
```powershell
.\scripts\deploy_gcloud.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/deploy_gcloud.sh
./scripts/deploy_gcloud.sh
```

**OU manualmente:**

```bash
# Habilitar APIs
gcloud services enable run.googleapis.com sqladmin.googleapis.com cloudbuild.googleapis.com

# Build e push
gcloud builds submit --tag gcr.io/$PROJECT_ID/hospicast-backend:latest ./backend

# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")

# Deploy
gcloud run deploy hospicast-backend \
    --image gcr.io/$PROJECT_ID/hospicast-backend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars "DATABASE_URL=postgresql://hospicast_user:SENHA@localhost/hospicast?host=/cloudsql/$CONNECTION_NAME" \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --memory 2Gi \
    --cpu 2
```

### 7. Obter URL

```bash
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)"
```

### 8. Testar

```bash
curl https://hospicast-backend-xxxxx-uc.a.run.app/
```

Deve retornar: `{"message": "HospiCast API funcionando!"}`

## ✅ Pronto!

Agora você tem:
- ✅ Backend rodando no Cloud Run
- ✅ Banco PostgreSQL no Cloud SQL
- ✅ URL pública da API

**Próximo passo**: Atualizar o frontend para usar a nova URL da API.

## 📚 Documentação Completa

Para mais detalhes, consulte:
- `GOOGLE_CLOUD_SETUP_PASSO_A_PASSO.md` - Guia detalhado passo a passo
- `GOOGLE_CLOUD_DEPLOY.md` - Documentação técnica completa

## 🆘 Problemas?

### Erro: "Permission denied"
```bash
gcloud auth login
gcloud config set project SEU_PROJECT_ID
```

### Erro: "Billing not enabled"
Habilite billing em: https://console.cloud.google.com/billing

### Erro: "API not enabled"
```bash
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

---

**Tempo estimado**: 10-15 minutos
**Custo mensal**: ~R$ 40-60

