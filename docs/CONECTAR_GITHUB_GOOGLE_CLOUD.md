# 🔗 Conectar GitHub ao Google Cloud

## 📋 Opções de Conexão

Existem duas formas principais:

1. **Cloud Shell**: Clonar repositório do GitHub
2. **Cloud Build**: Conectar repositório para deploy automático

## ✅ Opção 1: Clonar Repositório no Cloud Shell

### Passo 1: Clonar do GitHub

```bash
# No Cloud Shell
cd ~

# Clonar repositório
git clone https://github.com/mateusdfaria/portif-lio.git

# Ou se já existe, atualizar
cd ~/portif-lio
git pull origin main
```

### Passo 2: Verificar

```bash
# Verificar se está no diretório correto
cd ~/portif-lio
pwd
ls -la

# Verificar remote
git remote -v
```

## ✅ Opção 2: Conectar Cloud Build ao GitHub (Deploy Automático)

### Passo 1: Habilitar Cloud Build API

```bash
# Habilitar API
gcloud services enable cloudbuild.googleapis.com

# Verificar se está habilitado
gcloud services list --enabled | grep cloudbuild
```

### Passo 2: Conectar Repositório via Console

1. Ir para: https://console.cloud.google.com/cloud-build/triggers
2. Clicar em "Connect Repository"
3. Selecionar "GitHub (Cloud Build GitHub App)"
4. Autorizar acesso ao GitHub
5. Selecionar repositório: `mateusdfaria/portif-lio`
6. Clicar em "Connect"

### Passo 3: Criar Trigger (via Console)

1. Após conectar, clicar em "Create Trigger"
2. Configurar:
   - **Name**: `deploy-backend`
   - **Event**: Push to a branch
   - **Branch**: `^main$`
   - **Configuration**: Cloud Build configuration file
   - **Location**: `cloudbuild.yaml`
3. Clicar em "Create"

### Passo 4: Criar Trigger via CLI

```bash
# Criar trigger para backend
gcloud builds triggers create github \
    --repo-name=portif-lio \
    --repo-owner=mateusdfaria \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --name=deploy-backend \
    --description="Deploy backend on push to main"
```

## ✅ Opção 3: Usar Cloud Shell Editor (Upload)

### Passo 1: Abrir Editor no Cloud Shell

```bash
# No Cloud Shell, clicar no ícone de editor (lápis)
# Ou usar comando
cloudshell open-editor
```

### Passo 2: Upload de Arquivos

1. No editor, clicar com botão direito na pasta
2. Selecionar "Upload Files"
3. Selecionar arquivos do projeto local

## 📋 Comandos Completos - Clonar do GitHub

```bash
# === 1. NAVEGAR PARA HOME ===
cd ~

# === 2. CLONAR REPOSITÓRIO ===
git clone https://github.com/mateusdfaria/portif-lio.git

# === 3. ENTRAR NO DIRETÓRIO ===
cd portif-lio

# === 4. VERIFICAR ===
pwd
ls -la
git remote -v

# === 5. SE JÁ EXISTIR, ATUALIZAR ===
# cd ~/portif-lio
# git pull origin main
```

## 🔐 Autenticação GitHub (se necessário)

### Se pedir credenciais:

```bash
# Configurar usuário Git
git config --global user.name "mateusdfaria"
git config --global user.email "mateusfarias2308@gmail.com"

# Para HTTPS, usar Personal Access Token
# Criar token: https://github.com/settings/tokens
# Usar token como senha quando pedir
```

## 🔄 Atualizar Código do GitHub

```bash
# No Cloud Shell
cd ~/portif-lio

# Verificar status
git status

# Atualizar do GitHub
git pull origin main

# Se houver conflitos, resolver ou fazer reset
# git reset --hard origin/main
```

## 📦 Verificar Estrutura do Projeto

```bash
# Ver estrutura
cd ~/portif-lio
tree -L 2

# Ou
ls -la
ls -la backend/
ls -la frontend/
```

## 🎯 Configurar Cloud Build (Opcional)

### Criar `cloudbuild.yaml` na raiz (se ainda não tiver):

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/hospicast-backend:$SHORT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/hospicast-backend:latest'
      - './backend'
    id: 'build-backend'

  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/$PROJECT_ID/hospicast-backend:latest'
    id: 'push-backend'

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
      - '--allow-unauthenticated'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '2'
      - '--timeout'
      - '600'
      - '--max-instances'
      - '10'
      - '--port'
      - '8080'
      - '--set-env-vars'
      - 'API_ALLOWED_ORIGINS=*'
      - '--set-env-vars'
      - 'LOG_LEVEL=INFO'
      - '--set-env-vars'
      - 'PROMETHEUS_ENABLED=true'
      - '--set-env-vars'
      - 'ENVIRONMENT=production'
    id: 'deploy-backend'

images:
  - 'gcr.io/$PROJECT_ID/hospicast-backend:$SHORT_SHA'
  - 'gcr.io/$PROJECT_ID/hospicast-backend:latest'

options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY

timeout: '1200s'
```

## 🔍 Verificar Conexão

### Ver triggers do Cloud Build:

```bash
# Listar triggers
gcloud builds triggers list

# Ver detalhes de um trigger
gcloud builds triggers describe TRIGGER_NAME
```

### Ver histórico de builds:

```bash
# Listar builds
gcloud builds list

# Ver detalhes de um build
gcloud builds describe BUILD_ID
```

## ⚠️ Troubleshooting

### Erro: "Repository not found"
- Verificar se o repositório é público ou se você tem acesso
- Verificar se o nome está correto: `mateusdfaria/portif-lio`

### Erro: "Permission denied"
- Verificar se está autenticado no GitHub
- Usar Personal Access Token se necessário

### Erro: "Cloud Build API not enabled"
```bash
gcloud services enable cloudbuild.googleapis.com
```

---

**Execute os comandos acima para conectar o GitHub ao Google Cloud!**



