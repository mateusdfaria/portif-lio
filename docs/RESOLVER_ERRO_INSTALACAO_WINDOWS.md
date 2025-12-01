# 🔧 Resolver Erro de Instalação no Windows

## ❌ Problemas Identificados

1. **Python 3.14.0** - Versão muito nova, pode ter problemas de compatibilidade
2. **Falta compilador C** - numpy precisa compilar, mas não há Visual Studio Build Tools
3. **Dependências não instaladas** - Por isso o erro "ModuleNotFoundError: No module named 'pydantic'"

## ✅ Solução 1: Instalar Visual Studio Build Tools (Recomendado)

### Opção A: Instalar Build Tools

1. Baixe: https://visualstudio.microsoft.com/downloads/
2. Instale "Build Tools for Visual Studio"
3. Durante instalação, marque "Desktop development with C++"
4. Depois tente novamente:
   ```bash
   pip install -r requirements.txt
   ```

### Opção B: Usar Wheels Pré-compilados (Mais Rápido)

```bash
# Atualizar pip primeiro
python -m pip install --upgrade pip

# Instalar numpy com wheel pré-compilado
pip install numpy --only-binary :all:

# Depois instalar o resto
pip install -r requirements.txt
```

## ✅ Solução 2: Instalar Apenas Dependências Essenciais (Para Testar Banco)

Para testar a conexão com o banco, você só precisa de `psycopg2-binary`:

```bash
# Instalar apenas o necessário para conectar ao banco
pip install psycopg2-binary

# Agora tente executar o script
python scripts/init_database.py
```

## ✅ Solução 3: Usar Python 3.11 ou 3.12 (Recomendado)

Python 3.14 é muito novo. Use uma versão mais estável:

1. **Desinstalar Python 3.14** (opcional)
2. **Instalar Python 3.11 ou 3.12:**
   - https://www.python.org/downloads/
   - Baixe Python 3.11.9 ou 3.12.7
   - Marque "Add Python to PATH"

3. **Depois de instalar:**
   ```bash
   # Verificar versão
   python --version
   # Deve mostrar: Python 3.11.x ou 3.12.x
   
   # Instalar dependências
   cd backend
   pip install -r requirements.txt
   ```

## 🚀 Solução Rápida: Instalar Só o Essencial

Se você só quer testar a conexão com o banco AGORA:

```bash
# 1. Instalar apenas psycopg2-binary
pip install psycopg2-binary

# 2. Verificar DATABASE_URL
echo $DATABASE_URL

# Se não estiver configurada:
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA@34.39.151.125:5432/hospicast"

# 3. Executar script
cd backend
python scripts/init_database.py
```

## 📋 Comandos Completos (Solução Rápida)

```bash
# 1. Atualizar pip
python -m pip install --upgrade pip

# 2. Instalar apenas o necessário para o banco
pip install psycopg2-binary

# 3. Verificar DATABASE_URL
echo $DATABASE_URL

# 4. Se não estiver configurada, configure:
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA@34.39.151.125:5432/hospicast"

# 5. Testar conexão
cd backend
python scripts/init_database.py
```

## 💡 Dica: Usar Ambiente Virtual

```bash
# Criar ambiente virtual
cd backend
python -m venv venv

# Ativar (Git Bash)
source venv/Scripts/activate

# Instalar dependências
pip install psycopg2-binary

# Executar script
python scripts/init_database.py
```

## 🐛 Se Ainda Der Erro

### Erro: "ModuleNotFoundError: No module named 'core'"

**Solução:** Certifique-se de estar no diretório correto:

```bash
# Ver onde você está
pwd

# Deve estar em: .../portif-lio/backend
# Se não estiver:
cd backend
```

### Erro: "could not connect to server"

**Solução:** Autorize o IP no Cloud SQL (se estiver usando Cloud Shell) ou configure firewall.

---

**Tente a Solução Rápida primeiro (instalar só psycopg2-binary) para testar o banco!**

