# 🔧 Corrigir CORS Definitivamente

## ❌ Erro: CORS Policy Blocked

```
Access to fetch at '...' from origin 'https://storage.googleapis.com' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header 
is present on the requested resource.
```

## ✅ Solução: Atualizar CORS com Origem Exata

O problema é que o CORS precisa incluir **exatamente** a origem do frontend.

### Passo 1: Atualizar CORS no Cloud Run

```bash
# === ATUALIZAR CORS COM ORIGEM EXATA ===
FRONTEND_ORIGIN="https://storage.googleapis.com"
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=$FRONTEND_ORIGIN,https://storage.googleapis.com,http://storage.googleapis.com,*" \
    --quiet

echo "✅ CORS atualizado"
```

### Passo 2: Verificar se Atualizou

```bash
# Ver variável de ambiente
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='API_ALLOWED_ORIGINS')].value)"
```

### Passo 3: Aguardar e Testar

O Cloud Run pode levar 1-2 minutos para atualizar. Depois:

1. **Limpe o cache do navegador**: `Ctrl+Shift+R`
2. **Tente fazer uma previsão novamente**
3. **Verifique o console** (F12) - não deve mais aparecer erro de CORS

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
# === ATUALIZAR CORS ===
echo "🔄 Atualizando CORS no backend..."
FRONTEND_ORIGIN="https://storage.googleapis.com"
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=$FRONTEND_ORIGIN,https://storage.googleapis.com,http://storage.googleapis.com,*" \
    --quiet

echo "✅ CORS atualizado"
echo ""

# === VERIFICAR ===
echo "📋 CORS configurado:"
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='API_ALLOWED_ORIGINS')].value)"
echo ""

# === AGUARDAR ===
echo "⏳ Aguarde 1-2 minutos para o Cloud Run atualizar..."
echo "💡 Depois, limpe o cache do navegador (Ctrl+Shift+R) e teste novamente"
```

---

## 🔍 Verificar se Funcionou

### 1. Testar CORS Manualmente

```bash
# Testar requisição com CORS
curl -H "Origin: https://storage.googleapis.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://hospicast-backend-4705370248.southamerica-east1.run.app/forecast/predict \
     -v
```

**Deve retornar**:
```
< Access-Control-Allow-Origin: https://storage.googleapis.com
```

### 2. Verificar no Navegador

1. Abra o frontend
2. Abra o console (F12)
3. Tente fazer uma previsão
4. **Não deve mais aparecer erro de CORS**

### 3. Verificar Headers da Resposta

No DevTools (F12) → Network:
1. Clique na requisição que foi feita
2. Vá em "Headers"
3. Procure por `Access-Control-Allow-Origin`
4. Deve ter: `https://storage.googleapis.com`

---

## 🔄 Se Ainda Não Funcionar

### Opção 1: Usar Wildcard (Menos Seguro, Mas Funciona)

```bash
# Permitir todas as origens
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --quiet

echo "✅ CORS configurado para permitir todas as origens"
```

### Opção 2: Verificar Logs do Backend

```bash
# Ver logs recentes
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 30
```

### Opção 3: Verificar Configuração do CORS no Código

O código do backend já está correto. O problema é apenas a variável de ambiente.

---

## 🎯 Solução Definitiva (Recomendada)

Execute este comando que garante todas as possíveis origens:

```bash
# === CONFIGURAR CORS COMPLETO ===
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=https://storage.googleapis.com,http://storage.googleapis.com,https://hospicast-backend-4705370248.southamerica-east1.run.app,http://localhost:3000,http://localhost:8001,*" \
    --quiet

echo "✅ CORS configurado com todas as origens possíveis"
echo ""
echo "⏳ Aguarde 1-2 minutos..."
echo "💡 Limpe o cache do navegador (Ctrl+Shift+R) e teste novamente"
```

---

## ✅ Checklist

- [ ] CORS atualizado no Cloud Run
- [ ] Aguardou 1-2 minutos para atualizar
- [ ] Limpou cache do navegador (Ctrl+Shift+R)
- [ ] Testou fazer uma previsão
- [ ] Console do navegador não mostra mais erro de CORS
- [ ] Requisições estão funcionando

---

**Execute o comando acima e aguarde 1-2 minutos antes de testar novamente!** 🎯

