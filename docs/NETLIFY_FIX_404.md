# 🔧 Correção: Erro 404 no Netlify ao Cadastrar Hospital

## ❌ Problema

Ao tentar cadastrar hospital, aparece erro 404 do Netlify. Isso significa que a requisição está indo para o Netlify (frontend) em vez do backend (Railway).

## ✅ Solução

A variável `VITE_API_BASE_URL` não está configurada ou não foi aplicada após o deploy.

### Passo 1: Verificar Variável no Netlify

1. **Acesse**: https://app.netlify.com
2. **Seu site** → **Site settings** → **Environment variables**
3. **Verifique** se `VITE_API_BASE_URL` está configurada
4. **Verifique** se o valor está correto (URL do Railway com `https://`)

### Passo 2: Obter URL do Backend

1. **Acesse**: https://railway.app
2. **Seu projeto** → **Clique no serviço**
3. **Settings** → **Networking**
4. **Copie a URL**: `https://seu-app.railway.app`

### Passo 3: Configurar/Atualizar Variável

1. No Netlify, **Site settings** → **Environment variables**
2. Se não existir, **adicione**:
   ```
   Key: VITE_API_BASE_URL
   Value: https://seu-app.railway.app
   ```
3. Se já existir, **edite** e verifique se está correto
4. **Salve**

### Passo 4: Fazer Novo Deploy (CRÍTICO!)

**IMPORTANTE**: Após adicionar/editar variável, **SEMPRE** faça novo deploy:

1. Vá em **Deploys**
2. Clique em **"Trigger deploy"**
3. **Selecione**: **"Clear cache and deploy site"**
4. Aguarde o deploy terminar (~2-3 minutos)

### Passo 5: Verificar no Console

1. Acesse seu site no Netlify
2. Abra o console do navegador (F12)
3. Digite:
   ```javascript
   console.log(import.meta.env.VITE_API_BASE_URL)
   ```
4. Deve mostrar a URL do Railway

Se mostrar `undefined` ou `http://127.0.0.1:8001`, a variável não foi aplicada. Faça novo deploy.

## 🔍 Verificação Completa

### 1. Testar Backend Diretamente

Abra no navegador:
```
https://seu-app.railway.app/hospital-access/register
```

Deve retornar erro de método (POST esperado), não 404. Se der 404, o backend não está rodando.

### 2. Testar Endpoint de Status

```
https://seu-app.railway.app/
```

Deve retornar:
```json
{"status": "ok", "message": "HospiCast API", ...}
```

### 3. Verificar CORS

Se o backend responder mas o frontend der erro de CORS, configure no backend:

No Railway, **Settings** → **Variables**, adicione:
```
API_ALLOWED_ORIGINS=https://seu-app.netlify.app,http://localhost:3000
```

## 🐛 Troubleshooting

### Variável não funciona após deploy

**Causa**: Variáveis são injetadas no **build**, não em runtime.

**Solução**:
- **SEMPRE** faça novo deploy após adicionar/editar variável
- Use **Clear cache and deploy site**
- Aguarde o build completo terminar

### Backend retorna 404

**Causa**: Backend não está rodando ou rota incorreta.

**Solução**:
1. Verifique logs no Railway
2. Teste backend diretamente no navegador
3. Verifique se a URL está correta

### CORS Error

**Causa**: Backend não permite requisições do Netlify.

**Solução**:
1. Configure `API_ALLOWED_ORIGINS` no Railway
2. Inclua a URL do Netlify: `https://seu-app.netlify.app`

## 📝 Checklist Final

- [ ] URL do Railway copiada corretamente
- [ ] Variável `VITE_API_BASE_URL` configurada no Netlify
- [ ] Valor da variável está correto (com `https://`)
- [ ] Novo deploy feito após configurar variável
- [ ] Cache limpo no deploy
- [ ] Console mostra URL correta
- [ ] Backend testado diretamente (funciona)
- [ ] CORS configurado no backend

---

*Última atualização: Janeiro 2025*

