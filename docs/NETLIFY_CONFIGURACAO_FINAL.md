# 🚀 Configuração Final do Netlify

## ✅ Backend Funcionando no Railway

Agora vamos conectar o frontend (Netlify) ao backend (Railway).

## 📋 Passo a Passo

### Passo 1: Obter URL do Backend

1. **Acesse**: https://railway.app
2. **Seu projeto** → **Clique no serviço**
3. **Settings** → **Networking**
4. **Copie a URL**: `https://seu-app.railway.app`
   (Exemplo: `https://hospicast-production.up.railway.app`)

### Passo 2: Configurar Variável no Netlify

1. **Acesse**: https://app.netlify.com
2. **Seu site** → **Site settings** → **Environment variables**
3. **Adicione**:
   ```
   Key: VITE_API_BASE_URL
   Value: https://seu-app.railway.app
   ```
   (Substitua pela URL real do Railway que você copiou)

4. **IMPORTANTE**: Clique em **Save**

### Passo 3: Fazer Novo Deploy

Após adicionar a variável, **SEMPRE** faça um novo deploy:

1. Vá em **Deploys**
2. Clique em **"Trigger deploy"**
3. Selecione **"Clear cache and deploy site"**
4. Aguarde o deploy terminar (~2-3 minutos)

### Passo 4: Verificar Funcionamento

1. Acesse seu site no Netlify
2. Abra o console do navegador (F12)
3. Tente cadastrar um hospital
4. ✅ Deve funcionar!

## 🔍 Verificação Rápida

### Testar Backend Diretamente

Abra no navegador:
```
https://seu-app.railway.app/
```

Deve retornar:
```json
{"status": "ok", "message": "HospiCast API", ...}
```

### Testar no Console do Navegador

No Netlify, abra o console (F12) e digite:
```javascript
console.log(import.meta.env.VITE_API_BASE_URL)
```

Deve mostrar a URL do Railway.

## 🐛 Troubleshooting

### Erro: "Failed to fetch"

**Causa**: CORS não configurado ou URL incorreta.

**Solução**:
1. Verifique se a URL do Railway está correta
2. Configure CORS no backend (já está configurado, mas verifique)

### Erro: "ERR_CONNECTION_REFUSED"

**Causa**: Variável não configurada ou deploy não feito.

**Solução**:
1. Verifique se `VITE_API_BASE_URL` está configurada
2. **Faça novo deploy** após adicionar variável
3. Limpe cache: **Clear cache and deploy site**

### Variável não funciona

**Causa**: Deploy não foi feito após adicionar variável.

**Solução**:
- Variáveis são injetadas no **build**, não em runtime
- **SEMPRE** faça novo deploy após adicionar variável
- Use **Clear cache and deploy site**

## 📝 Checklist

- [ ] URL do Railway copiada
- [ ] Variável `VITE_API_BASE_URL` configurada no Netlify
- [ ] Novo deploy feito no Netlify
- [ ] Backend testado diretamente (retorna JSON)
- [ ] Console mostra URL correta
- [ ] Cadastro de hospital funcionando

## 🎯 URLs Finais

Após configurar, você terá:

- **Frontend**: `https://seu-app.netlify.app`
- **Backend**: `https://seu-app.railway.app`
- **API Docs**: `https://seu-app.railway.app/docs`

---

*Última atualização: Janeiro 2025*

