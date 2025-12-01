# 🔧 Configurar Frontend no Firebase - Passo a Passo

## 📋 Passo 1: Instalar Firebase CLI

### No Windows (PowerShell):

```powershell
# Se tiver Node.js instalado
npm install -g firebase-tools

# Verificar se instalou
firebase --version
```

### No Cloud Shell:

```bash
npm install -g firebase-tools
firebase --version
```

## 🔐 Passo 2: Login no Firebase

```bash
firebase login
```

Isso abrirá o navegador. Faça login com a mesma conta do Google Cloud.

**Verificar se está logado:**
```bash
firebase projects:list
```

## 📦 Passo 3: Criar Projeto Firebase (se ainda não tiver)

### Opção A: Via Console Web

1. Ir para: https://console.firebase.google.com
2. Clicar em "Adicionar projeto" ou "Create a project"
3. Nome do projeto: `hospicast-prod` (ou outro nome)
4. Aceitar termos e clicar em "Continuar"
5. **Desabilitar** Google Analytics (ou habilitar se quiser)
6. Clicar em "Criar projeto"

### Opção B: Via CLI

```bash
firebase projects:create hospicast-prod
```

## 🔗 Passo 4: Vincular Projeto ao Diretório Local

```bash
# No diretório raiz do projeto
cd /home/mateusfarias2308/portif-lio  # ou seu caminho

# Inicializar Firebase Hosting
firebase init hosting
```

### Durante a inicialização, escolher:

1. **"Use an existing project"** → Selecionar `hospicast-prod`
2. **"What do you want to use as your public directory?"** → Digitar: `frontend/dist`
3. **"Configure as a single-page app (rewrite all urls to /index.html)?"** → Digitar: `Yes`
4. **"Set up automatic builds and deploys with GitHub?"** → Digitar: `No` (vamos fazer depois)
5. **"File frontend/dist/index.html already exists. Overwrite?"** → Digitar: `No`

## ✅ Passo 5: Verificar Arquivos Criados

Após a inicialização, você deve ter:

- ✅ `firebase.json` (já criado)
- ✅ `.firebaserc` (já criado)

**Verificar conteúdo:**

```bash
# Ver firebase.json
cat firebase.json

# Ver .firebaserc
cat .firebaserc
```

## 🔧 Passo 6: Configurar URL do Backend

### Obter URL do Backend no Cloud Run:

```bash
# No Cloud Shell
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "Backend URL: $BACKEND_URL"
```

### Criar arquivo `.env.production`:

```bash
# Criar arquivo com a URL do backend
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

# Verificar se foi criado
cat frontend/.env.production
```

**Ou criar manualmente** `frontend/.env.production`:
```
VITE_API_BASE_URL=https://hospicast-backend-xxxxx-xx.a.run.app
```

## 🏗️ Passo 7: Build do Frontend

```bash
# Instalar dependências (se ainda não fez)
cd frontend
npm install

# Fazer build
npm run build

# Verificar se a pasta dist foi criada
ls -la dist/

cd ..
```

A pasta `frontend/dist` deve conter os arquivos prontos para deploy.

## 🚀 Passo 8: Deploy no Firebase

```bash
# No diretório raiz
firebase deploy --only hosting
```

**Primeira vez pode pedir:**
- Selecionar projeto: Escolher `hospicast-prod`
- Confirmar deploy: Digitar `Y`

## ✅ Passo 9: Verificar Deploy

Após o deploy, você verá:

```
✔  Deploy complete!

Hosting URL: https://hospicast-prod.web.app
```

**Abrir no navegador** e testar!

## 🔄 Passo 10: Configurar Deploy Automático (Opcional)

### Obter Token do Firebase:

```bash
firebase login:ci
```

Isso gerará um token. **Copie o token!**

### Adicionar Secrets no GitHub:

1. Ir para: https://github.com/mateusdfaria/portif-lio/settings/secrets/actions
2. Clicar em "New repository secret"
3. Adicionar:

**Secret 1:**
- Nome: `FIREBASE_TOKEN`
- Valor: Token obtido acima

**Secret 2:**
- Nome: `VITE_API_BASE_URL`
- Valor: URL do backend (ex: `https://hospicast-backend-xxxxx-xx.a.run.app`)

### Testar Deploy Automático:

```bash
# Fazer uma mudança pequena
echo "<!-- Test -->" >> frontend/index.html

# Commit e push
git add .
git commit -m "test: testar deploy automático"
git push origin main
```

O workflow `.github/workflows/deploy-frontend-firebase.yml` será executado automaticamente!

## 📋 Comandos Completos (Copiar e Colar)

```bash
# === 1. INSTALAR FIREBASE CLI ===
npm install -g firebase-tools

# === 2. LOGIN ===
firebase login

# === 3. VERIFICAR PROJETOS ===
firebase projects:list

# === 4. INICIALIZAR (se ainda não fez) ===
firebase init hosting
# Escolher: hospicast-prod, frontend/dist, Yes, No, No

# === 5. OBTER URL DO BACKEND ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# === 6. CRIAR .env.production ===
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

# === 7. BUILD ===
cd frontend
npm install
npm run build
cd ..

# === 8. DEPLOY ===
firebase deploy --only hosting
```

## 🔍 Verificar Configuração

### Ver `firebase.json`:

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

### Ver `.firebaserc`:

```json
{
  "projects": {
    "default": "hospicast-prod"
  }
}
```

## ⚠️ Problemas Comuns

### Erro: "Firebase project not found"
```bash
# Verificar projetos disponíveis
firebase projects:list

# Se não aparecer, criar projeto
firebase projects:create hospicast-prod
```

### Erro: "Directory frontend/dist not found"
```bash
# Fazer build primeiro
cd frontend
npm run build
cd ..
```

### Erro: "Not logged in"
```bash
# Fazer login novamente
firebase login
```

### Frontend não conecta com backend
- Verificar se `.env.production` tem a URL correta
- Verificar se o backend está acessível
- Verificar CORS no backend (deve incluir URL do Firebase)

## 🎯 Próximos Passos

Após configurar:
1. ✅ Testar frontend no navegador
2. ✅ Verificar se conecta com backend
3. ✅ Configurar domínio customizado (opcional)
4. ✅ Configurar deploy automático

---

**Execute os passos acima e me avise se funcionou!**



