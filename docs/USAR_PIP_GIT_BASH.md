# 🔧 Usar pip no Git Bash

## ❌ Erro: "pip: command not found"

No Git Bash, às vezes precisa usar `python -m pip` ao invés de apenas `pip`.

## ✅ Solução

### Opção 1: Usar `python -m pip` (Recomendado)

```bash
# Instalar dependências
python -m pip install psycopg2-binary pydantic

# Ou instalar todas (pode dar erro por falta de compilador)
python -m pip install -r requirements.txt
```

### Opção 2: Verificar se pip está no PATH

```bash
# Verificar se Python está instalado
python --version

# Verificar se pip está disponível
python -m pip --version

# Se funcionar, use sempre: python -m pip
```

## 🚀 Comandos Completos para Testar Banco

```bash
# 1. Instalar apenas o necessário para conectar ao banco
python -m pip install psycopg2-binary pydantic

# 2. Verificar DATABASE_URL
echo $DATABASE_URL

# Se não estiver configurada, configure:
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA@34.39.151.125:5432/hospicast"

# 3. Verificar
echo $DATABASE_URL

# 4. Executar script
python scripts/init_database.py
```

## ✅ Exemplo Completo no Git Bash

```bash
# Você já está em: ~/Downloads/hospcast/portif-lio/backend

# 1. Instalar dependências mínimas
python -m pip install psycopg2-binary pydantic

# 2. Configurar DATABASE_URL (substitua SUA_SENHA pela senha real)
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA@34.39.151.125:5432/hospicast"

# 3. Verificar se funcionou
echo $DATABASE_URL

# 4. Testar conexão
python scripts/init_database.py
```

## 🐛 Se Ainda Der Erro

### Erro: "python: command not found"

**Solução:** Python não está no PATH. Verifique:

```bash
# Tentar python3
python3 --version

# Se funcionar, use python3 ao invés de python
python3 -m pip install psycopg2-binary pydantic
```

### Erro: "ModuleNotFoundError"

**Solução:** Instale as dependências:
```bash
python -m pip install psycopg2-binary pydantic
```

### Erro: "could not connect to server"

**Solução:** 
1. Verifique se o IP está correto
2. Verifique se a senha está correta
3. Se estiver usando Cloud SQL, autorize seu IP no firewall

---

**Use `python -m pip` no Git Bash!**

