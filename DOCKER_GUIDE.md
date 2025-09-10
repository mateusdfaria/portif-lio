# 🐳 Guia de Uso do HospiCast com Docker

## 🚀 **Início Rápido**

### **1. Primeira Execução**
```bash
# Construir e iniciar todos os serviços
docker-compose up --build

# Ou usar o script de comandos
chmod +x docker-commands.sh
./docker-commands.sh start
```

### **2. Acessar a Aplicação**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs
- **Banco de Dados**: localhost:5432

## 🔧 **Comandos Essenciais**

### **Gerenciamento de Serviços**
```bash
# Iniciar todos os serviços
docker-compose up -d

# Parar todos os serviços
docker-compose down

# Reiniciar serviços
docker-compose restart

# Ver status dos serviços
docker-compose ps
```

### **Logs e Debugging**
```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### **Manutenção**
```bash
# Limpar containers e volumes
docker-compose down -v
docker system prune -f

# Reconstruir imagens
docker-compose build --no-cache

# Fazer backup do banco
docker-compose exec db pg_dump -U hospicast_user hospicast > backup.sql
```

## 🏗️ **Arquitetura dos Serviços**

### **Serviços Disponíveis**
- **`db`**: PostgreSQL (porta 5432)
- **`backend`**: FastAPI (porta 8000)
- **`frontend`**: React + Nginx (porta 3000)
- **`nginx`**: Proxy reverso (porta 80)

### **Volumes Persistentes**
- **`db_data`**: Dados do PostgreSQL
- **`./models`**: Modelos treinados do Prophet
- **`./backend`**: Código do backend (desenvolvimento)
- **`./frontend`**: Código do frontend (desenvolvimento)

## 🔐 **Configuração de Ambiente**

### **Arquivo de Configuração**
Crie um arquivo `.env` baseado no `config.example.env`:

```bash
# Copiar arquivo de exemplo
cp config.example.env .env

# Editar configurações
nano .env
```

### **Variáveis Importantes**
```env
# Banco de Dados
POSTGRES_DB=hospicast
POSTGRES_USER=hospicast_user
POSTGRES_PASSWORD=sua_senha_segura

# URLs da API
VITE_API_BASE_URL=http://localhost:8000

# Chaves de API (opcional)
OPENWEATHER_API_KEY=sua_chave_openweather
```

## 🚨 **Solução de Problemas**

### **Problemas Comuns**

#### **1. Porta já em uso**
```bash
# Verificar portas em uso
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# Parar serviços conflitantes
sudo systemctl stop apache2  # ou nginx
```

#### **2. Erro de permissão**
```bash
# Dar permissão ao script
chmod +x docker-commands.sh

# Verificar permissões do Docker
sudo usermod -aG docker $USER
```

#### **3. Problemas de rede**
```bash
# Limpar redes Docker
docker network prune

# Verificar conectividade
docker-compose exec backend ping db
```

#### **4. Banco de dados não conecta**
```bash
# Verificar logs do banco
docker-compose logs db

# Testar conexão
docker-compose exec backend python -c "import psycopg2; print('OK')"
```

## 📊 **Monitoramento**

### **Verificar Status**
```bash
# Status dos containers
docker-compose ps

# Uso de recursos
docker stats

# Espaço em disco
docker system df
```

### **Logs Importantes**
```bash
# Logs do backend
docker-compose logs backend | grep ERROR

# Logs do frontend
docker-compose logs frontend | grep ERROR

# Logs do banco
docker-compose logs db | grep ERROR
```

## 🔄 **Desenvolvimento**

### **Modo Desenvolvimento**
```bash
# Iniciar com hot-reload
docker-compose up

# Rebuild após mudanças
docker-compose up --build
```

### **Acessar Containers**
```bash
# Shell do backend
docker-compose exec backend bash

# Shell do banco
docker-compose exec db psql -U hospicast_user -d hospicast

# Shell do frontend
docker-compose exec frontend sh
```

## 🚀 **Deploy em Produção**

### **Configuração de Produção**
```bash
# Usar configuração de produção
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Ou usar script de deploy
./deploy.sh deploy
```

### **Variáveis de Produção**
```env
# config.prod.env
ENVIRONMENT=production
LOG_LEVEL=WARNING
POSTGRES_PASSWORD=senha_super_segura
SECRET_KEY=chave_secreta_producao
```

## 📝 **Próximos Passos**

1. **Configure o arquivo `.env`** com suas credenciais
2. **Execute `docker-compose up --build`** para iniciar
3. **Acesse http://localhost:3000** para usar o sistema
4. **Consulte http://localhost:8000/docs** para a API
5. **Use `./docker-commands.sh help`** para comandos úteis

## 🆘 **Suporte**

Se encontrar problemas:
1. Verifique os logs: `docker-compose logs`
2. Consulte este guia
3. Verifique o arquivo `DEPLOY.md` para detalhes técnicos
4. Use `./docker-commands.sh help` para comandos disponíveis
