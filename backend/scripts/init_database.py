"""Script para inicializar o banco de dados manualmente"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services.hospital_account_service import _get_connection, _ensure_schema

def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    print("🔧 Inicializando banco de dados...")
    
    try:
        conn = _get_connection()
        _ensure_schema(conn)
        
        # Verificar se as tabelas foram criadas
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"✅ Banco de dados inicializado com sucesso!")
        print(f"📊 Tabelas criadas: {', '.join(tables)}")
        
        # Verificar índices
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
        )
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"📇 Índices criados: {', '.join(indexes) if indexes else 'Nenhum'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

