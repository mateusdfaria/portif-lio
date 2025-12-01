# 🔍 Análise e Correção do Frontend

## 📋 Análise da Configuração Atual

### ✅ O que está CORRETO:

1. **index.html**: 
   - Tem `<div id="root"></div>` ✅
   - Carrega `/src/main.jsx` ✅

2. **main.jsx**: 
   - Renderiza o App corretamente ✅

3. **App.jsx**: 
   - Lê `import.meta.env.VITE_API_BASE_URL` ✅
   - Tem fallback para `http://127.0.0.1:8001` ✅

### ⚠️ Problemas Identificados:

1. **index.html no build**: O caminho `/src/main.jsx` é para desenvolvimento. No build, o Vite gera um arquivo diferente.

2. **Variável de ambiente**: O arquivo `.env.production` precisa estar presente durante o build.

3. **Caminhos relativos**: O `vite.config.js` precisa ter `base: './'` para funcionar no Cloud Storage.

## ✅ Solução Completa

### Passo 1: Verificar/Criar .env.production

```bash
cd ~/portif-lio/frontend

# Verificar se existe
cat .env.production 2>/dev/null || echo "Arquivo não existe"

# Criar/Atualizar com a URL do backend
echo "VITE_API_BASE_URL=https://hospicast-backend-4705370248.southamerica-east1.run.app" > .env.production

# Verificar
cat .env.production
```

### Passo 2: Atualizar vite.config.js

```bash
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './',  // Caminhos relativos para Cloud Storage
  server: { port: 3000 },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.js',
  },
});
EOF
```

### Passo 3: Rebuild Limpo

```bash
cd ~/portif-lio/frontend

# Limpar build anterior
rm -rf dist node_modules/.vite

# Rebuild
npm run build

# Verificar se a variável foi incluída
echo "Verificando se VITE_API_BASE_URL foi incluída no build:"
grep -r "hospicast-backend" dist/ || echo "Variável não encontrada (pode estar minificada)"
```

### Passo 4: Verificar index.html Gerado

```bash
# Ver o index.html gerado
cat dist/index.html

# Deve ter algo como:
# <script type="module" src="./assets/index-[hash].js"></script>
# NÃO deve ter: src="/src/main.jsx"
```

### Passo 5: Reupload

```bash
cd ~/portif-lio

# Upload
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

echo "✅ Frontend atualizado!"
```

---

## 🔍 Verificação Detalhada

### 1. Verificar se a Variável Está no Build

```bash
cd ~/portif-lio/frontend

# Fazer build
npm run build

# Procurar pela URL do backend no código gerado
grep -r "hospicast-backend" dist/ || echo "Não encontrado (pode estar minificada)"

# Verificar arquivos gerados
ls -la dist/
ls -la dist/assets/
```

### 2. Testar Localmente (Opcional)

```bash
cd ~/portif-lio/frontend

# Servir o build localmente
npm run preview

# Acessar http://localhost:4173
# Verificar console do navegador (F12)
```

### 3. Verificar Console do Navegador

No navegador, abra o console (F12) e verifique:

1. **Erros de JavaScript**: Procure por erros vermelhos
2. **Requisições de rede**: Veja se as requisições para o backend estão sendo feitas
3. **Variável de ambiente**: No console, digite:
   ```javascript
   // Isso não funciona no navegador, mas você pode verificar nas requisições
   ```

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
cd ~/portif-lio

# === 1. CONFIGURAR VARIÁVEL DE AMBIENTE ===
echo "VITE_API_BASE_URL=https://hospicast-backend-4705370248.southamerica-east1.run.app" > frontend/.env.production
echo "✅ .env.production criado"
cat frontend/.env.production

# === 2. ATUALIZAR VITE.CONFIG.JS ===
cat > frontend/vite.config.js << 'EOF'
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './',
  server: { port: 3000 },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.js',
  },
});
EOF
echo "✅ vite.config.js atualizado"

# === 3. REBUILD LIMPO ===
cd frontend
rm -rf dist node_modules/.vite
npm run build

# === 4. VERIFICAR BUILD ===
echo ""
echo "📋 Verificando build:"
ls -la dist/
echo ""
echo "📄 Conteúdo do index.html gerado:"
head -15 dist/index.html

cd ..

# === 5. REUPLOAD ===
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend

# === 6. RESULTADO ===
echo ""
echo "✅ Frontend atualizado e reenviado!"
echo "🌐 Acesse: https://storage.googleapis.com/hospicast-frontend/index.html"
echo ""
echo "💡 Limpe o cache do navegador (Ctrl+Shift+R) antes de acessar"
```

---

## 🔧 Debug Adicional

### Se ainda estiver em branco:

1. **Verificar arquivos no bucket**:
   ```bash
   gsutil ls -r gs://hospicast-frontend
   ```

2. **Verificar index.html no bucket**:
   ```bash
   gsutil cat gs://hospicast-frontend/index.html
   ```

3. **Verificar permissões**:
   ```bash
   gsutil iam get gs://hospicast-frontend
   ```

4. **Testar acesso direto a um asset**:
   ```bash
   # Listar assets
   gsutil ls gs://hospicast-frontend/assets/
   
   # Tentar acessar um asset diretamente no navegador
   ```

5. **Verificar console do navegador**:
   - Abra F12
   - Vá em "Console"
   - Veja os erros
   - Vá em "Network" e veja quais requisições falharam

---

## 📝 Notas Importantes

1. **Variáveis de ambiente no Vite**:
   - Devem começar com `VITE_`
   - São substituídas no código durante o build
   - Não funcionam em runtime (são "baked in" no build)

2. **index.html**:
   - O arquivo original (`frontend/index.html`) é um template
   - O Vite gera um novo `index.html` na pasta `dist/` durante o build
   - O arquivo gerado tem os caminhos corretos para os assets

3. **Caminhos relativos**:
   - Com `base: './'`, os caminhos ficam relativos
   - Funciona melhor no Cloud Storage

---

**Execute os comandos acima para corrigir completamente o frontend!** 🎯

