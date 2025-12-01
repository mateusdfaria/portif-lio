# 🚀 Deploy Automático - Alternativas ao Google Cloud

## 📋 Opções de Plataformas

Criei workflows do GitHub Actions para várias plataformas populares:

1. **Railway** - Fácil de usar, suporta PostgreSQL
2. **Render** - Gratuito para começar, fácil configuração
3. **Fly.io** - Boa performance, global edge network

## 🚂 Railway

### Vantagens:
- ✅ Setup muito simples
- ✅ PostgreSQL incluído
- ✅ Deploy automático via Git
- ✅ Plano gratuito disponível

### Configuração:

1. **Criar conta**: https://railway.app
2. **Criar projeto** e adicionar serviço
3. **Conectar GitHub** ao projeto
4. **Obter token**:
   - Ir em: Account Settings → Tokens
   - Criar novo token
5. **Adicionar secret no GitHub**:
   - Nome: `RAILWAY_TOKEN`
   - Valor: O token criado

### Workflow criado:
`.github/workflows/deploy-railway.yml`

## 🎨 Render

### Vantagens:
- ✅ Plano gratuito generoso
- ✅ PostgreSQL gratuito
- ✅ Deploy automático
- ✅ SSL automático

### Configuração:

1. **Criar conta**: https://render.com
2. **Criar Web Service**:
   - Conectar repositório GitHub
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Obter API Key**:
   - Ir em: Account Settings → API Keys
   - Criar nova chave
4. **Obter Service ID**:
   - No dashboard do serviço, URL contém o ID
5. **Adicionar secrets no GitHub**:
   - `RENDER_API_KEY`: A chave API
   - `RENDER_SERVICE_ID`: O ID do serviço

### Workflow criado:
`.github/workflows/deploy-render.yml`

## 🪂 Fly.io

### Vantagens:
- ✅ Performance excelente
- ✅ Edge network global
- ✅ PostgreSQL disponível
- ✅ Plano gratuito

### Configuração:

1. **Criar conta**: https://fly.io
2. **Instalar Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```
3. **Login e criar app**:
   ```bash
   fly auth login
   fly launch
   ```
4. **Obter token**:
   ```bash
   fly auth token
   ```
5. **Adicionar secret no GitHub**:
   - Nome: `FLY_API_TOKEN`
   - Valor: O token obtido

### Workflow criado:
`.github/workflows/deploy-flyio.yml`

## 📋 Comparação Rápida

| Plataforma | Grátis | PostgreSQL | Facilidade | Performance |
|------------|--------|------------|------------|-------------|
| Railway    | ✅ Sim | ✅ Sim     | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Render     | ✅ Sim | ✅ Sim     | ⭐⭐⭐⭐   | ⭐⭐⭐ |
| Fly.io     | ✅ Sim | ✅ Sim     | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ |

## 🔧 Configurar Deploy Automático

### 1. Escolher uma plataforma

Recomendo **Railway** para começar (mais fácil).

### 2. Configurar a plataforma

Seguir os passos acima para a plataforma escolhida.

### 3. Adicionar secrets no GitHub

1. Ir para: https://github.com/mateusdfaria/portif-lio/settings/secrets/actions
2. Adicionar os secrets necessários (veja acima)

### 4. Fazer push

```bash
git add .
git commit -m "Configurar deploy automático"
git push origin main
```

O deploy será acionado automaticamente!

## 📝 Arquivos de Configuração Necessários

### Railway

Criar `railway.json` na raiz:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Render

Criar `render.yaml` na raiz:

```yaml
services:
  - type: web
    name: hospicast-backend
    env: docker
    dockerfilePath: ./backend/Dockerfile
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: API_ALLOWED_ORIGINS
        value: "*"
      - key: LOG_LEVEL
        value: "INFO"
```

### Fly.io

Criar `fly.toml` na raiz:

```toml
app = "hospicast-backend"
primary_region = "gru"

[build]
  dockerfile = "backend/Dockerfile"

[env]
  PORT = "8080"
  API_ALLOWED_ORIGINS = "*"
  LOG_LEVEL = "INFO"

[[services]]
  internal_port = 8080
  protocol = "tcp"
```

## 🎯 Recomendação

Para começar rapidamente, recomendo **Railway**:
- ✅ Setup mais simples
- ✅ Interface muito intuitiva
- ✅ PostgreSQL incluído
- ✅ Deploy automático via Git

---

**Escolha uma plataforma e me avise qual você prefere configurar!**



