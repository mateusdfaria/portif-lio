# 🚀 Deploy no Netlify - HospiCast

## 📋 Pré-requisitos

1. Conta no Netlify (gratuita): https://www.netlify.com
2. Repositório no GitHub conectado

## 🔧 Configuração

### 1. Arquivo de Configuração

O arquivo `netlify.toml` já está configurado com:
- ✅ Comando de build: `cd frontend && npm install && npm run build`
- ✅ Diretório de publicação: `frontend/dist`
- ✅ Redirecionamentos para SPA
- ✅ Headers de segurança

### 2. Variáveis de Ambiente

**IMPORTANTE**: Configure no painel do Netlify:

1. Acesse: **Site settings** → **Environment variables**
2. Adicione:
   ```
   VITE_API_BASE_URL = https://sua-api-backend.com
   ```
   
   **Exemplos:**
   - Se o backend estiver no Heroku: `https://seu-app.herokuapp.com`
   - Se estiver no Railway: `https://seu-app.railway.app`
   - Se estiver local: `http://localhost:8000` (apenas para desenvolvimento)

### 3. Deploy Manual

#### Opção A: Via Netlify Dashboard

1. Acesse: https://app.netlify.com
2. Clique em **"Add new site"** → **"Import an existing project"**
3. Conecte seu repositório GitHub: `mateusdfaria/portif-lio`
4. Configure:
   - **Build command**: `cd frontend && npm install && npm run build`
   - **Publish directory**: `frontend/dist`
5. Adicione a variável de ambiente `VITE_API_BASE_URL`
6. Clique em **"Deploy site"**

#### Opção B: Via Netlify CLI

```bash
# Instalar Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

### 4. Deploy Automático (CI/CD)

O Netlify detecta automaticamente pushes na branch `main` e faz deploy.

**Para configurar:**
1. No Netlify Dashboard → **Site settings** → **Build & deploy**
2. Configure:
   - **Branch to deploy**: `main`
   - **Build command**: `cd frontend && npm install && npm run build`
   - **Publish directory**: `frontend/dist`

## 🐛 Problemas Comuns e Soluções

### ❌ Erro: "Build command failed" ou "Command failed with exit code 1"

**Possíveis causas e soluções:**

1. **Dependências não instaladas:**
   ```bash
   # Solução: Use npm ci em vez de npm install
   # O netlify.toml já está configurado com npm ci
   ```

2. **Erro de permissão ou caminho:**
   - Verifique se o comando está correto: `cd frontend && npm ci && npm run build`
   - Certifique-se de que o diretório `frontend` existe

3. **Erro de Node.js:**
   - Configure Node.js 20 no Netlify (já configurado no `netlify.toml`)
   - Ou configure manualmente: **Site settings** → **Build & deploy** → **Environment** → **Node version**: `20`

4. **Erro de memória:**
   - Adicione no `netlify.toml`:
   ```toml
   [build.environment]
     NODE_OPTIONS = "--max-old-space-size=4096"
   ```

### ❌ Erro: "Publish directory does not exist" ou "No such file or directory"

**Causa**: O diretório `frontend/dist` não foi gerado durante o build.

**Soluções:**

1. **Verifique o build localmente:**
   ```bash
   cd frontend
   npm ci
   npm run build
   # Verifique se a pasta dist/ foi criada
   ```

2. **Verifique o caminho no Netlify:**
   - **Publish directory** deve ser: `frontend/dist` (não apenas `dist`)
   - O `netlify.toml` já está configurado corretamente

3. **Se o build falhar antes de gerar dist/:**
   - Veja os logs completos no Netlify
   - Procure por erros de compilação do Vite
   - Verifique se há erros de sintaxe no código

### ❌ Erro: "API calls failing" ou "Failed to fetch"

**Causa**: Variável de ambiente `VITE_API_BASE_URL` não configurada ou incorreta.

**Soluções:**

1. **Configure a variável de ambiente:**
   - **Site settings** → **Environment variables**
   - Adicione: `VITE_API_BASE_URL` = `https://sua-api.com`
   - ⚠️ **IMPORTANTE**: Use `https://` para produção (não `http://`)

2. **Verifique se o backend está acessível:**
   ```bash
   curl https://sua-api.com/
   # Deve retornar status 200
   ```

3. **Rebuild após adicionar variável:**
   - Após adicionar a variável, faça um novo deploy
   - Ou clique em **Trigger deploy** → **Clear cache and deploy site**

### ❌ Erro: "404 on routes" ou "Page not found"

**Causa**: Redirecionamentos SPA não configurados.

**Solução**: 
- O arquivo `netlify.toml` já tem a configuração correta
- O arquivo `_redirects` também foi criado na raiz
- Se ainda não funcionar, verifique se os arquivos estão no repositório

### ❌ Erro: "CORS" ou "Access-Control-Allow-Origin"

**Causa**: Backend não permite requisições do domínio do Netlify.

**Solução**: Configure CORS no backend para aceitar o domínio do Netlify:

```python
# No backend/main.py (FastAPI)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seu-app.netlify.app",  # Substitua pelo seu domínio
        "https://*.netlify.app",  # Permite todos os subdomínios Netlify
        "http://localhost:3000",  # desenvolvimento
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Depois de configurar:**
- Faça deploy do backend atualizado
- Atualize a variável `VITE_API_BASE_URL` no Netlify
- Faça rebuild do frontend

### ❌ Erro: "Some specified paths were not resolved, unable to cache dependencies"

**Causa**: Problema com cache do npm no Netlify.

**Solução**: 
- Este erro geralmente não impede o deploy
- O `netlify.toml` já está configurado sem cache problemático
- Se persistir, desabilite o cache no Netlify: **Site settings** → **Build & deploy** → **Caching** → Desabilite

### ❌ Erro: "Module not found" ou "Cannot find module"

**Causa**: Dependências não instaladas ou versão incorreta do Node.

**Soluções:**
1. Verifique se `package-lock.json` está no repositório
2. Use `npm ci` em vez de `npm install` (já configurado)
3. Configure Node.js 20 no Netlify

### ❌ Erro: "Build timed out"

**Causa**: Build demorando mais de 15 minutos.

**Soluções:**
1. Otimize o build (já está otimizado com `npm ci`)
2. Verifique se há processos lentos no build
3. Considere usar Netlify Pro para builds mais longos

## ✅ Checklist de Deploy

- [ ] Repositório conectado ao Netlify
- [ ] Build command configurado: `cd frontend && npm ci && npm run build`
- [ ] Publish directory configurado: `frontend/dist`
- [ ] Node.js 20 configurado (ou via `netlify.toml`)
- [ ] Variável de ambiente `VITE_API_BASE_URL` configurada
- [ ] Backend acessível publicamente
- [ ] CORS configurado no backend
- [ ] Build local funcionando: `cd frontend && npm run build`
- [ ] Arquivo `netlify.toml` no repositório
- [ ] Arquivo `_redirects` no repositório (opcional, mas recomendado)

## 🔗 Links Úteis

- **Netlify Dashboard**: https://app.netlify.com
- **Documentação Netlify**: https://docs.netlify.com
- **Netlify CLI**: https://cli.netlify.com

## 📝 Notas

- O Netlify faz deploy apenas do **frontend**
- O **backend** precisa estar hospedado em outro serviço (Heroku, Railway, Render, etc.)
- Certifique-se de que o backend está acessível publicamente
- Use HTTPS para produção (Netlify fornece automaticamente)

---

*Última atualização: Janeiro 2025*

