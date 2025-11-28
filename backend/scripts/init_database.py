"""Script para inicializar o banco de dados manualmente"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from core.database import get_database_type, is_postgresql
from services.hospital_account_service import _get_connection, _ensure_schema


def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    db_type = get_database_type()
    print(f"🗄️  Inicializando banco de dados ({db_type.upper()})...")
    
    try:
        conn = _get_connection()
        _ensure_schema(conn)
        
        # Verificar se as tabelas foram criadas
        cursor = conn.cursor()
        
        if is_postgresql():
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            tables = [row['table_name'] for row in cursor.fetchall()]
            
            # Verificar índices
            cursor.execute("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE schemaname = 'public' 
                AND indexname LIKE 'idx_%'
                ORDER BY indexname
            """)
            indexes = [row['indexname'] for row in cursor.fetchall()]
        else:
            # SQLite
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]
            
            # Verificar índices
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
            )
            indexes = [row[0] for row in cursor.fetchall()]
        
        print(f"✅ Banco de dados inicializado com sucesso!")
        print(f"📊 Tabelas criadas: {', '.join(tables) if tables else 'Nenhuma'}")
        print(f"📇 Índices criados: {', '.join(indexes) if indexes else 'Nenhum'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

