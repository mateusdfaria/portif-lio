# 🔧 Corrigir URL do Backend e CORS

## ❌ Problemas Identificados

1. **URL do backend mudou**: Agora é `hospicast-backend-fbuqwglmsq-rj.a.run.app`
2. **Barra dupla na URL**: `//forecast/predict` (deveria ser `/forecast/predict`)
3. **CORS ainda bloqueando**: Backend não está permitindo requisições
4. **Erro 401**: Autenticação falhando
5. **Erro 400**: Requisição malformada

## ✅ Solução Completa

### Passo 1: Obter Nova URL do Backend

```bash
# Obter URL atual do backend
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "✅ Nova URL do backend: $BACKEND_URL"
```

### Passo 2: Atualizar CORS no Backend

```bash
# Atualizar CORS para permitir todas as origens
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --quiet

echo "✅ CORS atualizado"
```

### Passo 3: Atualizar Frontend com Nova URL

```bash
cd ~/portif-lio

# Obter URL do backend
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# Remover barra final se houver
BACKEND_URL=${BACKEND_URL%/}

# Atualizar .env.production
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

echo "✅ .env.production atualizado:"
cat frontend/.env.production
```

### Passo 4: Rebuild e Reupload do Frontend

```bash
cd ~/portif-lio/frontend

# Rebuild
npm run build

cd ..

# Reupload
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

echo "✅ Frontend atualizado e reenviado"
```

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
cd ~/portif-lio

# === 1. OBTER NOVA URL DO BACKEND ===
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# Remover barra final
BACKEND_URL=${BACKEND_URL%/}

echo "✅ Nova URL do backend: $BACKEND_URL"
echo ""

# === 2. ATUALIZAR CORS ===
echo "🔄 Atualizando CORS..."
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --quiet

echo "✅ CORS atualizado"
echo ""

# === 3. ATUALIZAR FRONTEND ===
echo "🔄 Atualizando frontend..."
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

echo "✅ .env.production atualizado:"
cat frontend/.env.production
echo ""

# === 4. REBUILD FRONTEND ===
echo "🏗️  Fazendo build do frontend..."
cd frontend
npm run build
cd ..

# === 5. REUPLOAD ===
echo "📤 Fazendo upload..."
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

# === 6. RESULTADO ===
echo ""
echo "✅ Tudo atualizado!"
echo ""
echo "📋 URLs:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: https://storage.googleapis.com/hospicast-frontend/index.html"
echo ""
echo "⏳ Aguarde 1-2 minutos..."
echo "💡 Limpe o cache do navegador (Ctrl+Shift+R) e teste novamente"
```

---

## 🔍 Verificar Problema da Barra Dupla

O problema da barra dupla (`//forecast/predict`) pode estar no código. Vamos verificar:

```bash
cd ~/portif-lio

# Verificar como as URLs são construídas
grep -n "apiBaseUrl" frontend/src/App.jsx | head -10
```

**Se a URL do backend terminar com `/` e o código adicionar `/forecast/predict`, vai dar `//forecast/predict`.**

### Solução: Garantir que URL não Termine com Barra

O comando acima já remove a barra final com `${BACKEND_URL%/}`.

---

## 🔧 Corrigir Código (Se Necessário)

Se o problema persistir, pode ser necessário ajustar o código para garantir que não haja barras duplas:

```javascript
// Em vez de:
const url = `${apiBaseUrl}/forecast/predict`;

// Usar:
const url = `${apiBaseUrl.replace(/\/$/, '')}/forecast/predict`;
```

Mas primeiro, vamos tentar com a correção da URL no `.env.production`.

---

## ✅ Verificar se Funcionou

### 1. Verificar URL no Console do Navegador

1. Abra o frontend
2. Abra o console (F12)
3. Digite:
   ```javascript
   // Ver qual URL está sendo usada
   console.log(import.meta.env.VITE_API_BASE_URL);
   ```

### 2. Verificar Requisições

1. No DevTools (F12) → Network
2. Tente fazer uma previsão
3. Veja a URL da requisição
4. **Não deve ter barra dupla** (`//`)

### 3. Verificar CORS

1. No DevTools → Network
2. Clique na requisição
3. Vá em "Headers"
4. Procure por `Access-Control-Allow-Origin`
5. Deve ter: `*`

---

## 🚨 Se Ainda Não Funcionar

### Verificar Logs do Backend

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 30
```

### Testar Backend Diretamente

```bash
BACKEND_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

# Testar endpoint
curl "$BACKEND_URL/"

# Testar CORS
curl -H "Origin: https://storage.googleapis.com" \
     -X OPTIONS \
     "$BACKEND_URL/forecast/predict" \
     -v 2>&1 | grep -i "access-control"
```

---

**Execute os comandos acima para corrigir a URL e o CORS!** 🎯

