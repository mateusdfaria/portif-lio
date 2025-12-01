"""Script para migrar dados do SQLite para PostgreSQL."""

import json
import sqlite3
import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("❌ psycopg2-binary não está instalado.")
    print("   Instale com: pip install psycopg2-binary")
    sys.exit(1)


def get_sqlite_connection():
    """Conecta ao banco SQLite."""
    DATA_DIR = Path(__file__).resolve().parents[2] / "data"
    DB_PATH = DATA_DIR / "hospital_access.db"
    
    if not DB_PATH.exists():
        print(f"❌ Banco SQLite não encontrado em: {DB_PATH}")
        sys.exit(1)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def get_postgresql_connection(database_url: str):
    """Conecta ao banco PostgreSQL."""
    try:
        conn = psycopg2.connect(database_url)
        conn.cursor_factory = RealDictCursor
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        sys.exit(1)


def migrate_hospital_accounts(sqlite_conn, pg_conn):
    """Migra tabela hospital_accounts."""
    print("📦 Migrando hospital_accounts...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Buscar todos os hospitais do SQLite
    sqlite_cursor.execute("SELECT * FROM hospital_accounts")
    hospitals = sqlite_cursor.fetchall()
    
    if not hospitals:
        print("   ℹ️  Nenhum hospital encontrado no SQLite")
        return
    
    migrated = 0
    for hospital in hospitals:
        try:
            pg_cursor.execute(
                """
                INSERT INTO hospital_accounts (
                    hospital_id, display_name, cnes, city, state,
                    contact_email, password_hash, short_code, created_at
                ) VALUES (
                    %(hospital_id)s, %(display_name)s, %(cnes)s, %(city)s, %(state)s,
                    %(contact_email)s, %(password_hash)s, %(short_code)s, %(created_at)s
                )
                ON CONFLICT (hospital_id) DO NOTHING
                """,
                dict(hospital),
            )
            migrated += 1
        except Exception as e:
            print(f"   ⚠️  Erro ao migrar hospital {hospital['hospital_id']}: {e}")
    
    pg_conn.commit()
    print(f"   ✅ {migrated} hospitais migrados")


def migrate_hospital_sessions(sqlite_conn, pg_conn):
    """Migra tabela hospital_sessions."""
    print("📦 Migrando hospital_sessions...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Buscar todas as sessões do SQLite
    sqlite_cursor.execute("SELECT * FROM hospital_sessions")
    sessions = sqlite_cursor.fetchall()
    
    if not sessions:
        print("   ℹ️  Nenhuma sessão encontrada no SQLite")
        return
    
    migrated = 0
    for session in sessions:
        try:
            pg_cursor.execute(
                """
                INSERT INTO hospital_sessions (
                    token, hospital_id, expires_at, created_at
                ) VALUES (
                    %(token)s, %(hospital_id)s, %(expires_at)s, %(created_at)s
                )
                ON CONFLICT (token) DO NOTHING
                """,
                dict(session),
            )
            migrated += 1
        except Exception as e:
            print(f"   ⚠️  Erro ao migrar sessão {session['token']}: {e}")
    
    pg_conn.commit()
    print(f"   ✅ {migrated} sessões migradas")


def migrate_hospital_forecasts(sqlite_conn, pg_conn):
    """Migra tabela hospital_forecasts."""
    print("📦 Migrando hospital_forecasts...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Buscar todas as previsões do SQLite
    sqlite_cursor.execute("SELECT * FROM hospital_forecasts")
    forecasts = sqlite_cursor.fetchall()
    
    if not forecasts:
        print("   ℹ️  Nenhuma previsão encontrada no SQLite")
        return
    
    migrated = 0
    for forecast in forecasts:
        try:
            pg_cursor.execute(
                """
                INSERT INTO hospital_forecasts (
                    forecast_id, hospital_id, series_id, horizon,
                    payload, average_yhat, created_at
                ) VALUES (
                    %(forecast_id)s, %(hospital_id)s, %(series_id)s, %(horizon)s,
                    %(payload)s, %(average_yhat)s, %(created_at)s
                )
                ON CONFLICT (forecast_id) DO NOTHING
                """,
                dict(forecast),
            )
            migrated += 1
        except Exception as e:
            print(f"   ⚠️  Erro ao migrar previsão {forecast['forecast_id']}: {e}")
    
    pg_conn.commit()
    print(f"   ✅ {migrated} previsões migradas")


def main():
    """Função principal de migração."""
    import os
    
    # Obter URL do PostgreSQL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Variável de ambiente DATABASE_URL não encontrada")
        print("   Exemplo: postgresql://user:password@host:port/database")
        sys.exit(1)
    
    if not database_url.startswith("postgresql"):
        print("❌ DATABASE_URL deve começar com 'postgresql://'")
        sys.exit(1)
    
    print("🚀 Iniciando migração de SQLite para PostgreSQL...")
    print(f"   PostgreSQL URL: {database_url.split('@')[1] if '@' in database_url else 'oculto'}")
    
    # Conectar aos bancos
    sqlite_conn = get_sqlite_connection()
    pg_conn = get_postgresql_connection(database_url)
    
    try:
        # Verificar se as tabelas existem no PostgreSQL
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('hospital_accounts', 'hospital_sessions', 'hospital_forecasts')
        """)
        existing_tables = [row['table_name'] for row in pg_cursor.fetchall()]
        
        if len(existing_tables) < 3:
            print("❌ Tabelas não encontradas no PostgreSQL.")
            print("   Execute o script init_database.py primeiro ou use o schema do database/init.sql")
            sys.exit(1)
        
        # Migrar dados
        migrate_hospital_accounts(sqlite_conn, pg_conn)
        migrate_hospital_sessions(sqlite_conn, pg_conn)
        migrate_hospital_forecasts(sqlite_conn, pg_conn)
        
        print("\n✅ Migração concluída com sucesso!")
        print("\n💡 Próximos passos:")
        print("   1. Verifique os dados no PostgreSQL")
        print("   2. Configure DATABASE_URL no ambiente de produção")
        print("   3. Faça backup do SQLite antes de desativá-lo")
        
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()



