#!/bin/bash
set -e

echo "Iniciando HospiCast Backend..."

# Navegar para o diretório backend
cd "$(dirname "$0")" || exit 1

# Verificar se Python está disponível
python3 --version || python --version

# Verificar se uvicorn está instalado, se não, instalar
if ! python3 -m pip show uvicorn > /dev/null 2>&1; then
    echo "Instalando uvicorn..."
    python3 -m pip install uvicorn[standard]
fi

# Iniciar servidor
echo "Iniciando servidor na porta ${PORT:-8000}..."
exec python3 -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"

