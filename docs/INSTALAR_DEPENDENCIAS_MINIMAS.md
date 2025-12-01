# 📦 Instalar Dependências Mínimas para Testar Banco

## ❌ Erro: "ModuleNotFoundError: No module named 'bcrypt'"

Faltam algumas dependências. Vamos instalar apenas o necessário para testar a conexão com o banco.

## ✅ Solução: Instalar Dependências Mínimas

```bash
# Instalar todas as dependências necessárias para o script
python -m pip install psycopg2-binary pydantic-settings bcrypt
```

## 🚀 Comandos Completos

```bash
# 1. Instalar dependências mínimas
python -m pip install psycopg2-binary pydantic-settings bcrypt

# 2. Verificar DATABASE_URL
echo $DATABASE_URL

# Se não estiver configurada:
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA@34.39.151.125:5432/hospicast"

# 3. Testar conexão
python scripts/init_database.py
```

## 📋 Lista de Dependências Mínimas

Para o script `init_database.py` funcionar, você precisa de:

- ✅ `psycopg2-binary` - Para conectar ao PostgreSQL
- ✅ `pydantic-settings` - Para configurações (Pydantic v2)
- ✅ `bcrypt` - Para hash de senhas

## 💡 Instalar Todas de Uma Vez

```bash
python -m pip install psycopg2-binary pydantic-settings bcrypt
```

## ✅ Depois de Instalar

```bash
# Verificar se DATABASE_URL está configurada
echo $DATABASE_URL

# Se não estiver, configure:
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA@34.39.151.125:5432/hospicast"

# Testar
python scripts/init_database.py
```

---

**Execute: `python -m pip install psycopg2-binary pydantic-settings bcrypt`**

