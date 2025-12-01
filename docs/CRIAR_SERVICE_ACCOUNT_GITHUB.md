# 🔧 Criar Service Account para GitHub Actions

## ❌ Erro: Service Account não existe

O erro indica que a service account `github-action-983769709@hospicast-prod.iam.gserviceaccount.com` não existe.

## ✅ Solução: Criar Service Account

### Passo 1: Criar Service Account

```bash
# No Cloud Shell ou localmente com gcloud configurado
PROJECT_ID="hospicast-prod"

# Criar service account
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions Deploy" \
    --project=$PROJECT_ID
```

### Passo 2: Dar Permissões Necessárias

```bash
# Dar permissão de Cloud Run Admin
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Dar permissão de Storage Admin (para Container Registry)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Dar permissão de Service Account User
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Dar permissão de Cloud SQL Client (para acessar banco)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# Dar permissão de Cloud Build (se usar Cloud Build)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.editor"
```

### Passo 3: Criar e Baixar Chave JSON

```bash
# Criar chave JSON
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com

# Ver a chave (copiar todo o conteúdo)
cat github-actions-key.json
```

### Passo 4: Adicionar Secret no GitHub

1. Ir para: https://github.com/mateusdfaria/portif-lio/settings/secrets/actions
2. Clicar em "New repository secret"
3. Nome: `GCP_SA_KEY`
4. Valor: Cole todo o conteúdo do arquivo `github-actions-key.json`

## 📋 Comandos Completos (Copiar e Colar)

```bash
# === 1. DEFINIR VARIÁVEIS ===
PROJECT_ID="hospicast-prod"

# === 2. CRIAR SERVICE ACCOUNT ===
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions Deploy" \
    --project=$PROJECT_ID

# === 3. DAR PERMISSÕES ===
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# === 4. CRIAR CHAVE JSON ===
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com

# === 5. VER CHAVE ===
cat github-actions-key.json
```

## 🔍 Verificar Service Accounts Existentes

```bash
# Listar todas as service accounts
gcloud iam service-accounts list --project=$PROJECT_ID

# Ver detalhes de uma service account
gcloud iam service-accounts describe github-actions@$PROJECT_ID.iam.gserviceaccount.com
```

## ⚠️ Se a Service Account Já Existir

Se você já tem uma service account diferente, pode usar ela:

```bash
# Listar service accounts
gcloud iam service-accounts list --project=$PROJECT_ID

# Criar nova chave para service account existente
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=SUA_SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com
```

## 🔐 Segurança

Após adicionar a chave no GitHub:
- ✅ **NÃO** commitar o arquivo `github-actions-key.json` no Git
- ✅ **DELETAR** o arquivo local após copiar para GitHub
- ✅ A chave está no `.gitignore` (verificar)

---

**Execute os comandos acima para criar a service account!**



