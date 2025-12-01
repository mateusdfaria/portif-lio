# 🔧 Corrigir Erro do Pydantic

## ❌ Erro: "BaseSettings has been moved to pydantic-settings"

O Pydantic v2 foi instalado, mas `BaseSettings` foi movido para um pacote separado.

## ✅ Solução

### Opção 1: Instalar pydantic-settings (Recomendado)

```bash
# No Git Bash
python -m pip install pydantic-settings

# Depois tente novamente
python scripts/init_database.py
```

### Opção 2: Usar Pydantic v1 (Compatível com o código atual)

```bash
# Desinstalar Pydantic v2
python -m pip uninstall pydantic -y

# Instalar Pydantic v1
python -m pip install "pydantic>=1.10.15,<2.0.0"

# Depois tente novamente
python scripts/init_database.py
```

## ✅ Código Já Foi Corrigido

O arquivo `backend/core/config.py` já foi atualizado para funcionar com ambas as versões do Pydantic.

## 🚀 Comandos Completos

```bash
# 1. Instalar pydantic-settings
python -m pip install pydantic-settings

# 2. Verificar DATABASE_URL
echo $DATABASE_URL

# Se não estiver configurada:
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA@34.39.151.125:5432/hospicast"

# 3. Testar novamente
python scripts/init_database.py
```

## 📋 Alternativa: Instalar Pydantic v1

Se preferir usar Pydantic v1 (mais compatível):

```bash
# Desinstalar versão atual
python -m pip uninstall pydantic pydantic-settings -y

# Instalar Pydantic v1
python -m pip install "pydantic>=1.10.15,<2.0.0"

# Testar
python scripts/init_database.py
```

---

**Execute: `python -m pip install pydantic-settings` e tente novamente!**

