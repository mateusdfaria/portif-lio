"""Módulo de abstração de banco de dados com suporte a SQLite e PostgreSQL."""

from __future__ import annotations

import os
import time
from typing import Any

from core.config import get_settings

settings = get_settings()

# Detectar tipo de banco de dados
database_url_env = os.getenv("DATABASE_URL")
database_url_config = settings.database_url

# Prioridade: DATABASE_URL (env) > database_url (config) > database_type
if database_url_env and ("postgresql" in database_url_env.lower() or "postgres" in database_url_env.lower()):
    DATABASE_TYPE = "postgresql"
    DATABASE_URL = database_url_env
elif database_url_config and ("postgresql" in database_url_config.lower() or "postgres" in database_url_config.lower()):
    DATABASE_TYPE = "postgresql"
    DATABASE_URL = database_url_config
elif settings.database_type in ["postgresql", "postgres"]:
    DATABASE_TYPE = "postgresql"
    DATABASE_URL = database_url_config or database_url_env
else:
    DATABASE_TYPE = "sqlite"
    DATABASE_URL = None

# Pool de conexões para PostgreSQL (None = não inicializado)
_postgresql_pool = None
_max_retries = 3
_retry_delay = 1


def _get_postgresql_connection_params():
    """Extrai parâmetros de conexão do DATABASE_URL."""
    from urllib.parse import urlparse, parse_qs
    
    parsed = urlparse(DATABASE_URL)
    user = parsed.username or ""
    password = parsed.password or ""
    database = parsed.path.lstrip("/") or "hospicast"
    query_params = parse_qs(parsed.query)
    host = query_params.get("host", [None])[0]
    port = query_params.get("port", [None])[0] or "5432"
    
    return {
        "user": user,
        "password": password,
        "database": database,
        "host": host,
        "port": port,
    }


def _create_postgresql_pool():
    """Cria ou recria o pool de conexões PostgreSQL."""
    global _postgresql_pool
    
    try:
        import psycopg2
        from psycopg2 import pool
        
        params = _get_postgresql_connection_params()
        
        # Fechar pool existente se houver
        if _postgresql_pool and not _postgresql_pool.closed:
            try:
                _postgresql_pool.closeall()
            except Exception:
                pass
        
        # Criar novo pool com keep-alive para evitar timeouts
        _postgresql_pool = pool.SimpleConnectionPool(
            1,  # min connections
            10,  # max connections
            **params,
            connect_timeout=10,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5,
        )
        
        return _postgresql_pool
    except ImportError:
        raise ImportError(
            "psycopg2-binary não está instalado. "
            "Instale com: pip install psycopg2-binary"
        )


def get_database_connection():
    """Retorna uma conexão com o banco de dados apropriado com retry automático."""
    if DATABASE_TYPE == "postgresql":
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from psycopg2 import OperationalError, InterfaceError, pool
            
            global _postgresql_pool
            
            # Tentar obter conexão com retry
            for attempt in range(_max_retries):
                try:
                    # Criar pool se não existir ou estiver fechado
                    if _postgresql_pool is None or _postgresql_pool.closed:
                        _create_postgresql_pool()
                    
                    # Obter conexão do pool
                    conn = _postgresql_pool.getconn()
                    
                    # Testar conexão (verifica se está válida)
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        cursor.close()
                    except (OperationalError, InterfaceError):
                        # Conexão inválida, devolver ao pool e recriar
                        try:
                            _postgresql_pool.putconn(conn, close=True)
                        except Exception:
                            pass
                        _postgresql_pool = None
                        raise
                    
                    # Configurar cursor factory
                    conn.cursor_factory = RealDictCursor
                    return conn
                    
                except (OperationalError, InterfaceError, pool.PoolError) as e:
                    if attempt < _max_retries - 1:
                        # Aguardar antes de tentar novamente
                        time.sleep(_retry_delay)
                        # Forçar recriação do pool
                        _postgresql_pool = None
                        continue
                    # Última tentativa falhou
                    raise ConnectionError(
                        f"Erro ao conectar ao PostgreSQL após {_max_retries} tentativas: {e}"
                    )
                    
        except ImportError:
            raise ImportError(
                "psycopg2-binary não está instalado. "
                "Instale com: pip install psycopg2-binary"
            )
        except Exception as e:
            raise ConnectionError(f"Erro ao conectar ao PostgreSQL: {e}")
    else:
        # SQLite (padrão)
        import sqlite3
        from pathlib import Path
        
        DATA_DIR = Path(__file__).resolve().parents[1] / "data"
        DATA_DIR.mkdir(exist_ok=True, mode=0o755)
        DB_PATH = DATA_DIR / "hospital_access.db"
        
        conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


def execute_query(query: str, params: tuple | dict | None = None) -> Any:
    """Executa uma query e retorna o resultado."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if DATABASE_TYPE == "postgresql":
            conn.commit()
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                cursor.close()
                return result
            cursor.close()
            return cursor.rowcount
        else:
            # SQLite
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                conn.commit()
                cursor.close()
                return result
            conn.commit()
            cursor.close()
            return cursor.rowcount
    finally:
        # Devolver conexão ao pool (PostgreSQL) ou fechar (SQLite)
        if DATABASE_TYPE == "postgresql":
            global _postgresql_pool
            if _postgresql_pool and not _postgresql_pool.closed:
                try:
                    _postgresql_pool.putconn(conn)
                except (AttributeError, TypeError):
                    # Se houver erro ao devolver, fechar a conexão
                    try:
                        conn.close()
                    except Exception:  # pylint: disable=broad-except
                        # Ignorar erros ao fechar conexão já fechada
                        pass
        else:
            conn.close()


def execute_many(query: str, params_list: list[tuple | dict]) -> None:
    """Executa uma query múltiplas vezes com diferentes parâmetros."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        if DATABASE_TYPE == "postgresql":
            conn.commit()
        else:
            conn.commit()
        cursor.close()
    finally:
        # Devolver conexão ao pool (PostgreSQL) ou fechar (SQLite)
        if DATABASE_TYPE == "postgresql":
            global _postgresql_pool
            if _postgresql_pool and not _postgresql_pool.closed:
                try:
                    _postgresql_pool.putconn(conn)
                except Exception:
                    try:
                        conn.close()
                    except Exception:
                        pass
        else:
            conn.close()


def get_database_type() -> str:
    """Retorna o tipo de banco de dados em uso."""
    return DATABASE_TYPE


def is_postgresql() -> bool:
    """Verifica se está usando PostgreSQL."""
    return DATABASE_TYPE == "postgresql"


def is_sqlite() -> bool:
    """Verifica se está usando SQLite."""
    return DATABASE_TYPE == "sqlite"

