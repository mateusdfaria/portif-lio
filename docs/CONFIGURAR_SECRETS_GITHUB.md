# 🔐 Configurar Secrets no GitHub

## 📋 Secrets Necessários

Para o workflow `.github/workflows/deploy-completo.yml` funcionar, você precisa configurar:

1. **`GCP_SA_KEY`**: Chave JSON da Service Account do Google Cloud
2. **`DATABASE_URL`**: URL de conexão com o PostgreSQL

---

## 🔑 Secret 1: GCP_SA_KEY

### O Que É

Chave JSON da Service Account do Google Cloud que permite ao GitHub Actions fazer deploy no Google Cloud.

### Como Obter

#### Opção 1: Criar Nova Service Account (Recomendado)

```bash
# No Cloud Shell
PROJECT_ID="hospicast-prod"

# Criar service account
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions Deploy" \
    --project=$PROJECT_ID

# Dar permissões necessárias
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Criar chave JSON
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com

# Mostrar chave (copie todo o conteúdo)
cat github-actions-key.json
```

#### Opção 2: Usar Service Account Existente

Se você já tem uma service account:

```bash
# Listar service accounts
gcloud iam service-accounts list

# Criar chave para service account existente
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=SEU_SERVICE_ACCOUNT@${PROJECT_ID}.iam.gserviceaccount.com

# Mostrar chave
cat github-actions-key.json
```

### Como Adicionar no GitHub

1. Acesse: https://github.com/mateusdfaria/portif-lio/settings/secrets/actions
2. Clique em **"New repository secret"**
3. Configure:
   - **Name**: `GCP_SA_KEY`
   - **Secret**: Cole **TODO O CONTEÚDO** do arquivo `github-actions-key.json`
4. Clique em **"Add secret"**

**⚠️ IMPORTANTE**: Cole o JSON completo, incluindo `{` e `}` no início e fim!

---

## 🔑 Secret 2: DATABASE_URL

### O Que É

URL de conexão com o PostgreSQL no Cloud SQL, usada pelo backend para se conectar ao banco.

### Como Obter

```bash
# No Cloud Shell
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DB_PASSWORD="mateus22"  # Use a senha real do banco

# Montar DATABASE_URL
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

echo "DATABASE_URL=$DATABASE_URL"
```

**Exemplo de DATABASE_URL**:
```
postgresql://hospicast_user:SUA_SENHA@localhost/hospicast?host=/cloudsql/hospicast-prod:southamerica-east1:hospicast-db
```

### Como Adicionar no GitHub

1. Acesse: https://github.com/mateusdfaria/portif-lio/settings/secrets/actions
2. Clique em **"New repository secret"**
3. Configure:
   - **Name**: `DATABASE_URL`
   - **Secret**: Cole a URL completa (exemplo acima)
4. Clique em **"Add secret"**

**⚠️ IMPORTANTE**: 
- Use a senha **real** do banco de dados
- A URL deve estar completa e correta
- Não deixe espaços no início ou fim

---

## 📋 Comandos Completos para Obter Secrets

### Obter GCP_SA_KEY

```bash
cd ~/portif-lio

PROJECT_ID="hospicast-prod"

# Criar service account (se não existir)
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions Deploy" \
    --project=$PROJECT_ID 2>/dev/null || echo "Service account já existe"

# Dar permissões
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer" \
    --condition=None

# Criar chave
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com

echo ""
echo "✅ Chave criada! Copie TODO o conteúdo abaixo:"
echo "=========================================="
cat github-actions-key.json
echo "=========================================="
echo ""
echo "💡 Adicione como secret 'GCP_SA_KEY' no GitHub"
```

### Obter DATABASE_URL

```bash
# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")

# Pedir senha
echo "Digite a senha do banco de dados:"
read -s DB_PASSWORD

# Montar URL
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

echo ""
echo "✅ DATABASE_URL gerada:"
echo "=========================================="
echo "$DATABASE_URL"
echo "=========================================="
echo ""
echo "💡 Adicione como secret 'DATABASE_URL' no GitHub"
```

---

## ✅ Verificar Secrets Configurados

### No GitHub

1. Acesse: https://github.com/mateusdfaria/portif-lio/settings/secrets/actions
2. Você deve ver:
   - ✅ `GCP_SA_KEY`
   - ✅ `DATABASE_URL`

### Testar Workflow

1. Acesse: https://github.com/mateusdfaria/portif-lio/actions
2. Clique em "Deploy Completo - Backend + Frontend"
3. Clique em "Run workflow"
4. Se os secrets estiverem corretos, o workflow deve executar com sucesso

---

## 🔒 Segurança

### ⚠️ NUNCA Faça:

- ❌ Commitar secrets no código
- ❌ Compartilhar secrets publicamente
- ❌ Usar secrets em logs públicos
- ❌ Deixar secrets em arquivos `.env` no repositório

### ✅ SEMPRE Faça:

- ✅ Usar GitHub Secrets para valores sensíveis
- ✅ Rotacionar secrets periodicamente
- ✅ Usar service accounts com permissões mínimas necessárias
- ✅ Revisar permissões regularmente

---

## 🔄 Atualizar Secrets

### Atualizar GCP_SA_KEY

Se precisar gerar uma nova chave:

```bash
# Criar nova chave
gcloud iam service-accounts keys create github-actions-key-new.json \
    --iam-account=github-actions@hospicast-prod.iam.gserviceaccount.com

# Mostrar nova chave
cat github-actions-key-new.json

# Adicionar no GitHub (substituir a antiga)
```

### Atualizar DATABASE_URL

Se a senha do banco mudar:

```bash
# Gerar nova URL
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Digite a nova senha:"
read -s DB_PASSWORD
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

echo "$DATABASE_URL"

# Atualizar no GitHub (editar secret existente)
```

---

## 📝 Resumo Rápido

1. **Criar Service Account** (se não existir)
2. **Gerar chave JSON** → Copiar todo o conteúdo
3. **Adicionar no GitHub** como `GCP_SA_KEY`
4. **Gerar DATABASE_URL** → Copiar a URL completa
5. **Adicionar no GitHub** como `DATABASE_URL`
6. **Testar workflow** → Executar manualmente

---

**Configure os secrets acima e seu workflow estará pronto para usar!** 🎯

