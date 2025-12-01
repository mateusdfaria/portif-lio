# 🔧 Solução: ERR_CONNECTION_REFUSED no Netlify

## ❌ Problema

O erro `ERR_CONNECTION_REFUSED` ocorre porque:

1. **Frontend no Netlify** está tentando acessar `localhost:8000`
2. **Backend não está rodando** ou não está acessível publicamente
3. **Variável de ambiente não configurada** no Netlify

## ✅ Solução Rápida

### Passo 1: Hospedar o Backend

O backend precisa estar em um serviço de hospedagem. **Recomendado: Railway (grátis)**

#### Opção A: Railway (Mais Fácil - Grátis)

1. **Acesse**: https://railway.app
2. **Login** com GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Selecione**: `mateusdfaria/portif-lio`
5. **Configure**:
   - **Root Directory**: `/backend`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. **Aguarde deploy** → Railway fornecerá URL: `https://seu-app.railway.app`

#### Opção B: Render (Grátis)

1. **Acesse**: https://render.com
2. **New** → **Web Service**
3. **Conecte repositório** GitHub
4. **Configure**:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Deploy** → URL: `https://seu-app.onrender.com`

### Passo 2: Configurar CORS no Backend

O backend já tem CORS configurado, mas precisa aceitar o domínio do Netlify.

**Edite `backend/main.py`** e adicione o domínio do Netlify:

```python
# No arquivo backend/main.py, linha ~71
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seu-app.netlify.app",  # ← ADICIONE AQUI A URL DO NETLIFY
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "*"  # Temporário para testes
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**OU** configure via variável de ambiente (melhor):

No Railway/Render, adicione variável:
```
API_ALLOWED_ORIGINS=https://seu-app.netlify.app,http://localhost:3000
```

### Passo 3: Configurar Variável no Netlify

1. **Acesse**: https://app.netlify.com
2. **Seu site** → **Site settings** → **Environment variables**
3. **Adicione**:
   ```
   Key: VITE_API_BASE_URL
   Value: https://seu-app.railway.app
   ```
   (Substitua pela URL real do seu backend)

4. **IMPORTANTE**: Após adicionar, faça novo deploy:
   - **Deploys** → **Trigger deploy** → **Clear cache and deploy site**

### Passo 4: Verificar

1. **Teste o backend**:
   ```bash
   curl https://seu-app.railway.app/
   ```
   Deve retornar: `{"status": "ok", ...}`

2. **Teste no Netlify**:
   - Acesse seu site no Netlify
   - Abra console (F12)
   - Tente cadastrar um hospital
   - Deve funcionar!

## 🚀 Deploy Rápido no Railway (Passo a Passo)

### 1. Criar Conta
- Acesse: https://railway.app
- Clique em "Login with GitHub"
- Autorize o Railway

### 2. Criar Projeto
- Clique em "New Project"
- Selecione "Deploy from GitHub repo"
- Escolha: `mateusdfaria/portif-lio`

### 3. Configurar Serviço
Railway detecta automaticamente, mas se não detectar:

- **Settings** → **Root Directory**: `/backend`
- **Settings** → **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 4. Aguardar Deploy
- Railway faz build automaticamente
- Aguarde ~2-3 minutos
- URL será: `https://seu-app.railway.app`

### 5. Configurar Variáveis (Opcional)
- **Variables** → Adicione:
  - `API_ALLOWED_ORIGINS`: `https://seu-app.netlify.app,http://localhost:3000`

### 6. Configurar no Netlify
- Adicione `VITE_API_BASE_URL` = URL do Railway
- Faça novo deploy

## 📝 Checklist

- [ ] Backend hospedado (Railway/Render)
- [ ] Backend acessível (teste com curl)
- [ ] CORS configurado (aceita domínio Netlify)
- [ ] Variável `VITE_API_BASE_URL` no Netlify
- [ ] Novo deploy no Netlify após configurar variável
- [ ] Teste de cadastro funcionando

## 🐛 Troubleshooting

### Backend não responde
- Verifique logs no Railway: **View Logs**
- Verifique se o comando de start está correto
- Verifique se a porta está correta (`$PORT`)

### CORS Error
- Adicione domínio do Netlify em `allow_origins`
- Ou configure `API_ALLOWED_ORIGINS` no Railway

### Variável não funciona
- **SEMPRE** faça novo deploy após adicionar variável
- Variáveis são injetadas no **build**, não em runtime
- Limpe cache: **Clear cache and deploy site**

### Erro 404
- Verifique se as rotas estão corretas
- Teste: `https://seu-backend.railway.app/docs` (Swagger)

### Banco de dados não funciona
- SQLite funciona no Railway
- Verifique permissões do diretório `data/`
- Railway mantém arquivos entre reinicializações

## 💡 Dica Importante

**Variáveis de ambiente no Netlify:**
- São injetadas durante o **build**
- Após adicionar, **sempre** faça novo deploy
- Use **Clear cache and deploy site** para garantir

---

*Última atualização: Janeiro 2025*

