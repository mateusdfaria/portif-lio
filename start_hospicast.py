#!/usr/bin/env python3
"""
Script principal para iniciar o HospiCast
Inicia backend e frontend em processos separados
"""
import subprocess
import sys
import time
import os
from pathlib import Path
import threading

def start_backend():
    """Inicia o backend"""
    print("🔧 Iniciando Backend...")
    try:
        subprocess.run([sys.executable, "start_backend.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Backend interrompido.")
    except Exception as e:
        print(f"❌ Erro no backend: {e}")

def start_frontend():
    """Inicia o frontend"""
    print("🎨 Iniciando Frontend...")
    try:
        subprocess.run([sys.executable, "start_frontend.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend interrompido.")
    except Exception as e:
        print(f"❌ Erro no frontend: {e}")

def main():
    print("🏥 HospiCast - Sistema de Previsão Hospitalar")
    print("=" * 50)
    print("🚀 Iniciando serviços...")
    print()
    
    # Verificar se os arquivos existem
    if not Path("start_backend.py").exists():
        print("❌ Arquivo start_backend.py não encontrado!")
        return
    
    if not Path("start_frontend.py").exists():
        print("❌ Arquivo start_frontend.py não encontrado!")
        return
    
    print("📋 Instruções:")
    print("1. O backend será iniciado em http://127.0.0.1:8000")
    print("2. O frontend será iniciado em http://localhost:3000")
    print("3. Pressione Ctrl+C para parar ambos os serviços")
    print()
    
    try:
        # Iniciar backend em thread separada
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Aguardar um pouco para o backend inicializar
        time.sleep(3)
        
        # Iniciar frontend
        start_frontend()
        
    except KeyboardInterrupt:
        print("\n👋 HospiCast interrompido pelo usuário.")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()

