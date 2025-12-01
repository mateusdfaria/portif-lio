# 🔍 Diagnosticar Erro de Build e Deploy

## ❌ Problemas Identificados

1. **Build Failure**: Build step falhou
2. **Deploy Failure**: Container não inicia

## 🔍 Passo 1: Ver Logs do Build

```bash
# Ver logs do último build
gcloud builds list --limit=1

# Obter ID do build que falhou
BUILD_ID=$(gcloud builds list --limit=1 --format="value(id)")

# Ver logs detalhados
gcloud builds log $BUILD_ID
```

## 🔍 Passo 2: Ver Logs do Cloud Run

```bash
# Ver logs da última revisão
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100
```

**Procure por:**
- `error parsing env var "api_allowed_origins"`
- `ModuleNotFoundError`
- `ImportError`
- Outros erros de inicialização

## 🔍 Passo 3: Verificar Dockerfile

```bash
# No Cloud Shell
cd ~/portif-lio
cat backend/Dockerfile
```

**Verificar se:**
- Porta está configurada corretamente (8080)
- CMD está correto
- Dependências estão instaladas

## 🔍 Passo 4: Testar Build Localmente (Opcional)

```bash
# No Cloud Shell
cd ~/portif-lio/backend

# Testar build local (se Docker estiver disponível)
docker build -t test-backend .
docker run -p 8080:8080 test-backend
```

## ✅ Solução: Verificar e Corrigir

### 1. Ver Logs Completos

```bash
# Ver logs do Cloud Run
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 200
```

**Me envie os logs**, especialmente:
- Últimas 50 linhas
- Qualquer traceback ou erro

### 2. Verificar Código Local

```bash
# Verificar se o código está atualizado
cd ~/portif-lio
git status
git log -1

# Verificar arquivo config.py
cat backend/core/config.py | grep -A 10 "allowed_origins"
```

### 3. Rebuild com Debug

```bash
# Fazer rebuild com mais informações
PROJECT_ID=$(gcloud config get-value project)
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hospicast-backend:latest ./backend --verbosity=debug
```

## 📋 Comandos Completos de Diagnóstico

```bash
# === 1. VER LOGS DO BUILD ===
gcloud builds list --limit=1
BUILD_ID=$(gcloud builds list --limit=1 --format="value(id)")
gcloud builds log $BUILD_ID

# === 2. VER LOGS DO CLOUD RUN ===
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 200

# === 3. VERIFICAR CÓDIGO ===
cd ~/portif-lio
git status
cat backend/core/config.py | grep -A 10 "allowed_origins"

# === 4. VER DOCKERFILE ===
cat backend/Dockerfile
```

## 🔧 Possíveis Problemas e Soluções

### Problema 1: Erro de API_ALLOWED_ORIGINS

**Sintoma**: `error parsing env var "api_allowed_origins"`

**Solução**: Verificar se `backend/core/config.py` tem o validator correto

### Problema 2: Build Failure

**Sintoma**: Build step falha

**Solução**: Ver logs do build para identificar qual step falhou

### Problema 3: Container não inicia

**Sintoma**: Timeout ao iniciar

**Solução**: 
- Verificar logs
- Verificar se porta está correta
- Verificar se CMD está correto

---

**Execute os comandos de diagnóstico e me envie os logs para identificar o problema!**



