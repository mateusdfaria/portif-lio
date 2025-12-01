# 🗄️ Setup do Banco de Dados - HospiCast

## ✅ Banco de Dados Implementado

O banco de dados **SQLite** está configurado e funcionando automaticamente!

### 📍 Localização
- **Arquivo**: `backend/data/hospital_access.db`
- **Criação**: Automática na primeira execução

## 🏗️ Estrutura do Banco

### Tabelas Criadas Automaticamente

#### 1. `hospital_accounts`
Armazena cadastro de hospitais.

**Campos:**
- `hospital_id` (PRIMARY KEY) - ID único do hospital
- `display_name` - Nome do hospital
- `cnes` - Código CNES (opcional)
- `city` - Cidade
- `state` - Estado
- `contact_email` - Email de contato
- `password_hash` - Hash da senha (bcrypt)
- `short_code` - Código curto para login (único)
- `created_at` - Data de criação

#### 2. `hospital_sessions`
Armazena tokens de autenticação.

**Campos:**
- `token` (PRIMARY KEY) - Token de sessão (UUID)
- `hospital_id` - Referência ao hospital
- `expires_at` - Data de expiração (12 horas)
- `created_at` - Data de criação

#### 3. `hospital_forecasts`
Armazena histórico de previsões.

**Campos:**
- `forecast_id` (PRIMARY KEY) - ID único da previsão
- `hospital_id` - Referência ao hospital
- `series_id` - ID da série temporal
- `horizon` - Horizonte da previsão (dias)
- `payload` - JSON completo da previsão
- `average_yhat` - Média dos valores previstos
- `created_at` - Data de criação

### Índices Criados Automaticamente

Para melhor performance:
- `idx_sessions_hospital_id` - Busca rápida de sessões por hospital
- `idx_sessions_token` - Validação rápida de tokens
- `idx_forecasts_hospital_id` - Busca rápida de previsões por hospital
- `idx_forecasts_created_at` - Ordenação rápida por data
- `idx_forecasts_hospital_created` - Busca combinada (hospital + data)

## 🚀 Como Funciona

### Criação Automática

O banco é criado **automaticamente** quando:
1. Um hospital se cadastra pela primeira vez
2. Um hospital faz login
3. Uma previsão é salva
4. O servidor inicia (verifica e cria se necessário)

**Não é necessário fazer nada manualmente!**

### Fluxo de Dados

#### Cadastro de Hospital
```
POST /hospital-access/register
→ Salva em hospital_accounts
→ Retorna hospital_id, short_code, created_at
```

#### Login
```
POST /hospital-access/login
→ Valida senha em hospital_accounts
→ Cria token em hospital_sessions
→ Retorna token e dados do hospital
```

#### Gerar Previsão (com salvamento)
```
POST /forecast/predict
Body: {
  "hospital_id": "...",
  "session_token": "...",
  "series_id": "...",
  "horizon": 14
}
→ Valida sessão
→ Gera previsão
→ Salva em hospital_forecasts
→ Retorna previsão
```

#### Consultar Histórico
```
GET /hospital-access/{hospital_id}/forecasts
Header: X-Hospital-Token: ...
→ Busca em hospital_forecasts
→ Retorna últimas 20 previsões
```

## 🔧 Script de Inicialização Manual

Se precisar inicializar o banco manualmente:

```bash
# No diretório do backend
python backend/scripts/init_database.py
```

Isso criará todas as tabelas e índices.

## 🌐 Funcionamento em Produção

### Netlify (Frontend)
- ✅ Frontend está no Netlify
- ✅ Faz chamadas para a API do backend

### Backend (Produção)
O backend precisa estar hospedado em:
- **Railway** (recomendado)
- **Render**
- **Heroku**
- **AWS/Google Cloud**
- **VPS próprio**

### Banco de Dados em Produção

**SQLite funciona perfeitamente em produção se:**
1. ✅ O diretório `backend/data/` tem permissão de escrita
2. ✅ O servidor mantém o arquivo entre reinicializações
3. ✅ Há apenas uma instância do servidor (ou usa banco compartilhado)

**Para múltiplas instâncias, considere:**
- PostgreSQL (Railway, Render oferecem)
- MySQL/MariaDB
- SQLite com volume compartilhado

## 📊 Verificar Banco de Dados

### Via Python
```python
from services.hospital_account_service import _get_connection

conn = _get_connection()
cursor = conn.execute("SELECT COUNT(*) FROM hospital_accounts")
count = cursor.fetchone()[0]
print(f"Total de hospitais cadastrados: {count}")
conn.close()
```

### Via SQLite CLI
```bash
sqlite3 backend/data/hospital_access.db

# Comandos úteis:
.tables
.schema hospital_accounts
SELECT COUNT(*) FROM hospital_accounts;
SELECT * FROM hospital_accounts LIMIT 5;
```

## 🔒 Segurança

- ✅ Senhas são hasheadas com **bcrypt** (nunca em texto plano)
- ✅ Tokens expiram após **12 horas**
- ✅ Validação de sessão em todas as operações sensíveis
- ✅ Foreign keys habilitadas para integridade

## 🐛 Troubleshooting

### Banco não está sendo criado
```bash
# Verificar permissões
ls -la backend/data/

# Criar diretório manualmente
mkdir -p backend/data
chmod 755 backend/data
```

### Erro de permissão
```bash
# Dar permissão de escrita
chmod 755 backend/data
chmod 644 backend/data/hospital_access.db
```

### Banco corrompido
```bash
# Fazer backup
cp backend/data/hospital_access.db backend/data/hospital_access.db.backup

# Recriar (vai perder dados)
rm backend/data/hospital_access.db
# Reiniciar servidor (banco será recriado)
```

## ✅ Checklist de Verificação

- [x] Banco criado automaticamente
- [x] Tabelas criadas com schema correto
- [x] Índices criados para performance
- [x] Foreign keys habilitadas
- [x] Senhas hasheadas com bcrypt
- [x] Tokens com expiração
- [x] Previsões sendo salvas automaticamente
- [x] Histórico consultável por hospital

## 📝 Notas Importantes

1. **Backup**: Faça backup regular do arquivo `hospital_access.db`
2. **Produção**: Em produção, considere usar PostgreSQL para múltiplas instâncias
3. **Limpeza**: Sessões expiradas são removidas automaticamente
4. **Performance**: Índices garantem consultas rápidas mesmo com muitos dados

---

*Última atualização: Janeiro 2025*

