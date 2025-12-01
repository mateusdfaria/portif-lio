# ⚡ Configuração Rápida do Netlify

## 🎯 URL do Backend

```
https://web-production-039db.up.railway.app
```

## 📋 Passo a Passo Rápido

### 1. Configurar Variável no Netlify

1. **Acesse**: https://app.netlify.com
2. **Seu site** → **Site settings** → **Environment variables**
3. **Adicione**:
   ```
   Key: VITE_API_BASE_URL
   Value: https://web-production-039db.up.railway.app
   ```
4. **Clique em Save**

### 2. Fazer Novo Deploy (OBRIGATÓRIO!)

1. Vá em **Deploys**
2. Clique em **"Trigger deploy"**
3. Selecione **"Clear cache and deploy site"**
4. Aguarde ~2-3 minutos

### 3. Verificar

1. Acesse seu site no Netlify
2. Abra console (F12)
3. Digite: `console.log(import.meta.env.VITE_API_BASE_URL)`
4. Deve mostrar: `https://web-production-039db.up.railway.app`

## 🔍 Testar Backend

Abra no navegador:
```
https://web-production-039db.up.railway.app/
```

Deve retornar JSON com status "ok".

## ✅ Pronto!

Após fazer o deploy, o cadastro de hospital deve funcionar!

---

*Última atualização: Janeiro 2025*

