# 🚀 Configurar Deploy Automático no GitHub

## 📋 O que foi criado

Foi criado um workflow do GitHub Actions (`.github/workflows/deploy-cloud-run.yml`) que faz deploy automático no Google Cloud Run quando você faz push no branch `main`.

## ✅ Pré-requisitos

### 1. Criar Service Account no Google Cloud

```bash
# No Cloud Shell ou localmente com gcloud configurado
PROJECT_ID="hospicast-prod"

# Criar service account
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions Deploy" \
    --project=$PROJECT_ID

# Dar permissões necessárias
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

# Criar e baixar chave JSON
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com

# Ver a chave (copiar todo o conteúdo)
cat github-actions-key.json
```

### 2. Adicionar Secrets no GitHub

1. Ir para: https://github.com/mateusdfaria/portif-lio/settings/secrets/actions
2. Clicar em "New repository secret"
3. Adicionar os seguintes secrets:

#### `GCP_SA_KEY`
- **Nome**: `GCP_SA_KEY`
- **Valor**: Cole todo o conteúdo do arquivo `github-actions-key.json` (criado acima)

#### `DATABASE_URL`
- **Nome**: `DATABASE_URL`
- **Valor**: A URL completa do banco de dados
  ```bash
  # Obter connection name
  CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
  
  # DATABASE_URL será:
  postgresql://hospicast_user:SUA_SENHA@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}
  ```

## 🔄 Como Funciona

O workflow é acionado automaticamente quando:
- Você faz push no branch `main`
- Você faz push de mudanças em arquivos do `backend/`
- Você aciona manualmente via "Run workflow" no GitHub

### O que o workflow faz:

1. ✅ Faz checkout do código
2. ✅ Autentica no Google Cloud usando a service account
3. ✅ Configura Docker para usar Google Container Registry
4. ✅ Obtém o connection name do Cloud SQL
5. ✅ Faz build da imagem Docker
6. ✅ Faz push da imagem para GCR
7. ✅ Faz deploy no Cloud Run
8. ✅ Testa se o deploy funcionou

## 📋 Verificar se Está Funcionando

### 1. Ver Workflows no GitHub

1. Ir para: https://github.com/mateusdfaria/portif-lio/actions
2. Você verá os workflows executando
3. Clicar em um workflow para ver os logs

### 2. Testar Manualmente

```bash
# Fazer uma mudança pequena e fazer commit
echo "# Test" >> README.md
git add README.md
git commit -m "test: testar deploy automático"
git push origin main
```

### 3. Ver Logs do Deploy

No GitHub Actions, você verá:
- ✅ Build da imagem
- ✅ Push para GCR
- ✅ Deploy no Cloud Run
- ✅ Teste do deployment

## ⚠️ Troubleshooting

### Erro: "Permission denied"
- Verificar se a service account tem as permissões corretas
- Verificar se o secret `GCP_SA_KEY` está correto

### Erro: "DATABASE_URL not found"
- Verificar se o secret `DATABASE_URL` foi adicionado
- Verificar se a URL está correta

### Erro: "Connection name not found"
- Verificar se a instância do Cloud SQL existe
- Verificar se o nome da instância está correto (`hospicast-db`)

## 🔍 Comandos Úteis

```bash
# Ver service accounts
gcloud iam service-accounts list

# Ver permissões de uma service account
gcloud projects get-iam-policy hospicast-prod \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:github-actions@hospicast-prod.iam.gserviceaccount.com"

# Ver logs do Cloud Run
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

---

**Após configurar os secrets, faça um push no branch main para testar o deploy automático!**



