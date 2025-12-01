# HospiCast - Guia de Deploy

Este guia explica como fazer o deploy do HospiCast em produção usando Docker e Docker Compose.

## 📋 Pré-requisitos

- Docker (versão 20.10+)
- Docker Compose (versão 2.0+)
- Git
- Pelo menos 4GB de RAM disponível
- Pelo menos 20GB de espaço em disco

## 🚀 Deploy Rápido

### 1. Clone o repositório
```bash
git clone <repository-url>
cd hospi-cast-prophet-starter
```

### 2. Configure as variáveis de ambiente
```bash
cp config.example.env .env
# Edite o arquivo .env com suas configurações
```

### 3. Execute o deploy
```bash
./deploy.sh deploy
```

## 🔧 Configuração Detalhada

### Variáveis de Ambiente (.env)

Principais variáveis que devem ser configuradas:

```bash
# Banco de dados
POSTGRES_PASSWORD=sua_senha_segura_aqui
REDIS_PASSWORD=sua_senha_redis_aqui

# URLs da aplicação
VITE_API_BASE_URL=https://api.seudominio.com

# Chaves de API externas
OPENWEATHER_API_KEY=sua_chave_openweather_aqui

# Segurança
SECRET_KEY=sua_chave_secreta_aqui
JWT_SECRET=sua_chave_jwt_aqui
```

### Estrutura de Diretórios

```
hospi-cast-prophet-starter/
├── backend/                 # API FastAPI
├── frontend/               # Aplicação React
├── database/               # Scripts de banco
│   ├── init.sql           # Inicialização do banco
│   └── backup/            # Backups automáticos
├── nginx/                 # Configuração do proxy
│   ├── nginx.conf         # Configuração principal
│   ├── logs/              # Logs do nginx
│   └── ssl/               # Certificados SSL
├── docker-compose.yml     # Orquestração de serviços
├── docker-compose.prod.yml # Configuração de produção
└── deploy.sh              # Script de deploy
```

## 🐳 Serviços Incluídos

### 1. PostgreSQL (Banco de Dados)
- **Porta**: 5432
- **Banco**: hospicast
- **Usuário**: hospicast_user
- **Backup automático**: Diário às 2h

### 2. Redis (Cache)
- **Porta**: 6379
- **Uso**: Cache de sessões e dados temporários

### 3. Backend API (FastAPI)
- **Porta**: 8000
- **Documentação**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/

### 4. Frontend (React + Nginx)
- **Porta**: 3000
- **Build otimizado** para produção

### 5. Nginx (Proxy Reverso)
- **Porta**: 80 (HTTP)
- **Porta**: 443 (HTTPS - configurar SSL)
- **Rate limiting** configurado
- **Compressão gzip** habilitada

## 📊 Monitoramento

### Health Checks
Todos os serviços incluem health checks automáticos:

```bash
# Verificar status dos serviços
docker-compose ps

# Verificar logs
docker-compose logs -f

# Verificar saúde específica
curl http://localhost:8000/  # Backend
curl http://localhost:3000/   # Frontend
```

### Logs
```bash
# Logs de todos os serviços
./deploy.sh logs

# Logs específicos
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

## 🔄 Comandos de Deploy

### Deploy Completo
```bash
./deploy.sh deploy
```

### Gerenciamento de Serviços
```bash
./deploy.sh start      # Iniciar serviços
./deploy.sh stop       # Parar serviços
./deploy.sh restart    # Reiniciar serviços
./deploy.sh status     # Ver status
```

### Backup e Restore
```bash
# Backup do banco
./deploy.sh backup

# Restore do banco
./deploy.sh restore database/backup/hospicast_20240101_120000.sql
```

### Limpeza
```bash
./deploy.sh cleanup    # Para serviços e remove volumes
```

## 🔒 Configuração de SSL (HTTPS)

### 1. Obter certificados SSL
```bash
# Usando Let's Encrypt (recomendado)
certbot certonly --standalone -d seudominio.com

# Ou usar certificados próprios
```

### 2. Copiar certificados
```bash
cp /etc/letsencrypt/live/seudominio.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/seudominio.com/privkey.pem nginx/ssl/key.pem
```

### 3. Atualizar configuração
Descomente a seção HTTPS no arquivo `nginx/nginx.conf`

### 4. Reiniciar serviços
```bash
./deploy.sh restart
```

## 📈 Escalabilidade

### Horizontal Scaling
Para escalar horizontalmente:

```bash
# Escalar backend
docker-compose up -d --scale backend=3

# Escalar frontend
docker-compose up -d --scale frontend=2
```

### Load Balancer
Configure um load balancer externo (ex: AWS ALB, Cloudflare) apontando para:
- Frontend: porta 3000
- Backend: porta 8000

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Porta já em uso
```bash
# Verificar portas em uso
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# Parar serviços conflitantes
sudo systemctl stop apache2  # exemplo
```

#### 2. Erro de permissão
```bash
# Dar permissões corretas
sudo chown -R $USER:$USER .
chmod +x deploy.sh
```

#### 3. Banco não conecta
```bash
# Verificar logs do banco
docker-compose logs postgres

# Testar conexão manual
docker-compose exec postgres psql -U hospicast_user -d hospicast
```

#### 4. Memória insuficiente
```bash
# Verificar uso de memória
docker stats

# Ajustar limites no docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### Logs de Debug
```bash
# Ativar logs detalhados
export LOG_LEVEL=DEBUG
./deploy.sh restart

# Ver logs em tempo real
docker-compose logs -f --tail=100
```

## 🔄 Atualizações

### Atualizar Aplicação
```bash
# 1. Fazer backup
./deploy.sh backup

# 2. Atualizar código
git pull origin main

# 3. Rebuild e restart
./deploy.sh deploy
```

### Atualizar Dependências
```bash
# Backend
cd backend
pip-compile requirements.in
pip-sync requirements.txt

# Frontend
cd frontend
npm update
npm audit fix

# Rebuild
./deploy.sh deploy
```

## 📞 Suporte

Para problemas ou dúvidas:

1. Verifique os logs: `./deploy.sh logs`
2. Consulte a documentação da API: http://localhost:8000/docs
3. Verifique o status: `./deploy.sh status`

## 🎯 Próximos Passos

Após o deploy bem-sucedido:

1. ✅ Configure SSL/HTTPS
2. ✅ Configure monitoramento (ex: Prometheus + Grafana)
3. ✅ Configure alertas (ex: Slack, email)
4. ✅ Configure backup automático
5. ✅ Configure CI/CD pipeline
6. ✅ Configure CDN para assets estáticos
