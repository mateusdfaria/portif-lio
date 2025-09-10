#!/usr/bin/env python3
"""
Script para iniciar o backend HospiCast
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Mudar para o diretório backend
os.chdir(backend_dir)

if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print("🚀 Iniciando HospiCast Backend...")
    print("📍 Diretório:", backend_dir)
    print("🌐 URL: http://127.0.0.1:8000")
    print("📚 Docs: http://127.0.0.1:8000/docs")
    print("-" * 50)
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        log_level="info",
        reload=False  # Desabilitar reload para evitar problemas
    )

