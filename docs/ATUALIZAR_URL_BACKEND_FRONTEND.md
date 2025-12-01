# 🔄 Atualizar URL do Backend no Frontend

## ❌ Problema: Frontend Usando URL Antiga

O backend mudou para `https://hospicast-backend-fbuqwglmsq-rj.a.run.app/`, mas o frontend ainda está usando a URL antiga.

## ✅ Solução: Atualizar Frontend

### Passo 1: Atualizar .env.production

```bash
cd ~/portif-lio

# Nova URL do backend (sem barra final)
BACKEND_URL="https://hospicast-backend-fbuqwglmsq-rj.a.run.app"

# Atualizar .env.production
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

echo "✅ .env.production atualizado:"
cat frontend/.env.production
```

### Passo 2: Rebuild do Frontend

```bash
cd frontend

# Rebuild
npm run build

# Verificar se build foi criado
ls -la dist/

cd ..
```

### Passo 3: Reupload para Cloud Storage

```bash
# Upload
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

echo "✅ Frontend atualizado e reenviado"
```

### Passo 4: Atualizar CORS no Backend

```bash
# Garantir que CORS está configurado
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --quiet

echo "✅ CORS atualizado"
```

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
cd ~/portif-lio

# === 1. ATUALIZAR .env.production ===
BACKEND_URL="https://hospicast-backend-fbuqwglmsq-rj.a.run.app"
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production

echo "✅ .env.production atualizado:"
cat frontend/.env.production
echo ""

# === 2. REBUILD ===
echo "🏗️  Fazendo build do frontend..."
cd frontend
npm run build

if [ ! -d "dist" ]; then
    echo "❌ Build falhou!"
    exit 1
fi

echo "✅ Build concluído"
cd ..

# === 3. REUPLOAD ===
echo "📤 Fazendo upload..."
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

# === 4. ATUALIZAR CORS ===
echo "🔄 Atualizando CORS..."
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --quiet

# === 5. RESULTADO ===
echo ""
echo "✅ Frontend atualizado com nova URL do backend!"
echo ""
echo "📋 URLs:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: https://storage.googleapis.com/hospicast-frontend/index.html"
echo ""
echo "⏳ Aguarde 1-2 minutos..."
echo "💡 Limpe o cache do navegador (Ctrl+Shift+R) e teste novamente"
```

---

## 🔍 Verificar se Funcionou

### 1. Verificar URL no Console do Navegador

1. Abra o frontend
2. Abra o console (F12)
3. Digite:
   ```javascript
   // Ver qual URL está sendo usada
   console.log(import.meta.env.VITE_API_BASE_URL);
   ```
4. **Deve mostrar**: `https://hospicast-backend-fbuqwglmsq-rj.a.run.app`

### 2. Verificar Requisições

1. No DevTools (F12) → Network
2. Tente fazer uma previsão
3. Veja a URL da requisição
4. **Deve ser**: `https://hospicast-backend-fbuqwglmsq-rj.a.run.app/forecast/predict`
5. **NÃO deve ser**: `https://hospicast-backend-4705370248.southamerica-east1.run.app/...`

### 3. Verificar se Não Há Erros

1. No console (F12)
2. Não deve aparecer mais:
   - Erro de CORS
   - Erro "Failed to fetch"
   - URL antiga do backend

---

## ⚠️ Importante

- **Limpe o cache do navegador** após o upload: `Ctrl+Shift+R`
- O Vite substitui `import.meta.env.VITE_API_BASE_URL` **durante o build**, não em runtime
- Por isso é necessário fazer **rebuild** após mudar o `.env.production`

---

**Execute os comandos acima para atualizar o frontend com a nova URL!** 🎯

