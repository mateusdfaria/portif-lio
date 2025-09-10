#!/usr/bin/env python3
"""
Script para iniciar o frontend HospiCast
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print("❌ Diretório frontend não encontrado!")
        return
    
    print("🚀 Iniciando HospiCast Frontend...")
    print("📍 Diretório:", frontend_dir)
    print("🌐 URL: http://localhost:3000")
    print("-" * 50)
    
    try:
        # Mudar para o diretório frontend
        os.chdir(frontend_dir)
        
        # Verificar se node_modules existe
        if not (frontend_dir / "node_modules").exists():
            print("📦 Instalando dependências do frontend...")
            subprocess.run([sys.executable, "-m", "npm", "install"], check=True)
        
        # Iniciar o servidor de desenvolvimento
        print("🌐 Iniciando servidor de desenvolvimento...")
        subprocess.run([sys.executable, "-m", "npm", "run", "dev"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar frontend: {e}")
    except FileNotFoundError:
        print("❌ npm não encontrado. Instale Node.js primeiro.")
    except KeyboardInterrupt:
        print("\n👋 Frontend interrompido pelo usuário.")

if __name__ == "__main__":
    main()

