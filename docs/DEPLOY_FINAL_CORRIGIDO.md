# 🚀 Deploy Final Corrigido

## ✅ Correções Aplicadas

1. **Dockerfile otimizado** - CmdStan já instalado no build, não tenta instalar na inicialização
2. **Porta corrigida** - Usa 8080 (padrão do Cloud Run)
3. **Health check removido** - Cloud Run faz health check automaticamente
4. **main.py otimizado** - Não tenta instalar CmdStan em produção

## 🔨 Rebuild e Deploy

### Passo 1: Rebuild da Imagem

```bash
# Rebuild com Dockerfile corrigido
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/hospicast-backend:latest ./backend
```

**⏱️ Aguarde o build terminar (5-10 minutos)**

### Passo 2: Deploy no Cloud Run

```bash
# 1. Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")

# 2. Definir variáveis
PROJECT_ID=$(gcloud config get-value project)
DB_PASSWORD="mateus22"
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

# 3. Deploy
gcloud run deploy hospicast-backend \
    --image gcr.io/${PROJECT_ID}/hospicast-backend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances ${CONNECTION_NAME} \
    --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --set-env-vars "LOG_LEVEL=INFO" \
    --set-env-vars "PROMETHEUS_ENABLED=true" \
    --set-env-vars "ENVIRONMENT=production" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --port 8080 \
    --min-instances 0
```

### Passo 3: Verificar Logs (se necessário)

```bash
# Ver logs em tempo real
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50 \
    --follow
```

### Passo 4: Obter URL

```bash
# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "✅ Deploy concluído!"
echo "🌐 URL: $SERVICE_URL"
```

### Passo 5: Testar

```bash
# Testar endpoint
curl $SERVICE_URL/

# Deve retornar: {"message": "HospiCast API funcionando!"}
```

## 🐛 Se Ainda Der Erro

### Ver Logs Detalhados

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100
```

### Problemas Comuns

1. **Erro de importação**: Verificar se todas as dependências estão no requirements.txt
2. **Erro de conexão com banco**: Verificar se DATABASE_URL está correta
3. **Timeout**: Aumentar timeout ou memory

---

**Faça rebuild e deploy novamente com as correções aplicadas!**

