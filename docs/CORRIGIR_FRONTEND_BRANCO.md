# 🔧 Corrigir Frontend em Branco

## ❌ Problema: Frontend aparece em branco

O frontend está carregando, mas aparece em branco. Isso geralmente acontece porque:

1. **Caminhos dos assets estão incorretos** (Vite usa caminhos absolutos `/`)
2. **Base path não configurado** no Vite
3. **Arquivos JavaScript não estão sendo carregados**

## ✅ Solução: Configurar Base Path no Vite

### Passo 1: Atualizar vite.config.js

O Vite precisa saber qual é o base path para gerar os caminhos corretos dos assets.

```bash
cd ~/portif-lio/frontend

# Verificar vite.config.js atual
cat vite.config.js
```

### Passo 2: Atualizar Configuração

Adicione `base: './'` no `vite.config.js` para usar caminhos relativos:

```bash
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './',  // Usar caminhos relativos para funcionar no Cloud Storage
  server: { port: 3000 },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.js',
  },
});
EOF
```

### Passo 3: Rebuild e Reupload

```bash
cd ~/portif-lio

# Rebuild com a nova configuração
cd frontend
npm run build
cd ..

# Reupload
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

echo "✅ Frontend atualizado!"
```

---

## 🔍 Verificar o Problema

### 1. Verificar Console do Navegador

Abra o console do navegador (F12) e verifique se há erros como:
- `Failed to load resource: 404`
- `Uncaught SyntaxError`
- `Cannot find module`

### 2. Verificar Arquivos no Bucket

```bash
# Listar arquivos no bucket
gsutil ls -r gs://hospicast-frontend

# Verificar se index.html existe
gsutil cat gs://hospicast-frontend/index.html
```

### 3. Verificar Caminhos no index.html

O `index.html` gerado deve ter caminhos relativos (sem `/` no início):

```bash
# Ver conteúdo do index.html gerado
cat frontend/dist/index.html
```

**Deve ter algo como:**
```html
<script type="module" src="./assets/index-abc123.js"></script>
```

**NÃO deve ter:**
```html
<script type="module" src="/assets/index-abc123.js"></script>
```

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
cd ~/portif-lio

# === 1. ATUALIZAR VITE.CONFIG.JS ===
cat > frontend/vite.config.js << 'EOF'
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './',  // Caminhos relativos para Cloud Storage
  server: { port: 3000 },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.js',
  },
});
EOF

# === 2. REBUILD ===
cd frontend
npm run build

# Verificar se os caminhos estão corretos
echo "Verificando index.html gerado:"
head -20 dist/index.html

cd ..

# === 3. REUPLOAD ===
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

# === 4. VERIFICAR ===
echo ""
echo "✅ Frontend atualizado!"
echo "🌐 Acesse: https://storage.googleapis.com/hospicast-frontend/index.html"
echo ""
echo "💡 Dica: Limpe o cache do navegador (Ctrl+Shift+R) se ainda aparecer em branco"
```

---

## 🔄 Alternativa: Usar Cloud CDN com Load Balancer

Se o problema persistir, podemos configurar um Load Balancer com Cloud CDN:

```bash
# Criar backend bucket
gcloud compute backend-buckets create hospicast-frontend-backend \
    --gcs-bucket-name=hospicast-frontend

# Criar URL map
gcloud compute url-maps create hospicast-frontend-map \
    --default-backend-bucket=hospicast-frontend-backend

# Criar proxy HTTP
gcloud compute target-http-proxies create hospicast-frontend-proxy \
    --url-map=hospicast-frontend-map

# Criar forwarding rule (IP público)
gcloud compute forwarding-rules create hospicast-frontend-rule \
    --global \
    --target-http-proxy=hospicast-frontend-proxy \
    --ports=80

# Obter IP
FRONTEND_IP=$(gcloud compute forwarding-rules describe hospicast-frontend-rule \
    --global \
    --format="value(IPAddress)")

echo "Frontend IP: $FRONTEND_IP"
```

---

## ⚠️ Troubleshooting Adicional

### Se ainda estiver em branco:

1. **Limpar cache do navegador**: Ctrl+Shift+R (ou Cmd+Shift+R no Mac)

2. **Verificar se os arquivos foram uploadados**:
   ```bash
   gsutil ls -r gs://hospicast-frontend | head -20
   ```

3. **Verificar permissões do bucket**:
   ```bash
   gsutil iam get gs://hospicast-frontend
   ```

4. **Testar acesso direto aos arquivos**:
   ```
   https://storage.googleapis.com/hospicast-frontend/assets/index-[hash].js
   ```

5. **Verificar console do navegador** para erros específicos

---

**Execute os comandos acima para corrigir o frontend em branco!** 🎯

