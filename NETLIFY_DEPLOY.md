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

## 🐛 Problemas Comuns

### Erro: "Build command failed"

**Causa**: Comando de build incorreto ou dependências não instaladas.

**Solução**: 
- Verifique se o comando está correto: `cd frontend && npm install && npm run build`
- Verifique se há erros no `package.json`

### Erro: "Publish directory does not exist"

**Causa**: O diretório `frontend/dist` não foi gerado.

**Solução**:
- Verifique se o build está gerando arquivos em `frontend/dist`
- Execute localmente: `cd frontend && npm run build`
- Verifique se há erros no build

### Erro: "API calls failing"

**Causa**: Variável de ambiente `VITE_API_BASE_URL` não configurada ou incorreta.

**Solução**:
- Configure `VITE_API_BASE_URL` no Netlify Dashboard
- Verifique se a URL está correta (com `https://` ou `http://`)
- Verifique se o backend está acessível publicamente

### Erro: "404 on routes"

**Causa**: Redirecionamentos SPA não configurados.

**Solução**: O arquivo `netlify.toml` já tem a configuração correta:
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Erro: "CORS"

**Causa**: Backend não permite requisições do domínio do Netlify.

**Solução**: Configure CORS no backend para aceitar o domínio do Netlify:
```python
# No backend (FastAPI)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seu-app.netlify.app",
        "http://localhost:3000",  # desenvolvimento
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## ✅ Checklist de Deploy

- [ ] Repositório conectado ao Netlify
- [ ] Build command configurado: `cd frontend && npm install && npm run build`
- [ ] Publish directory configurado: `frontend/dist`
- [ ] Variável de ambiente `VITE_API_BASE_URL` configurada
- [ ] Backend acessível publicamente
- [ ] CORS configurado no backend
- [ ] Build local funcionando: `cd frontend && npm run build`
- [ ] Arquivo `netlify.toml` no repositório

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

