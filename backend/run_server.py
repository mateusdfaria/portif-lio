#!/usr/bin/env python3
"""
Script simples para rodar o servidor HospiCast
"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("🏥 HospiCast Backend")
    print("🚀 Iniciando servidor...")
    print("📍 URL: http://127.0.0.1:8001")
    print("📚 Docs: http://127.0.0.1:8001/docs")
    print("-" * 40)
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8001, 
        log_level="info"
    )
