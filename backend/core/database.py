"""Módulo de abstração de banco de dados com suporte a SQLite e PostgreSQL."""

from __future__ import annotations

import os
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


def get_database_connection():
    """Retorna uma conexão com o banco de dados apropriado."""
    if DATABASE_TYPE == "postgresql":
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            # Parse da URL do PostgreSQL
            # Formato: postgresql://user:password@host:port/database
            conn = psycopg2.connect(DATABASE_URL)
            conn.cursor_factory = RealDictCursor
            return conn
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
                return cursor.fetchall()
            return cursor.rowcount
        else:
            # SQLite
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                conn.commit()
                return result
            conn.commit()
            return cursor.rowcount
    finally:
        conn.close()


def execute_many(query: str, params_list: list[tuple | dict]) -> None:
    """Executa uma query múltiplas vezes com diferentes parâmetros."""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
    finally:
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

