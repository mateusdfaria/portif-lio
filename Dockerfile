FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema (para compilar algumas bibliotecas se necessário)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY backend/requirements.txt /app/requirements.txt

# Instalar dependências Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código do backend
COPY backend/ /app/

# Criar diretório de dados
RUN mkdir -p /app/data

# Expor porta
EXPOSE 8000

# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando para iniciar
# Railway define $PORT automaticamente, usar variável de ambiente
ENV PORT=8000
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}"]

