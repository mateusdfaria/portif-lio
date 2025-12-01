# 🐍 Usar Python no Git Bash

## ❌ Erro: Caminho do Windows não funciona no Git Bash

No Git Bash, não use caminhos do Windows como `C:\Users\...`. Use apenas `python` ou `python3`.

## ✅ Solução

### Use apenas `python` ou `python3`

```bash
# Correto
python -m pip install psycopg2-binary pydantic-settings bcrypt

# Ou se python não funcionar
python3 -m pip install psycopg2-binary pydantic-settings bcrypt
```

## 🚀 Comandos Completos

```bash
# 1. Verificar qual comando funciona
python --version
# OU
python3 --version

# 2. Instalar dependências (use o que funcionou acima)
python -m pip install psycopg2-binary pydantic-settings bcrypt

# 3. Verificar DATABASE_URL
echo $DATABASE_URL

# Se não estiver configurada:
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA@34.39.151.125:5432/hospicast"

# 4. Testar conexão
python scripts/init_database.py
```

## 💡 Dica: Atualizar pip

Se quiser atualizar o pip primeiro:

```bash
# Use python (sem caminho completo)
python -m pip install --upgrade pip

# Depois instale as dependências
python -m pip install psycopg2-binary pydantic-settings bcrypt
```

## 📋 Resumo

- ❌ **Errado:** `C:\Users\Caio\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pip`
- ✅ **Correto:** `python -m pip` ou `python3 -m pip`

---

**Use apenas `python` no Git Bash!**

