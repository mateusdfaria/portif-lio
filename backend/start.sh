#!/bin/bash
set -e

echo "🚀 Iniciando HospiCast Backend..."

# Navegar para o diretório backend
cd "$(dirname "$0")" || exit 1

# Verificar se Python está disponível
python --version

# Verificar se uvicorn está instalado
python -m pip list | grep uvicorn || pip install uvicorn[standard]

# Iniciar servidor
echo "📡 Iniciando servidor na porta ${PORT:-8000}..."
exec python -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"

