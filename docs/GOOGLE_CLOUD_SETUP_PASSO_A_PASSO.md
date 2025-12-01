# 🚀 Guia Passo a Passo - Deploy no Google Cloud

Este guia te levará do zero até ter o HospiCast rodando no Google Cloud.

## 📋 Pré-requisitos

1. **Conta Google Cloud** - Crie em [cloud.google.com](https://cloud.google.com)
2. **Google Cloud SDK** - Instale o `gcloud` CLI
3. **Docker** instalado (opcional, mas recomendado)
4. **Projeto no GitHub** (recomendado para CI/CD)

## 🔧 Passo 1: Instalar Google Cloud SDK

### Windows (PowerShell)

```powershell
# Baixar e instalar o SDK
# Acesse: https://cloud.google.com/sdk/docs/install

# Ou usar Chocolatey
choco install gcloudsdk

# Verificar instalação
gcloud --version
```

### Linux/Mac

```bash
# Instalar via script
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verificar
gcloud --version
```

## 🔐 Passo 2: Autenticar e Configurar

```bash
# Fazer login
gcloud auth login

# Criar novo projeto (ou usar existente)
gcloud projects create hospicast-prod --name="HospiCast Production"

# Definir projeto como padrão
gcloud config set project hospicast-prod

# Verificar configuração
gcloud config list
```

**Nota**: Anote o **PROJECT_ID** (ex: `hospicast-prod-123456`)

## 💳 Passo 3: Habilitar Billing e APIs

```bash
# Habilitar billing (via console web)
# Acesse: https://console.cloud.google.com/billing

# Habilitar APIs necessárias
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## 🗄️ Passo 4: Criar Banco de Dados Cloud SQL

### 4.1 Criar Instância PostgreSQL

```bash
# Substitua SEU_PROJECT_ID pelo ID do seu projeto
gcloud sql instances create hospicast-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=southamerica-east1 \
    --root-password=SUA_SENHA_FORTE_AQUI \
    --storage-type=SSD \
    --storage-size=20GB \
    --backup-start-time=03:00 \
    --enable-bin-log
```

**⚠️ IMPORTANTE**: 
- Escolha uma senha forte e guarde em local seguro
- `db-f1-micro` é o tier mais barato (suficiente para começar)
- `southamerica-east1` é São Paulo (melhor latência para Brasil)

### 4.2 Criar Banco de Dados

```bash
# Criar banco de dados
gcloud sql databases create hospicast --instance=hospicast-db
```

### 4.3 Criar Usuário

```bash
# Criar usuário para aplicação
gcloud sql users create hospicast_user \
    --instance=hospicast-db \
    --password=OUTRA_SENHA_FORTE_AQUI
```

### 4.4 Obter IP Público

```bash
# Ver informações da instância
gcloud sql instances describe hospicast-db

# Ou obter apenas o IP
gcloud sql instances describe hospicast-db \
    --format="get(ipAddresses[0].ipAddress)"
```

**Anote o IP público** (será usado depois)

## 📝 Passo 5: Configurar Schema do Banco

### Opção A: Via SQL direto

```bash
# Conectar via psql (se tiver instalado)
psql -h [IP_PUBLICO] -U hospicast_user -d hospicast

# Dentro do psql, execute:
\i database/init_hospital_access.sql
```

### Opção B: Via Python (Recomendado)

```bash
# Configurar variável de ambiente
# Substitua [IP_PUBLICO] e [SENHA] pelos valores reais
export DATABASE_URL="postgresql://hospicast_user:SENHA@[IP_PUBLICO]:5432/hospicast"

# Executar script de inicialização
cd backend
python scripts/init_database.py
```

## 🐳 Passo 6: Preparar e Testar Docker Localmente

### 6.1 Testar Build Local

```bash
# No diretório raiz do projeto
cd backend

# Build da imagem
docker build -t hospicast-backend:local .

# Testar localmente
docker run -p 8000:8000 \
    -e DATABASE_URL="postgresql://hospicast_user:SENHA@[IP_PUBLICO]:5432/hospicast" \
    -e API_ALLOWED_ORIGINS="*" \
    hospicast-backend:local
```

### 6.2 Verificar se funciona

Abra no navegador: `http://localhost:8000`

Deve retornar: `{"message": "HospiCast API funcionando!"}`

## 📤 Passo 7: Fazer Push da Imagem para Google Container Registry

### 7.1 Configurar Docker para GCR

```bash
# Configurar autenticação
gcloud auth configure-docker
```

### 7.2 Build e Push

```bash
# Substitua SEU_PROJECT_ID
export PROJECT_ID="seu-project-id"

# Build da imagem
docker build -t gcr.io/$PROJECT_ID/hospicast-backend:latest ./backend

# Push para Container Registry
docker push gcr.io/$PROJECT_ID/hospicast-backend:latest
```

**OU** usar Cloud Build (mais fácil):

```bash
# Build e push em um comando
gcloud builds submit --tag gcr.io/$PROJECT_ID/hospicast-backend:latest ./backend
```

## 🚀 Passo 8: Deploy no Cloud Run

### 8.1 Obter Connection Name do Cloud SQL

```bash
# Obter connection name (necessário para Cloud Run)
gcloud sql instances describe hospicast-db \
    --format="value(connectionName)"
```

**Anote o connection name** (formato: `PROJECT_ID:REGION:INSTANCE`)

### 8.2 Criar Secret para Senha do Banco (Opcional mas Recomendado)

```bash
# Criar secret com a senha
echo -n "SUA_SENHA_DO_BANCO" | gcloud secrets create db-password --data-file=-

# Dar permissão ao Cloud Run
gcloud secrets add-iam-policy-binding db-password \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 8.3 Deploy no Cloud Run

```bash
# Substitua os valores entre []
gcloud run deploy hospicast-backend \
    --image gcr.io/$PROJECT_ID/hospicast-backend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances [CONNECTION_NAME] \
    --set-env-vars "DATABASE_URL=postgresql://hospicast_user:[SENHA]@localhost/hospicast?host=/cloudsql/[CONNECTION_NAME]" \
    --set-env-vars "API_ALLOWED_ORIGINS=https://seu-frontend.netlify.app,http://localhost:3000" \
    --set-env-vars "LOG_LEVEL=INFO" \
    --set-env-vars "PROMETHEUS_ENABLED=true" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0
```

**Exemplo completo**:

```bash
gcloud run deploy hospicast-backend \
    --image gcr.io/hospicast-prod-123456/hospicast-backend:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances hospicast-prod-123456:southamerica-east1:hospicast-db \
    --set-env-vars "DATABASE_URL=postgresql://hospicast_user:minhasenha123@localhost/hospicast?host=/cloudsql/hospicast-prod-123456:southamerica-east1:hospicast-db" \
    --set-env-vars "API_ALLOWED_ORIGINS=https://hospicast.netlify.app" \
    --set-env-vars "LOG_LEVEL=INFO" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10
```

### 8.4 Obter URL do Deploy

Após o deploy, você receberá uma URL como:
```
https://hospicast-backend-xxxxx-uc.a.run.app
```

**Anote esta URL** - será usada no frontend!

## ✅ Passo 9: Verificar Deploy

### 9.1 Testar Endpoint

```bash
# Testar endpoint raiz
curl https://hospicast-backend-xxxxx-uc.a.run.app/

# Deve retornar: {"message": "HospiCast API funcionando!"}
```

### 9.2 Ver Logs

```bash
# Ver logs em tempo real
gcloud run services logs read hospicast-backend --limit 50

# Ou no console web
# https://console.cloud.google.com/run
```

### 9.3 Verificar no Console

Acesse: https://console.cloud.google.com/run

Você deve ver o serviço `hospicast-backend` rodando.

## 🔗 Passo 10: Configurar Frontend

Atualize a URL da API no frontend para apontar para o Cloud Run:

```javascript
// frontend/src/App.jsx ou onde estiver a configuração
const API_BASE_URL = "https://hospicast-backend-xxxxx-uc.a.run.app";
```

## 🔄 Passo 11: Configurar CI/CD (Opcional)

### 11.1 Criar Trigger no Cloud Build

```bash
# Conectar repositório (GitHub, GitLab, etc)
# Via console: https://console.cloud.google.com/cloud-build/triggers

# Ou criar trigger via CLI
gcloud builds triggers create github \
    --repo-name=portif-lio \
    --repo-owner=SEU_USUARIO \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

### 11.2 Atualizar cloudbuild.yaml

O arquivo `cloudbuild.yaml` já está configurado! Apenas verifique se o `PROJECT_ID` está correto.

## 💰 Passo 12: Monitorar Custos

### Estimativa de Custos Mensais

- **Cloud SQL (db-f1-micro)**: ~R$ 35-50/mês
- **Cloud Run**: Pay-per-use (primeiros 2 milhões de requisições grátis)
- **Container Registry**: ~R$ 0,10/GB/mês
- **Total estimado**: ~R$ 40-60/mês para começar

### Configurar Alertas de Billing

```bash
# Via console: https://console.cloud.google.com/billing
# Configure alertas para não passar do orçamento
```

## 🐛 Troubleshooting

### Erro: "Permission denied"

```bash
# Verificar permissões
gcloud projects get-iam-policy $PROJECT_ID

# Dar permissões necessárias
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:seu-email@gmail.com" \
    --role="roles/owner"
```

### Erro: "Cannot connect to database"

1. Verificar se Cloud SQL está rodando
2. Verificar connection name no Cloud Run
3. Verificar se a senha está correta
4. Verificar firewall do Cloud SQL (permitir conexões do Cloud Run)

### Erro: "Image not found"

```bash
# Verificar se a imagem foi enviada
gcloud container images list

# Re-fazer push se necessário
gcloud builds submit --tag gcr.io/$PROJECT_ID/hospicast-backend:latest ./backend
```

### Erro: "Out of memory"

Aumentar memória:

```bash
gcloud run services update hospicast-backend \
    --memory 4Gi \
    --region southamerica-east1
```

## 📋 Checklist Final

- [ ] Google Cloud SDK instalado
- [ ] Projeto criado e billing habilitado
- [ ] APIs habilitadas
- [ ] Cloud SQL criado e configurado
- [ ] Schema do banco executado
- [ ] Imagem Docker buildada e enviada
- [ ] Cloud Run deployado com sucesso
- [ ] URL da API funcionando
- [ ] Frontend configurado com nova URL
- [ ] Testes realizados
- [ ] Logs verificados
- [ ] Monitoramento configurado

## 🔗 Links Úteis

- **Console Cloud Run**: https://console.cloud.google.com/run
- **Console Cloud SQL**: https://console.cloud.google.com/sql
- **Cloud Build**: https://console.cloud.google.com/cloud-build
- **Documentação Cloud Run**: https://cloud.google.com/run/docs
- **Documentação Cloud SQL**: https://cloud.google.com/sql/docs/postgres

## 📞 Próximos Passos

1. ✅ Configurar domínio customizado (opcional)
2. ✅ Configurar SSL/HTTPS (já vem por padrão)
3. ✅ Configurar backups automáticos do banco
4. ✅ Configurar monitoramento e alertas
5. ✅ Otimizar custos conforme uso

---

**Dúvidas?** Consulte a documentação oficial ou abra uma issue no repositório.

**Última atualização**: Janeiro 2025

