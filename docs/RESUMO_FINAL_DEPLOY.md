# 📋 Resumo Final do Deploy - HospiCast

## ✅ URLs Finais Confirmadas

- **Backend**: https://hospicast-backend-fbuqwglmsq-rj.a.run.app
- **Frontend**: https://storage.googleapis.com/hospicast-frontend/index.html

## 🔧 Configurações Atuais

### Backend (Cloud Run)
- **Serviço**: `hospicast-backend`
- **Região**: `southamerica-east1`
- **URL**: https://hospicast-backend-fbuqwglmsq-rj.a.run.app
- **Memória**: 4Gi
- **CPU**: 2
- **Timeout**: 900s (15 minutos)
- **Porta**: 8080

### Frontend (Cloud Storage)
- **Bucket**: `hospicast-frontend`
- **URL**: https://storage.googleapis.com/hospicast-frontend/index.html
- **Configuração**: Site estático com `index.html`

### Banco de Dados (Cloud SQL)
- **Instância**: `hospicast-db`
- **Tipo**: PostgreSQL
- **Região**: `southamerica-east1`
- **Usuário**: `hospicast_user`
- **Database**: `hospicast`

## 🔐 Comandos Úteis

### Verificar Status do Backend

```bash
# Ver URL do backend
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(status.url)"

# Ver logs
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 20
```

### Atualizar CORS

```bash
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "API_ALLOWED_ORIGINS=*" \
    --quiet
```

### Resetar Senha do Banco

```bash
NEW_PASSWORD="SuaNovaSenhaForte123!"
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=$NEW_PASSWORD

CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
DATABASE_URL="postgresql://hospicast_user:${NEW_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL},API_ALLOWED_ORIGINS=*,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" \
    --quiet
```

### Atualizar Frontend

```bash
cd ~/portif-lio

# Atualizar URL do backend
echo "VITE_API_BASE_URL=https://hospicast-backend-fbuqwglmsq-rj.a.run.app" > frontend/.env.production

# Build
cd frontend
npm run build
cd ..

# Upload
gsutil -m rsync -r -d frontend/dist gs://hospicast-frontend
```

## 🧪 Testar

### Testar Backend

```bash
# Testar endpoint raiz
curl https://hospicast-backend-fbuqwglmsq-rj.a.run.app/

# Deve retornar: {"message":"HospiCast API funcionando!"}
```

### Testar CORS

```bash
curl -H "Origin: https://storage.googleapis.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://hospicast-backend-fbuqwglmsq-rj.a.run.app/forecast/predict \
     -v 2>&1 | grep -i "access-control"

# Deve retornar: < access-control-allow-origin: *
```

### Testar Frontend

1. Acesse: https://storage.googleapis.com/hospicast-frontend/index.html
2. Limpe o cache: `Ctrl+Shift+R`
3. Teste fazer uma previsão

## 📝 Variáveis de Ambiente do Backend

- `DATABASE_URL`: Conexão com PostgreSQL via Cloud SQL
- `API_ALLOWED_ORIGINS`: `*` (permite todas as origens)
- `LOG_LEVEL`: `INFO`
- `PROMETHEUS_ENABLED`: `true`
- `ENVIRONMENT`: `production`

## 🔍 Troubleshooting

### Erro de CORS
- Verificar se `API_ALLOWED_ORIGINS=*` está configurado
- Forçar nova revisão do Cloud Run
- Limpar cache do navegador

### Erro de Senha do Banco
- Resetar senha do usuário `hospicast_user`
- Atualizar `DATABASE_URL` no Cloud Run
- Aguardar 1-2 minutos para atualizar

### Erro 500
- Verificar logs do backend
- Verificar se o banco está acessível
- Verificar memória e timeout

## ✅ Checklist Final

- [x] Backend deployado: https://hospicast-backend-fbuqwglmsq-rj.a.run.app
- [x] Frontend deployado: https://storage.googleapis.com/hospicast-frontend/index.html
- [ ] CORS configurado e funcionando
- [ ] Banco de dados conectado
- [ ] Senha do banco correta
- [ ] Frontend usando URL correta do backend
- [ ] Tudo funcionando!

---

**Todas as URLs e configurações estão documentadas acima!** 🎯

