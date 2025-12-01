# 🚂 Guia Completo: Deploy do Backend no Railway

## 📋 Pré-requisitos

- Conta no GitHub (já tem: `mateusdfaria/portif-lio`)
- Conta no Railway (vamos criar agora)

## 🚀 Passo a Passo Completo

### Passo 1: Criar Conta no Railway

1. **Acesse**: https://railway.app
2. Clique em **"Start a New Project"** ou **"Login"**
3. Escolha **"Login with GitHub"**
4. Autorize o Railway a acessar seus repositórios
5. ✅ Conta criada!

### Passo 2: Criar Novo Projeto

1. No dashboard do Railway, clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Se não aparecer seus repositórios, clique em **"Configure GitHub App"** e autorize
4. **Procure e selecione**: `mateusdfaria/portif-lio`
5. Clique em **"Deploy Now"**

### Passo 3: Configurar o Serviço

O Railway vai detectar automaticamente, mas vamos garantir que está correto:

1. **Clique no serviço** que foi criado
2. Vá em **Settings** (ícone de engrenagem)
3. Configure:

   **Root Directory:**
   ```
   backend
   ```

   **Start Command:**
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

   **Build Command (opcional, mas recomendado):**
   ```
   pip install -r requirements.txt
   ```

4. **Salve** as configurações

### Passo 4: Configurar Variáveis de Ambiente

1. No mesmo serviço, vá em **Variables**
2. Adicione as seguintes variáveis:

   ```
   API_ALLOWED_ORIGINS=https://seu-app.netlify.app,http://localhost:3000,http://localhost:5173
   ```

   (Substitua `seu-app.netlify.app` pela URL real do seu Netlify)

   **Outras variáveis opcionais:**
   ```
   LOG_LEVEL=INFO
   PROMETHEUS_ENABLED=true
   ```

3. **Salve** as variáveis

### Passo 5: Aguardar Deploy

1. O Railway vai fazer o build automaticamente
2. Aguarde ~2-5 minutos
3. Você verá os logs em tempo real
4. Quando terminar, verá: **"Deployment successful"**

### Passo 6: Obter URL do Backend

1. No serviço, vá em **Settings**
2. Role até **"Networking"**
3. Clique em **"Generate Domain"** (se não tiver)
4. Copie a URL: `https://seu-app.railway.app`
5. ✅ Esta é a URL do seu backend!

### Passo 7: Testar o Backend

Abra no navegador ou use curl:

```
https://seu-app.railway.app/
```

Deve retornar:
```json
{"status": "ok", "message": "HospiCast API", ...}
```

Teste também a documentação:
```
https://seu-app.railway.app/docs
```

Deve abrir o Swagger UI.

### Passo 8: Configurar no Netlify

1. **Acesse**: https://app.netlify.com
2. **Seu site** → **Site settings** → **Environment variables**
3. **Adicione**:
   ```
   Key: VITE_API_BASE_URL
   Value: https://seu-app.railway.app
   ```
   (Substitua pela URL do Railway que você copiou)

4. **IMPORTANTE**: Após adicionar, faça novo deploy:
   - Vá em **Deploys**
   - Clique em **"Trigger deploy"**
   - Selecione **"Clear cache and deploy site"**
   - Aguarde o deploy terminar

### Passo 9: Verificar Funcionamento

1. Acesse seu site no Netlify
2. Abra o console do navegador (F12)
3. Tente cadastrar um hospital
4. ✅ Deve funcionar!

## 🔍 Verificação de Logs

### Ver Logs no Railway

1. No serviço, clique em **"View Logs"**
2. Você verá logs em tempo real
3. Se houver erros, aparecerão aqui

### Erros Comuns

**Erro: "Module not found"**
- Verifique se `requirements.txt` está correto
- Verifique se o Root Directory está como `backend`

**Erro: "Port already in use"**
- Use `$PORT` no comando (Railway define automaticamente)

**Erro: "Command not found: uvicorn"**
- Adicione `uvicorn` no `requirements.txt`
- Ou use: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

## 📝 Checklist Final

- [ ] Conta Railway criada
- [ ] Projeto criado e conectado ao GitHub
- [ ] Root Directory configurado: `backend`
- [ ] Start Command configurado: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Variável `API_ALLOWED_ORIGINS` configurada
- [ ] Deploy concluído com sucesso
- [ ] URL do backend copiada
- [ ] Backend testado (retorna JSON)
- [ ] Variável `VITE_API_BASE_URL` configurada no Netlify
- [ ] Novo deploy feito no Netlify
- [ ] Cadastro de hospital funcionando

## 🎯 URLs Importantes

Após configurar, você terá:

- **Frontend**: `https://seu-app.netlify.app`
- **Backend**: `https://seu-app.railway.app`
- **API Docs**: `https://seu-app.railway.app/docs`

## 💡 Dicas

1. **Railway oferece 500 horas grátis por mês** (suficiente para desenvolvimento)
2. **Logs são importantes**: Sempre verifique se houver erros
3. **Variáveis de ambiente**: Use para configurações diferentes (dev/prod)
4. **Backup**: Railway mantém o banco SQLite entre reinicializações

## 🆘 Precisa de Ajuda?

Se algo não funcionar:
1. Verifique os logs no Railway
2. Verifique se todas as variáveis estão configuradas
3. Teste o backend diretamente (curl ou navegador)
4. Verifique se o Netlify fez o deploy após adicionar a variável

---

*Última atualização: Janeiro 2025*

