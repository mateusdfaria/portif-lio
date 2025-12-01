# 🚀 Deploy do Frontend no Firebase Hosting

## 📋 Pré-requisitos

1. ✅ Conta no Google (mesma do Google Cloud)
2. ✅ Projeto Firebase criado
3. ✅ Firebase CLI instalado

## 🔧 Passo 1: Instalar Firebase CLI

### No Windows (PowerShell):

```powershell
# Instalar via npm (se tiver Node.js)
npm install -g firebase-tools

# Ou via Chocolatey
choco install firebase-tools
```

### No Cloud Shell:

```bash
npm install -g firebase-tools
```

### Verificar instalação:

```bash
firebase --version
```

## 🔐 Passo 2: Login no Firebase

```bash
firebase login
```

Isso abrirá o navegador para autenticar. Use a mesma conta do Google Cloud.

## 📦 Passo 3: Criar Projeto Firebase (se ainda não tiver)

1. Ir para: https://console.firebase.google.com
2. Clicar em "Adicionar projeto"
3. Nome: `hospicast-prod` (ou outro nome)
4. Aceitar termos e criar projeto
5. **Não** adicionar Google Analytics (ou adicionar se quiser)

## 🔗 Passo 4: Inicializar Firebase no Projeto

```bash
# No diretório raiz do projeto
cd /home/mateusfarias2308/portif-lio  # ou caminho do seu projeto

# Inicializar Firebase
firebase init hosting
```

**Durante a inicialização, escolher:**
- ✅ Use an existing project → Selecionar `hospicast-prod`
- ✅ What do you want to use as your public directory? → `frontend/dist`
- ✅ Configure as a single-page app? → `Yes`
- ✅ Set up automatic builds and deploys with GitHub? → `No` (por enquanto)
- ✅ File frontend/dist/index.html already exists. Overwrite? → `No`

## 🔧 Passo 5: Configurar Variável de Ambiente do Backend

O frontend precisa saber a URL do backend no Cloud Run.

### Obter URL do Backend:

```bash
# No Cloud Shell
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "Backend URL: $BACKEND_URL"
```

### Criar arquivo `.env.production` no frontend:

```bash
# Criar arquivo .env.production
cd frontend
echo "VITE_API_BASE_URL=$BACKEND_URL" > .env.production
cd ..
```

**Ou criar manualmente** `frontend/.env.production`:
```
VITE_API_BASE_URL=https://hospicast-backend-xxxxx-xx.a.run.app
```

## 🏗️ Passo 6: Build do Frontend

```bash
# No diretório raiz
cd frontend
npm install
npm run build
cd ..
```

Isso criará a pasta `frontend/dist` com os arquivos prontos para deploy.

## 🚀 Passo 7: Deploy no Firebase Hosting

```bash
# No diretório raiz
firebase deploy --only hosting
```

**Primeira vez pode pedir para:**
- Selecionar projeto Firebase
- Confirmar deploy

## ✅ Passo 8: Verificar Deploy

Após o deploy, você verá uma URL como:
```
✔  Deploy complete!

Hosting URL: https://hospicast-prod.web.app
```

**Abrir no navegador** e testar!

## 🔄 Deploy Automático via GitHub Actions

Criar workflow para deploy automático:

### Criar `.github/workflows/deploy-frontend-firebase.yml`:

```yaml
name: Deploy Frontend to Firebase

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend-firebase.yml'
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        working-directory: frontend
        run: npm ci

      - name: Build frontend
        working-directory: frontend
        env:
          VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}
        run: npm run build

      - name: Setup Firebase CLI
        run: npm install -g firebase-tools

      - name: Deploy to Firebase
        env:
          FIREBASE_TOKEN: ${{ secrets.FIREBASE_TOKEN }}
        run: firebase deploy --only hosting --token $FIREBASE_TOKEN
```

### Obter Token do Firebase:

```bash
firebase login:ci
```

Copiar o token e adicionar como secret no GitHub:
- Nome: `FIREBASE_TOKEN`
- Valor: O token obtido

### Adicionar Secret da URL do Backend:

No GitHub, adicionar secret:
- Nome: `VITE_API_BASE_URL`
- Valor: URL do backend no Cloud Run

## 📋 Comandos Completos (Resumo)

```bash
# === 1. INSTALAR FIREBASE CLI ===
npm install -g firebase-tools

# === 2. LOGIN ===
firebase login

# === 3. INICIALIZAR (se ainda não fez) ===
firebase init hosting

# === 4. OBTER URL DO BACKEND ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# === 5. CRIAR .env.production ===
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

# === 6. BUILD ===
cd frontend
npm install
npm run build
cd ..

# === 7. DEPLOY ===
firebase deploy --only hosting
```

## 🔍 Verificar Configuração

### Ver arquivo `firebase.json`:

```json
{
  "hosting": {
    "public": "frontend/dist",
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

### Ver arquivo `.firebaserc`:

```json
{
  "projects": {
    "default": "hospicast-prod"
  }
}
```

## ⚠️ Troubleshooting

### Erro: "Firebase project not found"
- Verificar se o projeto existe no console Firebase
- Verificar se está logado: `firebase login`
- Verificar `.firebaserc` tem o projeto correto

### Erro: "Directory frontend/dist not found"
- Fazer build primeiro: `cd frontend && npm run build`

### Erro: "CORS" no navegador
- Verificar se `API_ALLOWED_ORIGINS` no backend inclui a URL do Firebase
- Adicionar URL do Firebase no backend: `API_ALLOWED_ORIGINS=https://hospicast-prod.web.app,https://hospicast-prod.firebaseapp.com`

### Frontend não conecta com backend
- Verificar se `.env.production` tem a URL correta
- Verificar se a URL do backend está acessível
- Verificar CORS no backend

## 🎯 Próximos Passos

Após o deploy:
1. ✅ Testar frontend no navegador
2. ✅ Verificar se conecta com backend
3. ✅ Configurar domínio customizado (opcional)
4. ✅ Configurar deploy automático via GitHub Actions

---

**Execute os passos acima e me avise se funcionou!**



