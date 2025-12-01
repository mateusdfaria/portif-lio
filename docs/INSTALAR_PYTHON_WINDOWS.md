# 🐍 Instalar e Configurar Python no Windows

## ❌ Erro: "Python não foi encontrado"

No Windows, o comando pode ser `python` ao invés de `python3`.

## ✅ Solução Rápida

### Opção 1: Tentar com `python` (sem o 3)

```bash
# No Git Bash ou PowerShell
cd backend
python scripts/init_database.py
```

### Opção 2: Verificar se Python está Instalado

```bash
# Tentar python
python --version

# Tentar python3
python3 --version

# Tentar py (launcher do Windows)
py --version
```

## 🔧 Se Python Não Estiver Instalado

### Instalar Python no Windows

1. **Baixar Python:**
   - Acesse: https://www.python.org/downloads/
   - Baixe a versão mais recente (3.11 ou 3.12)
   - **IMPORTANTE:** Marque a opção "Add Python to PATH" durante a instalação

2. **Ou usar Chocolatey:**
   ```powershell
   # No PowerShell (como Administrador)
   choco install python
   ```

3. **Ou usar Microsoft Store:**
   - Abra Microsoft Store
   - Procure por "Python 3.11" ou "Python 3.12"
   - Instale

### Verificar Instalação

Depois de instalar, **feche e abra novamente** o terminal:

```bash
# Verificar versão
python --version

# Deve mostrar algo como: Python 3.11.5
```

## 🚀 Depois de Instalar Python

```bash
# 1. Verificar se está funcionando
python --version

# 2. Instalar dependências
cd backend
python -m pip install -r requirements.txt

# 3. Testar conexão
python scripts/init_database.py
```

## 💡 Dica: Criar Ambiente Virtual (Recomendado)

```bash
# Criar ambiente virtual
cd backend
python -m venv venv

# Ativar (Git Bash)
source venv/Scripts/activate

# Ativar (PowerShell)
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Executar script
python scripts/init_database.py
```

## 🐛 Problemas Comuns

### Erro: "python não é reconhecido como comando"

**Solução:** Python não está no PATH. Reinstale Python marcando "Add Python to PATH".

### Erro: "pip não é reconhecido"

**Solução:**
```bash
python -m pip install -r requirements.txt
```

### Erro: "ModuleNotFoundError: No module named 'psycopg2'"

**Solução:** Instale as dependências:
```bash
pip install -r requirements.txt
```

## ✅ Comandos Completos

```bash
# 1. Verificar Python
python --version

# 2. Configurar DATABASE_URL (se ainda não fez)
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA@34.39.151.125:5432/hospicast"

# 3. Instalar dependências
cd backend
python -m pip install -r requirements.txt

# 4. Testar conexão
python scripts/init_database.py
```

---

**Instale Python primeiro e depois tente novamente!**

