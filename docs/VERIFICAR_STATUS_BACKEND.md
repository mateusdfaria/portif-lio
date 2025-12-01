# 🔍 Verificar Status do Backend no Cloud Run

## ❌ Problema: URL do Backend está vazia

Isso pode significar que o serviço não existe ou não está rodando.

## ✅ Solução: Verificar Status do Serviço

### 1. Listar Todos os Serviços Cloud Run

```bash
# Listar serviços na região
gcloud run services list --region southamerica-east1

# Listar todos os serviços
gcloud run services list
```

### 2. Verificar se o Serviço Existe

```bash
# Tentar descrever o serviço
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1
```

**Se aparecer erro "NOT_FOUND"**, o serviço não existe e precisa ser criado.

### 3. Verificar Status do Serviço

```bash
# Ver status detalhado
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="yaml"
```

### 4. Ver Logs

```bash
# Ver logs recentes
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

## 🔧 Se o Serviço Não Existir

### Opção 1: Verificar se está em outra região

```bash
# Listar em todas as regiões
gcloud run services list --platform managed
```

### Opção 2: Fazer Deploy do Backend

Se o serviço não existe, precisa fazer deploy:

```bash
# Ver guia completo
# docs/REBUILD_COM_CORRECAO_FINAL.md
```

## 📋 Comandos de Diagnóstico

```bash
# === 1. LISTAR SERVIÇOS ===
gcloud run services list --platform managed

# === 2. VERIFICAR SERVIÇO ESPECÍFICO ===
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1

# === 3. VER STATUS ===
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url,status.conditions)"

# === 4. VER LOGS ===
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 20
```

---

**Execute os comandos acima para diagnosticar o problema!**



