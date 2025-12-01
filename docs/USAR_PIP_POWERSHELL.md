# 🔧 Usar pip no PowerShell

## ❌ Erro: "pip não é reconhecido"

No PowerShell do Windows, às vezes precisa usar `python -m pip` ao invés de apenas `pip`.

## ✅ Solução

### Opção 1: Usar `python -m pip` (Recomendado)

```powershell
# Instalar dependências
python -m pip install psycopg2-binary pydantic

# Ou instalar todas (pode dar erro por falta de compilador)
python -m pip install -r requirements.txt
```

### Opção 2: Verificar se pip está no PATH

```powershell
# Verificar se Python está instalado
python --version

# Verificar se pip está disponível
python -m pip --version

# Se funcionar, use sempre: python -m pip
```

## 🚀 Comandos Completos para Testar Banco

```powershell
# 1. Instalar apenas o necessário para conectar ao banco
python -m pip install psycopg2-binary pydantic

# 2. Verificar DATABASE_URL (no PowerShell use $env:)
$env:DATABASE_URL

# Se não estiver configurada, configure:
$env:DATABASE_URL = "postgresql://hospicast_user:SUA_SENHA@34.39.151.125:5432/hospicast"

# 3. Verificar
echo $env:DATABASE_URL

# 4. Executar script
python scripts/init_database.py
```

## 📋 Diferenças: PowerShell vs Bash

| Comando | Bash/Git Bash | PowerShell |
|---------|---------------|------------|
| Instalar pacote | `pip install` | `python -m pip install` |
| Variável de ambiente | `export VAR=valor` | `$env:VAR = "valor"` |
| Ver variável | `echo $VAR` | `echo $env:VAR` |

## ✅ Exemplo Completo no PowerShell

```powershell
# 1. Navegar para o backend (se ainda não estiver)
cd backend

# 2. Instalar dependências mínimas
python -m pip install psycopg2-binary pydantic

# 3. Configurar DATABASE_URL
$env:DATABASE_URL = "postgresql://hospicast_user:SUA_SENHA@34.39.151.125:5432/hospicast"

# 4. Verificar
echo $env:DATABASE_URL

# 5. Testar conexão
python scripts/init_database.py
```

## 🐛 Se Ainda Der Erro

### Erro: "python não é reconhecido"

**Solução:** Python não está no PATH. Reinstale Python marcando "Add Python to PATH".

### Erro: "ModuleNotFoundError"

**Solução:** Instale as dependências:
```powershell
python -m pip install psycopg2-binary pydantic
```

---

**Use `python -m pip` no PowerShell!**

