FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY backend/requirements.txt /app/requirements.txt

# Instalar dependências
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código do backend
COPY backend/ /app/

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

