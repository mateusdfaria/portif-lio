# 🔐 Configuração de Variáveis de Ambiente

Este guia explica como configurar as variáveis de ambiente necessárias para o HospiCast, especialmente para resolver problemas de segurança relacionados a senhas hardcoded.

---

## ⚠️ Problema de Segurança Corrigido

**Antes**: Senhas estavam hardcoded no `docker-compose.yml`  
**Depois**: Senhas são lidas de variáveis de ambiente

---

## 📋 Variáveis Necessárias

### Para Desenvolvimento (docker-compose.yml)

Crie um arquivo `.env` na raiz do projeto com:

```bash
# PostgreSQL Database
POSTGRES_DB=hospicast
POSTGRES_USER=hospicast_user
POSTGRES_PASSWORD=SUA_SENHA_SEGURA_AQUI

# Backend
DATABASE_URL=postgresql://hospicast_user:SUA_SENHA_SEGURA_AQUI@postgres:5432/hospicast
LOG_LEVEL=INFO
ENVIRONMENT=development

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

### Para Produção (docker-compose.prod.yml)

```bash
# PostgreSQL Database
POSTGRES_DB=hospicast
POSTGRES_USER=hospicast_user
POSTGRES_PASSWORD=SUA_SENHA_FORTE_PRODUCAO

# Redis
REDIS_PASSWORD=SUA_SENHA_REDIS

# Backend
DATABASE_URL=postgresql://hospicast_user:SUA_SENHA_FORTE_PRODUCAO@postgres:5432/hospicast
LOG_LEVEL=INFO
ENVIRONMENT=production

# Frontend
VITE_API_BASE_URL=https://api.hospicast.com
```

---

## 🚀 Como Configurar

### 1. Criar arquivo `.env`

```bash
# Na raiz do projeto
cp .env.example .env  # Se existir
# ou
touch .env
```

### 2. Editar `.env`

```bash
# Use um editor de texto
nano .env
# ou
code .env
```

### 3. Definir senhas seguras

**⚠️ IMPORTANTE**: Use senhas fortes e únicas!

```bash
# Gerar senha segura (Linux/Mac)
openssl rand -base64 32

# Gerar senha segura (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

### 4. Verificar que `.env` está no `.gitignore`

O arquivo `.env` já está no `.gitignore`, então não será commitado.

---

## 🔍 Verificação

### Verificar se as variáveis estão sendo lidas

```bash
# Docker Compose
docker-compose config | grep POSTGRES_PASSWORD
# Não deve mostrar a senha real, apenas a referência ${POSTGRES_PASSWORD}
```

### Testar conexão

```bash
# Iniciar serviços
docker-compose up -d

# Verificar logs
docker-compose logs postgres

# Testar conexão
docker-compose exec backend python -c "from core.database import get_database_connection; conn = get_database_connection(); print('✅ Conexão OK')"
```

---

## 🛡️ Boas Práticas de Segurança

### ✅ FAZER

- ✅ Usar variáveis de ambiente para todas as senhas
- ✅ Usar senhas fortes e únicas
- ✅ Manter `.env` no `.gitignore`
- ✅ Usar diferentes senhas para desenvolvimento e produção
- ✅ Rotacionar senhas periodicamente
- ✅ Usar gerenciadores de segredos em produção (ex: Google Secret Manager)

### ❌ NÃO FAZER

- ❌ Commitar arquivos `.env` no Git
- ❌ Usar senhas fracas (ex: `123456`, `password`)
- ❌ Reutilizar senhas entre ambientes
- ❌ Hardcodar senhas no código
- ❌ Compartilhar senhas por email ou chat

---

## 📚 Referências

- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [12 Factor App - Config](https://12factor.net/config)
- [OWASP - Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_cryptographic_key)

---

**✅ Problema de segurança corrigido! Agora todas as senhas são lidas de variáveis de ambiente.**

