"""Serviços de cadastro/autenticação de hospitais e histórico de previsões."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import bcrypt

# Diretório de dados - funciona em desenvolvimento e produção
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(exist_ok=True, mode=0o755)  # Garantir permissões
DB_PATH = DATA_DIR / "hospital_access.db"


def _get_connection() -> sqlite3.Connection:
    """Retorna conexão com o banco de dados, criando se necessário"""
    # Garantir que o diretório existe
    DATA_DIR.mkdir(exist_ok=True, mode=0o755)
    
    # Conectar ao banco (cria automaticamente se não existir)
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    conn.row_factory = sqlite3.Row
    
    # Habilitar foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Criar schema se necessário
    _ensure_schema(conn)
    
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Cria as tabelas do banco de dados se não existirem"""
    # Tabela de contas de hospitais
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS hospital_accounts (
            hospital_id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            cnes TEXT,
            city TEXT,
            state TEXT,
            contact_email TEXT,
            password_hash TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    
    # Tabela de sessões (tokens)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS hospital_sessions (
            token TEXT PRIMARY KEY,
            hospital_id TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (hospital_id) REFERENCES hospital_accounts(hospital_id)
        )
        """
    )
    
    # Tabela de previsões (histórico)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS hospital_forecasts (
            forecast_id TEXT PRIMARY KEY,
            hospital_id TEXT NOT NULL,
            series_id TEXT NOT NULL,
            horizon INTEGER NOT NULL,
            payload TEXT NOT NULL,
            average_yhat REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (hospital_id) REFERENCES hospital_accounts(hospital_id)
        )
        """
    )
    
    # Criar índices para melhor performance
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_sessions_hospital_id 
        ON hospital_sessions(hospital_id)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_sessions_token 
        ON hospital_sessions(token)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_forecasts_hospital_id 
        ON hospital_forecasts(hospital_id)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_forecasts_created_at 
        ON hospital_forecasts(created_at DESC)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_forecasts_hospital_created 
        ON hospital_forecasts(hospital_id, created_at DESC)
        """
    )
    
    conn.commit()


def _slugify(value: str) -> str:
    import re

    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def _normalize_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _normalize_json(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_normalize_json(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize_json(item) for item in value]
    if isinstance(value, set):
        return [_normalize_json(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:  # pragma: no cover - fallback seguro
            pass
    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except Exception:  # pragma: no cover
            pass
    return value


class HospitalAccountService:
    """Gerencia contas de hospitais e sessões."""

    def register_hospital(self, payload: dict) -> dict:
        hospital_id = payload.get("hospital_id") or str(uuid.uuid4())
        display_name = payload["display_name"].strip()
        short_code = payload.get("short_code") or f"{_slugify(display_name)[:20]}-{hospital_id[:8]}"
        password = payload["password"].encode("utf-8")
        password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")

        record = {
            "hospital_id": hospital_id,
            "display_name": display_name,
            "cnes": payload.get("cnes"),
            "city": payload.get("city"),
            "state": payload.get("state"),
            "contact_email": payload.get("contact_email"),
            "password_hash": password_hash,
            "short_code": short_code,
            "created_at": datetime.now(UTC).isoformat(),
        }

        with _get_connection() as conn:
            conn.execute(
                """
                INSERT INTO hospital_accounts (
                    hospital_id, display_name, cnes, city, state,
                    contact_email, password_hash, short_code, created_at
                ) VALUES (:hospital_id, :display_name, :cnes, :city, :state,
                          :contact_email, :password_hash, :short_code, :created_at)
                """,
                record,
            )
            conn.commit()

        return {
            "hospital_id": hospital_id,
            "display_name": display_name,
            "short_code": short_code,
            "created_at": record["created_at"],
        }

    def authenticate(self, identifier: str, password: str) -> dict:
        with _get_connection() as conn:
            row = conn.execute(
                """
                SELECT hospital_id, display_name, password_hash, short_code
                FROM hospital_accounts
                WHERE hospital_id = ? OR short_code = ?
                """,
                (identifier, identifier),
            ).fetchone()

        if not row:
            raise ValueError("Hospital não encontrado.")

        stored_hash = row["password_hash"].encode("utf-8")
        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            raise ValueError("Senha inválida.")

        token = str(uuid.uuid4())
        expires_at = datetime.now(UTC) + timedelta(hours=12)

        session = {
            "token": token,
            "hospital_id": row["hospital_id"],
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now(UTC).isoformat(),
        }

        with _get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO hospital_sessions (token, hospital_id, expires_at, created_at)
                VALUES (:token, :hospital_id, :expires_at, :created_at)
                """,
                session,
            )
            conn.commit()

        return {
            "hospital_id": row["hospital_id"],
            "display_name": row["display_name"],
            "short_code": row["short_code"],
            "token": token,
            "expires_at": session["expires_at"],
        }

    def validate_session(self, hospital_id: str, token: str) -> bool:
        with _get_connection() as conn:
            row = conn.execute(
                """
                SELECT expires_at FROM hospital_sessions
                WHERE token = ? AND hospital_id = ?
                """,
                (token, hospital_id),
            ).fetchone()

        if not row:
            return False

        expires_at = datetime.fromisoformat(row["expires_at"])
        if expires_at < datetime.now(UTC):
            self.invalidate_session(token)
            return False
        return True

    def invalidate_session(self, token: str) -> None:
        with _get_connection() as conn:
            conn.execute("DELETE FROM hospital_sessions WHERE token = ?", (token,))
            conn.commit()

    def record_forecast(
        self,
        hospital_id: str,
        series_id: str,
        horizon: int,
        forecast_payload: dict,
        avg_yhat: float | None,
    ) -> None:
        normalized_payload = _normalize_json(forecast_payload)
        entry = {
            "forecast_id": str(uuid.uuid4()),
            "hospital_id": hospital_id,
            "series_id": series_id,
            "horizon": horizon,
            "payload": json.dumps(normalized_payload, ensure_ascii=False),
            "average_yhat": avg_yhat,
            "created_at": datetime.now(UTC).isoformat(),
        }

        with _get_connection() as conn:
            conn.execute(
                """
                INSERT INTO hospital_forecasts (
                    forecast_id, hospital_id, series_id, horizon,
                    payload, average_yhat, created_at
                ) VALUES (
                    :forecast_id, :hospital_id, :series_id, :horizon,
                    :payload, :average_yhat, :created_at
                )
                """,
                entry,
            )
            conn.commit()

    def list_forecasts(self, hospital_id: str, limit: int = 20) -> list[dict]:
        with _get_connection() as conn:
            rows = conn.execute(
                """
                SELECT forecast_id, series_id, horizon, payload, average_yhat, created_at
                FROM hospital_forecasts
                WHERE hospital_id = ?
                ORDER BY datetime(created_at) DESC
                LIMIT ?
                """,
                (hospital_id, limit),
            ).fetchall()

        forecasts: list[dict] = []
        for row in rows:
            payload = json.loads(row["payload"])
            forecasts.append(
                {
                    "forecast_id": row["forecast_id"],
                    "series_id": row["series_id"],
                    "horizon": row["horizon"],
                    "average_yhat": row["average_yhat"],
                    "created_at": row["created_at"],
                    "payload": payload,
                }
            )
        return forecasts

    def get_hospital_metadata(self, hospital_id: str) -> dict | None:
        with _get_connection() as conn:
            row = conn.execute(
                """
                SELECT hospital_id, display_name, city, state, cnes, short_code, created_at
                FROM hospital_accounts
                WHERE hospital_id = ?
                """,
                (hospital_id,),
            ).fetchone()
        if not row:
            return None
        return dict(row)


hospital_account_service = HospitalAccountService()

