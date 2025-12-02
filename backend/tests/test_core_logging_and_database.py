"""Testes para módulos de infraestrutura: logging e database.

Eles aumentam a cobertura garantindo que:
- configure_logging configure e retorne um logger funcional
- o banco SQLite padrão consegue criar tabelas e inserir/consultar dados
"""

from core.database import (
    execute_many,
    execute_query,
    get_database_type,
    is_sqlite,
)
from core.logging import configure_logging


def test_configure_logging_returns_project_logger():
    """configure_logging deve retornar o logger raiz do projeto."""
    logger = configure_logging()
    assert logger is not None
    assert logger.name == "hospicast"


def test_default_database_is_sqlite_and_accepts_queries(tmp_path, monkeypatch):
    """Em ambiente de teste, o banco padrão deve ser SQLite e aceitar queries simples."""
    # Garantir que estamos usando SQLite (comportamento padrão em testes)
    assert is_sqlite()
    assert get_database_type() == "sqlite"

    # Criar tabela de teste e inserir/consultar dados usando helpers de database
    execute_query(
        """
        CREATE TABLE IF NOT EXISTS test_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """
    )

    execute_many(
        "INSERT INTO test_items (name) VALUES (?)",
        [("item-1",), ("item-2",)],
    )

    rows = execute_query("SELECT id, name FROM test_items ORDER BY id")
    # rows é uma lista de sqlite3.Row
    assert len(rows) == 2
    assert [row["name"] for row in rows] == ["item-1", "item-2"]




