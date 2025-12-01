# 🔄 Guia de Migração para PostgreSQL

Este guia explica como migrar o HospiCast de SQLite para PostgreSQL e configurar para produção.

## 📋 Visão Geral

O HospiCast agora suporta **ambos** SQLite (desenvolvimento) e PostgreSQL (produção) automaticamente. O sistema detecta qual banco usar baseado nas variáveis de ambiente.

## 🔧 Configuração

### Desenvolvimento (SQLite - Padrão)

Não é necessário fazer nada! O sistema usa SQLite automaticamente se `DATABASE_URL` não estiver configurada.

```bash
# O banco será criado automaticamente em backend/data/hospital_access.db
python backend/scripts/init_database.py
```

### Produção (PostgreSQL)

Configure a variável de ambiente `DATABASE_URL`:

```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

Ou no arquivo `.env`:

```env
DATABASE_URL=postgresql://hospicast_user:senha@localhost:5432/hospicast
DATABASE_TYPE=postgresql
```

## 🚀 Migração de Dados

### Passo 1: Configurar PostgreSQL

Certifique-se de que o PostgreSQL está rodando e acessível.

### Passo 2: Criar Schema

Execute o schema SQL:

```bash
psql -h localhost -U hospicast_user -d hospicast -f database/init_hospital_access.sql
```

**OU** use o script Python (cria automaticamente):

```bash
export DATABASE_URL="postgresql://hospicast_user:senha@localhost:5432/hospicast"
cd backend
python scripts/init_database.py
```

### Passo 3: Migrar Dados do SQLite

Se você já tem dados no SQLite e quer migrar:

```bash
export DATABASE_URL="postgresql://hospicast_user:senha@localhost:5432/hospicast"
cd backend
python scripts/migrate_to_postgresql.py
```

O script irá:
- ✅ Conectar ao SQLite existente
- ✅ Conectar ao PostgreSQL
- ✅ Migrar hospitais cadastrados
- ✅ Migrar sessões ativas
- ✅ Migrar histórico de previsões

## 🧪 Testando

### Verificar Tipo de Banco

```python
from core.database import get_database_type, is_postgresql, is_sqlite

print(f"Tipo de banco: {get_database_type()}")
print(f"É PostgreSQL? {is_postgresql()}")
print(f"É SQLite? {is_sqlite()}")
```

### Testar Conexão

```python
from core.database import get_database_connection

conn = get_database_connection()
cursor = conn.cursor()
cursor.execute("SELECT 1")
result = cursor.fetchone()
print(f"✅ Conexão OK: {result}")
conn.close()
```

## 📊 Estrutura de Tabelas

As tabelas são criadas automaticamente e são idênticas em ambos os bancos:

- `hospital_accounts` - Cadastro de hospitais
- `hospital_sessions` - Tokens de autenticação
- `hospital_forecasts` - Histórico de previsões

## 🔍 Diferenças SQLite vs PostgreSQL

| Recurso | SQLite | PostgreSQL |
|---------|--------|------------|
| Tipo de dados | TEXT | VARCHAR(255) |
| Timestamps | TEXT (ISO) | TIMESTAMP WITH TIME ZONE |
| Placeholders | `?` | `%s` ou `%(name)s` |
| ON CONFLICT | `INSERT OR REPLACE` | `ON CONFLICT ... DO UPDATE` |
| Índices | Suportado | Suportado |

O código trata essas diferenças automaticamente!

## 🐛 Troubleshooting

### Erro: "psycopg2-binary não está instalado"

```bash
pip install psycopg2-binary
```

### Erro: "Erro ao conectar ao PostgreSQL"

1. Verifique se o PostgreSQL está rodando
2. Verifique se a URL está correta
3. Verifique permissões de firewall
4. Para Google Cloud SQL, use o Cloud SQL Proxy

### Erro: "Tabelas não encontradas"

Execute o script de inicialização:

```bash
python backend/scripts/init_database.py
```

## 📝 Checklist de Migração

- [ ] PostgreSQL instalado e rodando
- [ ] Banco de dados criado
- [ ] Usuário criado com permissões
- [ ] `DATABASE_URL` configurada
- [ ] Schema executado (`init_database.py` ou SQL)
- [ ] Dados migrados (se aplicável)
- [ ] Testes realizados
- [ ] Backup do SQLite feito (se migrando)

## 🔗 Próximos Passos

Após migrar para PostgreSQL:

1. ✅ Configure para Google Cloud (veja `GOOGLE_CLOUD_DEPLOY.md`)
2. ✅ Configure backups automáticos
3. ✅ Configure monitoramento
4. ✅ Atualize variáveis de ambiente em produção

---

**Última atualização**: Janeiro 2025

