# 🚀 Usar Deploy Completo - Backend + Frontend

## 📋 Arquivo Criado

`.github/workflows/deploy-completo.yml` - Workflow único que faz deploy de ambos

## ✅ O Que Este Workflow Faz

1. **Deploy do Backend**:
   - Build da imagem Docker
   - Push para Google Container Registry
   - Deploy no Cloud Run
   - Testa se o backend está funcionando

2. **Deploy do Frontend** (após backend):
   - Obtém a URL do backend recém-deployado
   - Configura `.env.production` com a URL do backend
   - Build do frontend
   - Upload para Cloud Storage

## 🔧 Configuração Necessária

### Secrets do GitHub

Configure estes secrets no GitHub:
- `GCP_SA_KEY`: Chave JSON da Service Account do Google Cloud
- `DATABASE_URL`: URL de conexão com o PostgreSQL

### Como Configurar Secrets

1. Acesse: https://github.com/mateusdfaria/portif-lio/settings/secrets/actions
2. Clique em "New repository secret"
3. Adicione:
   - **Nome**: `GCP_SA_KEY`
   - **Valor**: Todo o conteúdo do arquivo JSON da service account
4. Adicione:
   - **Nome**: `DATABASE_URL`
   - **Valor**: `postgresql://hospicast_user:SENHA@localhost/hospicast?host=/cloudsql/CONNECTION_NAME`

## 🚀 Como Usar

### Deploy Automático

O workflow executa automaticamente quando:
- Você faz push para a branch `main`
- Altera arquivos em `backend/**` ou `frontend/**`
- Altera o próprio workflow

### Deploy Manual

1. Acesse: https://github.com/mateusdfaria/portif-lio/actions
2. Clique em "Deploy Completo - Backend + Frontend"
3. Clique em "Run workflow"
4. Selecione a branch `main`
5. Clique em "Run workflow"

## 📋 Ordem de Execução

1. **Job 1: deploy-backend**
   - Build e deploy do backend
   - Obtém URL do backend

2. **Job 2: deploy-frontend** (depende do job 1)
   - Usa a URL do backend do job anterior
   - Build e deploy do frontend

## 🔍 Verificar Deploy

### No GitHub Actions

1. Acesse: https://github.com/mateusdfaria/portif-lio/actions
2. Clique no workflow mais recente
3. Veja os logs de cada job
4. Verifique se ambos os jobs foram bem-sucedidos

### URLs Finais

Após o deploy, você verá no summary:
- **Backend**: https://hospicast-backend-...a.run.app
- **Frontend**: https://storage.googleapis.com/hospicast-frontend/index.html

## ⚙️ Desabilitar Workflows Antigos (Opcional)

Para evitar conflitos, você pode desabilitar os workflows antigos:

```bash
# Renomear workflows antigos (eles não serão executados)
cd ~/portif-lio
git mv .github/workflows/deploy-cloud-run.yml .github/workflows/deploy-cloud-run.yml.disabled
git mv .github/workflows/deploy-frontend-gcs.yml .github/workflows/deploy-frontend-gcs.yml.disabled

# Commit
git add .github/workflows/
git commit -m "chore: desabilitar workflows antigos, usar deploy-completo.yml"
git push origin main
```

Ou simplesmente delete os arquivos antigos se não precisar mais deles.

## 🔧 Personalizar

### Alterar Memória/CPU do Backend

Edite `.github/workflows/deploy-completo.yml`:

```yaml
--memory 4Gi \      # Altere aqui
--cpu 2 \           # Altere aqui
```

### Alterar Nome do Bucket

Edite a variável `BUCKET_NAME`:

```yaml
env:
  BUCKET_NAME: hospicast-frontend  # Altere aqui
```

### Alterar Região

Edite a variável `REGION`:

```yaml
env:
  REGION: southamerica-east1  # Altere aqui
```

## ✅ Vantagens

- ✅ **Um único arquivo** para gerenciar
- ✅ **Deploy sequencial** - frontend sempre usa a URL correta do backend
- ✅ **Automático** - executa ao fazer push
- ✅ **Manual** - pode executar quando quiser
- ✅ **Testes** - testa o backend após deploy

---

**Agora você tem um único workflow que faz deploy de tudo!** 🎯

