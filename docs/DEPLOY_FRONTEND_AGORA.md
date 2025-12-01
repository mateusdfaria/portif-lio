# 🌐 Deploy do Frontend - Backend Já Está Funcionando

## ✅ Backend Confirmado

Seu backend está funcionando em:
```
https://hospicast-backend-4705370248.southamerica-east1.run.app
```

## 🚀 Deploy do Frontend

Execute estes comandos no Cloud Shell:

```bash
cd ~/portif-lio

# === CONFIGURAÇÃO ===
PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME="hospicast-frontend"
BACKEND_URL="https://hospicast-backend-4705370248.southamerica-east1.run.app"

echo "✅ Backend URL: $BACKEND_URL"

# === 1. CRIAR BUCKET ===
echo ""
echo "📦 Criando bucket para frontend..."
gsutil mb -p $PROJECT_ID -c STANDARD -l southamerica-east1 gs://$BUCKET_NAME 2>/dev/null || echo "Bucket já existe"
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
echo "✅ Bucket criado e configurado"

# === 2. CONFIGURAR FRONTEND ===
echo ""
echo "⚙️  Configurando frontend..."
echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production
echo "✅ Variável de ambiente configurada"

# === 3. BUILD FRONTEND ===
echo ""
echo "🏗️  Fazendo build do frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
fi

npm run build

if [ ! -d "dist" ]; then
    echo "❌ Build falhou! Pasta dist não foi criada."
    exit 1
fi

echo "✅ Build concluído!"
cd ..

# === 4. UPLOAD ===
echo ""
echo "📤 Fazendo upload do frontend..."
gsutil -m rsync -r -d frontend/dist gs://$BUCKET_NAME
echo "✅ Upload concluído!"

# === 5. CONFIGURAR CORS ===
echo ""
echo "🔗 Configurando CORS no backend..."
FRONTEND_URL="https://storage.googleapis.com/$BUCKET_NAME"
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=$FRONTEND_URL,https://storage.googleapis.com/$BUCKET_NAME,http://storage.googleapis.com/$BUCKET_NAME,*" \
    --quiet

echo "✅ CORS configurado!"

# === 6. RESULTADO ===
echo ""
echo "🎉 Deploy Completo Concluído!"
echo ""
echo "📋 URLs:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: https://storage.googleapis.com/$BUCKET_NAME/index.html"
echo ""
echo "🌐 Acesse seu frontend no navegador:"
echo "   https://storage.googleapis.com/$BUCKET_NAME/index.html"
echo ""
```

---

## 📋 Comandos Rápidos (Copiar e Colar Tudo)

```bash
cd ~/portif-lio && PROJECT_ID=$(gcloud config get-value project) && BUCKET_NAME="hospicast-frontend" && BACKEND_URL="https://hospicast-backend-4705370248.southamerica-east1.run.app" && echo "✅ Backend: $BACKEND_URL" && gsutil mb -p $PROJECT_ID -c STANDARD -l southamerica-east1 gs://$BUCKET_NAME 2>/dev/null || echo "Bucket já existe" && gsutil web set -m index.html -e index.html gs://$BUCKET_NAME && gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME && echo "VITE_API_BASE_URL=$BACKEND_URL" > frontend/.env.production && cd frontend && npm install && npm run build && cd .. && gsutil -m rsync -r -d frontend/dist gs://$BUCKET_NAME && FRONTEND_URL="https://storage.googleapis.com/$BUCKET_NAME" && gcloud run services update hospicast-backend --platform managed --region southamerica-east1 --set-env-vars "API_ALLOWED_ORIGINS=$FRONTEND_URL,https://storage.googleapis.com/$BUCKET_NAME,http://storage.googleapis.com/$BUCKET_NAME,*" --quiet && echo "" && echo "🎉 Deploy Completo!" && echo "Backend:  $BACKEND_URL" && echo "Frontend: https://storage.googleapis.com/$BUCKET_NAME/index.html"
```

---

## ✅ Depois do Deploy

1. **Acesse o frontend** no navegador:
   ```
   https://storage.googleapis.com/hospicast-frontend/index.html
   ```

2. **Teste a integração**:
   - Faça uma busca de cidade
   - Verifique se não há erros no console (F12)

3. **Verificar logs** (se necessário):
   ```bash
   gcloud run services logs read hospicast-backend \
       --platform managed \
       --region southamerica-east1 \
       --limit 20
   ```

---

**Execute os comandos acima para fazer o deploy do frontend!** 🎯

