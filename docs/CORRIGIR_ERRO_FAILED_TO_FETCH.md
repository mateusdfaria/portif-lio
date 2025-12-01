# 🔧 Corrigir Erro "Failed to fetch"

## ❌ Erro: Failed to fetch

Este erro geralmente indica:
1. **Problema de CORS** - Backend não está permitindo requisições do frontend
2. **URL do backend incorreta** - Frontend está tentando acessar URL errada
3. **Backend não está respondendo** - Backend pode estar offline ou com erro

## ✅ Solução: Verificar e Corrigir

### Passo 1: Verificar URL do Backend no Frontend

```bash
cd ~/portif-lio

# Verificar .env.production
cat frontend/.env.production

# Deve ter:
# VITE_API_BASE_URL=https://hospicast-backend-4705370248.southamerica-east1.run.app
```

### Passo 2: Verificar CORS no Backend

```bash
# Ver variáveis de ambiente do Cloud Run
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env)"

# Verificar especificamente API_ALLOWED_ORIGINS
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='API_ALLOWED_ORIGINS')].value)"
```

### Passo 3: Atualizar CORS para Permitir Frontend

```bash
# Obter URL do frontend
FRONTEND_URL="https://storage.googleapis.com/hospicast-frontend"

# Atualizar CORS no backend
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=$FRONTEND_URL,https://storage.googleapis.com/hospicast-frontend,http://storage.googleapis.com/hospicast-frontend,https://hospicast-backend-4705370248.southamerica-east1.run.app,*" \
    --quiet

echo "✅ CORS atualizado"
```

### Passo 4: Verificar se Backend Está Funcionando

```bash
# Testar endpoint do backend
BACKEND_URL="https://hospicast-backend-4705370248.southamerica-east1.run.app"

# Testar endpoint raiz
curl $BACKEND_URL/

# Testar endpoint de busca de cidades
curl "$BACKEND_URL/api/cities/search?q=joinville"
```

### Passo 5: Verificar Logs do Backend

```bash
# Ver logs recentes
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
cd ~/portif-lio

# === 1. VERIFICAR URL DO BACKEND NO FRONTEND ===
echo "📋 Verificando .env.production:"
cat frontend/.env.production
echo ""

# === 2. VERIFICAR CORS ATUAL ===
echo "📋 CORS atual no backend:"
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='API_ALLOWED_ORIGINS')].value)"
echo ""

# === 3. ATUALIZAR CORS ===
echo "🔄 Atualizando CORS..."
FRONTEND_URL="https://storage.googleapis.com/hospicast-frontend"
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=$FRONTEND_URL,https://storage.googleapis.com/hospicast-frontend,http://storage.googleapis.com/hospicast-frontend,https://hospicast-backend-4705370248.southamerica-east1.run.app,*" \
    --quiet

echo "✅ CORS atualizado"
echo ""

# === 4. TESTAR BACKEND ===
echo "🧪 Testando backend..."
BACKEND_URL="https://hospicast-backend-4705370248.southamerica-east1.run.app"
curl -s $BACKEND_URL/ | head -5
echo ""
echo "✅ Backend está respondendo"
echo ""

# === 5. VERIFICAR LOGS ===
echo "📋 Últimos logs do backend:"
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 10
```

---

## 🔍 Debug no Navegador

### 1. Abrir Console do Navegador (F12)

1. Acesse o frontend
2. Pressione **F12** para abrir o DevTools
3. Vá na aba **Console**
4. Tente fazer uma previsão
5. Veja os erros que aparecem

### 2. Verificar Requisições de Rede

1. No DevTools, vá na aba **Network**
2. Tente fazer uma previsão
3. Veja se a requisição aparece
4. Clique na requisição e veja:
   - **Status**: Deve ser 200 (sucesso) ou outro código
   - **Headers**: Veja se há erros de CORS
   - **Response**: Veja a resposta do servidor

### 3. Erros Comuns

#### Erro de CORS:
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```

**Solução**: Execute o Passo 3 acima para atualizar CORS

#### Erro 404:
```
Failed to fetch: 404 Not Found
```

**Solução**: Verifique se a URL do backend está correta

#### Erro 500:
```
Failed to fetch: 500 Internal Server Error
```

**Solução**: Verifique os logs do backend (Passo 5)

---

## 🔄 Rebuild do Frontend (Se Necessário)

Se a URL do backend estiver incorreta no frontend:

```bash
cd ~/portif-lio

# Atualizar .env.production
echo "VITE_API_BASE_URL=https://hospicast-backend-4705370248.southamerica-east1.run.app" > frontend/.env.production

# Rebuild
cd frontend
npm run build
cd ..

# Reupload
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

echo "✅ Frontend atualizado"
```

---

## ✅ Checklist de Verificação

- [ ] URL do backend está correta no `.env.production`
- [ ] CORS está configurado para permitir o frontend
- [ ] Backend está respondendo (teste com curl)
- [ ] Logs do backend não mostram erros
- [ ] Console do navegador não mostra erros de CORS
- [ ] Requisições aparecem na aba Network do DevTools

---

## 🚨 Se Ainda Não Funcionar

1. **Copie o erro completo do console do navegador** (F12 → Console)
2. **Copie a URL da requisição que falhou** (F12 → Network)
3. **Verifique os logs do backend** com o comando acima
4. **Me envie essas informações** para eu ajudar melhor

---

**Execute os comandos acima e verifique o console do navegador (F12) para mais detalhes!** 🎯

