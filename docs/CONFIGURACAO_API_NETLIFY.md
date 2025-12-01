# 🔧 Configuração da API no Netlify

## ❌ Erro: `ERR_CONNECTION_REFUSED`

O erro ocorre porque o frontend está tentando acessar `localhost:8000`, mas:

1. **No Netlify**: `localhost` não existe (é o servidor local)
2. **Backend não está rodando**: O backend precisa estar hospedado separadamente

## ✅ Solução

### 1. Hospedar o Backend

O backend precisa estar em um serviço de hospedagem:

#### Opção A: Railway (Recomendado - Grátis)
1. Acesse: https://railway.app
2. Conecte seu repositório GitHub
3. Configure:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Adicione se necessário
4. Railway fornecerá uma URL: `https://seu-app.railway.app`

#### Opção B: Render (Grátis)
1. Acesse: https://render.com
2. New → Web Service
3. Conecte repositório
4. Configure:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Render fornecerá: `https://seu-app.onrender.com`

#### Opção C: Heroku (Pago)
1. Acesse: https://heroku.com
2. Crie um novo app
3. Configure buildpacks e variáveis
4. Deploy via Git

### 2. Configurar Variável de Ambiente no Netlify

Após hospedar o backend, configure no Netlify:

1. Acesse: https://app.netlify.com
2. Seu site → **Site settings** → **Environment variables**
3. Adicione:
   ```
   Key: VITE_API_BASE_URL
   Value: https://seu-backend.railway.app
   ```
   (Substitua pela URL real do seu backend)

4. **IMPORTANTE**: Após adicionar, faça um novo deploy:
   - **Deploys** → **Trigger deploy** → **Clear cache and deploy site**

### 3. Verificar Configuração no Código

O frontend já está configurado para usar a variável de ambiente:

```javascript
const defaultApiBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001';
```

Isso significa:
- **Em produção (Netlify)**: Usa `VITE_API_BASE_URL` (configurada no Netlify)
- **Em desenvolvimento local**: Usa `http://127.0.0.1:8001` (fallback)

## 🔍 Verificação

### 1. Verificar se Backend está Rodando

Teste a URL do backend diretamente:
```bash
curl https://seu-backend.railway.app/
```

Deve retornar:
```json
{"status": "ok", "message": "HospiCast API"}
```

### 2. Verificar Variável no Netlify

1. No Netlify Dashboard → **Site settings** → **Environment variables**
2. Verifique se `VITE_API_BASE_URL` está configurada
3. Verifique se o valor está correto (com `https://`)

### 3. Verificar no Console do Navegador

No Netlify, abra o console do navegador (F12) e verifique:
```javascript
console.log(import.meta.env.VITE_API_BASE_URL)
```

Deve mostrar a URL do backend em produção.

## 🚀 Deploy Rápido do Backend (Railway)

### Passo a Passo

1. **Criar conta no Railway**
   - https://railway.app
   - Login com GitHub

2. **Criar novo projeto**
   - New Project → Deploy from GitHub repo
   - Selecione: `mateusdfaria/portif-lio`

3. **Configurar serviço**
   - Railway detecta automaticamente
   - Se não detectar, configure:
     - **Root Directory**: `/backend`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Aguardar deploy**
   - Railway faz build e deploy automaticamente
   - URL será: `https://seu-app.railway.app`

5. **Configurar CORS no Backend**

   Adicione no `backend/main.py`:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://seu-app.netlify.app",  # URL do Netlify
           "http://localhost:3000",  # Desenvolvimento local
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

6. **Configurar no Netlify**
   - Adicione `VITE_API_BASE_URL` = `https://seu-app.railway.app`
   - Faça novo deploy

## 📝 Checklist

- [ ] Backend hospedado (Railway/Render/Heroku)
- [ ] Backend acessível publicamente (teste com curl)
- [ ] CORS configurado no backend
- [ ] Variável `VITE_API_BASE_URL` configurada no Netlify
- [ ] Novo deploy feito no Netlify após configurar variável
- [ ] Teste de cadastro funcionando

## 🐛 Troubleshooting

### Backend não responde
- Verifique se o backend está rodando
- Verifique logs no Railway/Render
- Teste a URL diretamente no navegador

### CORS Error
- Configure CORS no backend para aceitar o domínio do Netlify
- Verifique se `allow_origins` inclui a URL do Netlify

### Variável não funciona
- Após adicionar variável, **sempre** faça novo deploy
- Variáveis são injetadas no build, não em runtime
- Limpe cache: **Clear cache and deploy site**

### Erro 404 no backend
- Verifique se as rotas estão corretas
- Teste: `https://seu-backend.railway.app/docs` (deve mostrar Swagger)

---

*Última atualização: Janeiro 2025*

