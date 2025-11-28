# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    make \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install CmdStan (required by Prophet)
# Nota: CmdStan é grande (~200MB) e pode demorar para instalar
# Instalar make primeiro (necessário para build do CmdStan)
RUN apt-get update && apt-get install -y make && rm -rf /var/lib/apt/lists/*
ENV CMDSTAN_NO_UPDATE_CHECK=1
RUN python -c "import cmdstanpy; import os; os.environ['CMDSTAN_NO_UPDATE_CHECK']='1'; cmdstanpy.install_cmdstan(version=None, verbose=False, overwrite=False)" || echo "CmdStan installation attempt completed"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p models data logs

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Health check (removido - Cloud Run faz health check automaticamente)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
#     CMD curl -f http://localhost:${PORT}/ || exit 1

# Run the application
# Cloud Run fornece PORT via variável de ambiente
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1
