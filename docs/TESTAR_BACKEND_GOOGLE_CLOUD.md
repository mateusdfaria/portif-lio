# 🧪 Testar Backend no Google Cloud

## ✅ Status Atual

**Backend**: ✅ Já deployado no Cloud Run  
**Frontend**: ❌ Ainda não deployado

## 📋 Passos para Testar o Backend

### 1. Obter URL do Serviço

```bash
# Obter URL do Cloud Run
SERVICE_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "Backend URL: $SERVICE_URL"
```

### 2. Testar Endpoint Raiz

```bash
# Testar se o servidor está respondendo
curl $SERVICE_URL/

# Deve retornar algo como:
# {"message":"HospiCast API funcionando!"}
```

### 3. Testar Endpoints da API

```bash
# Testar endpoint de cidades
curl $SERVICE_URL/api/cities/search?q=joinville

# Testar endpoint de forecast (pode demorar)
curl -X POST $SERVICE_URL/api/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "demanda_hospitalar",
    "horizon": 7
  }'

# Testar endpoint de hospitais
curl $SERVICE_URL/api/hospitals
```

### 4. Verificar Logs

```bash
# Ver logs em tempo real
gcloud run services logs tail hospicast-backend \
    --platform managed \
    --region southamerica-east1

# Ver últimas 50 linhas
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50
```

### 5. Verificar Status do Serviço

```bash
# Ver informações do serviço
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1

# Ver métricas
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url,status.conditions)"
```

## 🔍 Verificar se Está Funcionando

### Teste Completo

```bash
# 1. Obter URL
SERVICE_URL=$(gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)")

echo "🔗 Backend URL: $SERVICE_URL"

# 2. Testar endpoint raiz
echo "📡 Testando endpoint raiz..."
curl -s $SERVICE_URL/ | jq .

# 3. Testar endpoint de cidades
echo "🏙️ Testando busca de cidades..."
curl -s "$SERVICE_URL/api/cities/search?q=joinville" | jq .

# 4. Verificar logs
echo "📋 Últimas linhas dos logs:"
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 10
```

## 🌐 Testar no Navegador

1. **Obter URL**:
   ```bash
   gcloud run services describe hospicast-backend \
       --platform managed \
       --region southamerica-east1 \
       --format="value(status.url)"
   ```

2. **Abrir no navegador**:
   - Cole a URL no navegador
   - Deve aparecer: `{"message":"HospiCast API funcionando!"}`

3. **Testar endpoints**:
   - `{URL}/api/cities/search?q=joinville`
   - `{URL}/api/hospitals`
   - `{URL}/docs` (documentação Swagger/OpenAPI)

## ⚠️ Problemas Comuns

### Erro 403 ou 401
```bash
# Verificar se o serviço está público
gcloud run services get-iam-policy hospicast-backend \
    --platform managed \
    --region southamerica-east1
```

### Erro 500 ou Timeout
```bash
# Verificar logs para identificar o problema
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100
```

### Erro de Conexão com Banco
```bash
# Verificar se o Cloud SQL está acessível
gcloud sql instances describe hospicast-db

# Verificar connection name
gcloud sql instances describe hospicast-db \
    --format="value(connectionName)"
```

## 📊 Monitoramento

### Ver Métricas no Console

1. Ir para: https://console.cloud.google.com/run
2. Clicar em `hospicast-backend`
3. Ver métricas de:
   - Requisições
   - Latência
   - Erros
   - CPU/Memória

### Ver Logs no Console

1. Ir para: https://console.cloud.google.com/logs
2. Filtrar por: `resource.type="cloud_run_revision"`
3. Filtrar por: `resource.labels.service_name="hospicast-backend"`

## 🎯 Próximos Passos

Após confirmar que o backend está funcionando:

1. ✅ **Backend funcionando** → Pronto para usar
2. ⏭️ **Deploy do Frontend** → Pode ser feito depois
3. 🔗 **Configurar CORS** → Se o frontend for deployado em outro lugar

---

**Execute os comandos acima para testar o backend!**



