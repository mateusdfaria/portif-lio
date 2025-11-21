#!/bin/bash
set -e

echo "Iniciando HospiCast Backend..."

# Navegar para o diretório backend
cd "$(dirname "$0")" || exit 1

# Verificar se Python está disponível
PYTHON_CMD=$(which python3 || which python)
echo "Usando Python: $PYTHON_CMD"
$PYTHON_CMD --version

# Verificar se as dependências estão instaladas
if ! $PYTHON_CMD -m pip show pydantic > /dev/null 2>&1; then
    echo "Instalando dependências..."
    $PYTHON_CMD -m pip install --upgrade pip setuptools wheel
    $PYTHON_CMD -m pip install -r requirements.txt
fi

# Verificar se uvicorn está instalado
if ! $PYTHON_CMD -m pip show uvicorn > /dev/null 2>&1; then
    echo "Instalando uvicorn..."
    $PYTHON_CMD -m pip install uvicorn[standard]
fi

# Iniciar servidor
echo "Iniciando servidor na porta ${PORT:-8000}..."
exec $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"

