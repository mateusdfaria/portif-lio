"""Script para instalar CmdStan se necessário."""
import sys

try:
    import cmdstanpy
    
    # Verificar se CmdStan já está instalado
    try:
        cmdstanpy.install_cmdstan(version=None, verbose=True)
        print("✅ CmdStan instalado/verificado com sucesso")
    except Exception as e:
        print(f"⚠️  Aviso ao instalar CmdStan: {e}")
        print("   Tentando continuar mesmo assim...")
        
except ImportError:
    print("⚠️  cmdstanpy não está instalado. Instale com: pip install cmdstanpy")
    sys.exit(1)

