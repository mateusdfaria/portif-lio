# 🗄️ Arquitetura de Banco de Dados - HospiCast

## 📋 Visão Geral

O HospiCast utiliza **SQLite** para persistência de dados, com arquitetura separada por funcionalidade.

## 🎯 Estrutura de Dados

### 1. **Banco de Hospitais Cadastrados** (`hospital_access.db`)

**Localização**: `backend/data/hospital_access.db`

**Propósito**: Gerenciar cadastro, autenticação e histórico de previsões dos hospitais.

#### Tabelas

##### `hospital_accounts`
Armazena informações de cadastro dos hospitais.

**Campos:**
- `hospital_id` (TEXT, PRIMARY KEY) - ID único do hospital
- `display_name` (TEXT) - Nome do hospital
- `cnes` (TEXT) - Código CNES (opcional)
- `city` (TEXT) - Cidade
- `state` (TEXT) - Estado
- `contact_email` (TEXT) - Email de contato
- `password_hash` (TEXT) - Hash da senha (bcrypt)
- `short_code` (TEXT, UNIQUE) - Código curto para login
- `created_at` (TEXT) - Data de criação

##### `hospital_sessions`
Armazena tokens de sessão dos hospitais autenticados.

**Campos:**
- `token` (TEXT, PRIMARY KEY) - Token de sessão (UUID)
- `hospital_id` (TEXT, FOREIGN KEY) - Referência ao hospital
- `expires_at` (TEXT) - Data de expiração do token
- `created_at` (TEXT) - Data de criação

##### `hospital_forecasts`
Armazena histórico de previsões geradas para cada hospital.

**Campos:**
- `forecast_id` (TEXT, PRIMARY KEY) - ID único da previsão
- `hospital_id` (TEXT, FOREIGN KEY) - Referência ao hospital
- `series_id` (TEXT) - ID da série temporal
- `horizon` (INTEGER) - Horizonte da previsão (dias)
- `payload` (TEXT) - JSON com dados completos da previsão
- `average_yhat` (REAL) - Média dos valores previstos
- `created_at` (TEXT) - Data de criação

## 🔄 Fluxo de Dados

### Cadastro de Hospital

```
1. Usuário preenche formulário de cadastro
2. Sistema gera hospital_id e short_code
3. Senha é hasheada com bcrypt
4. Dados são salvos em hospital_accounts
5. Retorna hospital_id, short_code e created_at
```

### Autenticação

```
1. Usuário informa hospital_id/short_code + senha
2. Sistema busca hospital em hospital_accounts
3. Compara hash da senha com bcrypt
4. Se válido, gera token UUID
5. Salva sessão em hospital_sessions
6. Retorna token e dados do hospital
```

### Geração de Previsão

```
1. Hospital autenticado gera previsão
2. Sistema salva previsão em hospital_forecasts
3. Payload completo é armazenado como JSON
4. Previsão fica disponível no histórico
```

### Consulta de Histórico

```
1. Hospital autenticado solicita histórico
2. Sistema busca em hospital_forecasts por hospital_id
3. Retorna últimas N previsões ordenadas por data
4. Cada previsão inclui dados completos do payload
```

## 🚫 O que NÃO é salvo no banco

### Dados de Monitoramento SUS

**Motivo**: Dados são buscados diretamente da API em tempo real.

**Comportamento:**
- Tela de monitoramento SUS busca dados da API do Datasus
- Se API não disponível, gera dados realistas dinamicamente
- **Nenhum dado é persistido** - sempre busca em tempo real

**Vantagens:**
- Dados sempre atualizados
- Não ocupa espaço no banco
- Não precisa sincronizar dados externos

## 📊 Resumo

| Funcionalidade | Banco de Dados | Persistência |
|---------------|----------------|--------------|
| Cadastro de Hospitais | ✅ `hospital_access.db` | ✅ Sim |
| Autenticação (Tokens) | ✅ `hospital_access.db` | ✅ Sim |
| Histórico de Previsões | ✅ `hospital_access.db` | ✅ Sim |
| Dados SUS (Monitoramento) | ❌ Não usa banco | ❌ Não (busca da API) |

## 🔧 Manutenção

### Backup

```bash
# Backup do banco de hospitais
cp backend/data/hospital_access.db backend/data/hospital_access.db.backup
```

### Limpeza de Sessões Expiradas

```python
from services.hospital_account_service import hospital_account_service

# Invalidar sessões expiradas (automático no validate_session)
# Ou manualmente:
hospital_account_service.invalidate_session(token)
```

### Limpeza de Previsões Antigas

```python
import sqlite3
from pathlib import Path

DB_PATH = Path("backend/data/hospital_access.db")
conn = sqlite3.connect(DB_PATH)

# Deletar previsões com mais de 1 ano
conn.execute("""
    DELETE FROM hospital_forecasts 
    WHERE created_at < datetime('now', '-1 year')
""")
conn.commit()
conn.close()
```

## 📝 Notas Importantes

1. **Senhas**: Nunca são armazenadas em texto plano, sempre como hash bcrypt
2. **Tokens**: Expiração automática após 12 horas
3. **Previsões**: Payload completo é salvo como JSON para reutilização
4. **Monitoramento SUS**: Dados sempre em tempo real, não persistidos
5. **Segurança**: Banco SQLite com validação de sessões e senhas hasheadas

---

*Última atualização: Janeiro 2025*

