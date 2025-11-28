"""Serviços de cadastro/autenticação de hospitais e histórico de previsões."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt

from core.database import get_database_connection, get_database_type, is_postgresql


def _get_connection():
    """Retorna conexão com o banco de dados, criando schema se necessário"""
    conn = get_database_connection()
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn) -> None:
    """Cria as tabelas do banco de dados se não existirem"""
    is_pg = is_postgresql()
    
    # Adaptar tipos de dados para PostgreSQL vs SQLite
    if is_pg:
        text_type = "VARCHAR(255)"
        text_primary = "VARCHAR(255) PRIMARY KEY"
        text_unique = "VARCHAR(255) UNIQUE NOT NULL"
        integer_type = "INTEGER"
        real_type = "REAL"
        timestamp_type = "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
        created_at_type = "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP"
    else:
        text_type = "TEXT"
        text_primary = "TEXT PRIMARY KEY"
        text_unique = "TEXT UNIQUE NOT NULL"
        integer_type = "INTEGER"
        real_type = "REAL"
        timestamp_type = "TEXT NOT NULL"
        created_at_type = "TEXT NOT NULL"
    
    cursor = conn.cursor()
    
    # Tabela de contas de hospitais
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS hospital_accounts (
            hospital_id {text_primary},
            display_name {text_type} NOT NULL,
            cnes {text_type},
            city {text_type},
            state {text_type},
            contact_email {text_type},
            password_hash {text_type} NOT NULL,
            short_code {text_unique},
            created_at {created_at_type}
        )
        """
    )
    
    # Tabela de sessões (tokens)
    if is_pg:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS hospital_sessions (
                token VARCHAR(255) PRIMARY KEY,
                hospital_id VARCHAR(255) NOT NULL,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hospital_id) REFERENCES hospital_accounts(hospital_id) ON DELETE CASCADE
            )
            """
        )
    else:
        cursor.execute(
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
    if is_pg:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS hospital_forecasts (
                forecast_id VARCHAR(255) PRIMARY KEY,
                hospital_id VARCHAR(255) NOT NULL,
                series_id VARCHAR(255) NOT NULL,
                horizon INTEGER NOT NULL,
                payload TEXT NOT NULL,
                average_yhat REAL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hospital_id) REFERENCES hospital_accounts(hospital_id) ON DELETE CASCADE
            )
            """
        )
    else:
        cursor.execute(
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
    indexes = [
        ("idx_sessions_hospital_id", "hospital_sessions", "hospital_id"),
        ("idx_sessions_token", "hospital_sessions", "token"),
        ("idx_forecasts_hospital_id", "hospital_forecasts", "hospital_id"),
        ("idx_forecasts_created_at", "hospital_forecasts", "created_at DESC"),
        ("idx_forecasts_hospital_created", "hospital_forecasts", "hospital_id, created_at DESC"),
    ]
    
    for idx_name, table, columns in indexes:
        if is_pg:
            # PostgreSQL usa CREATE INDEX IF NOT EXISTS diretamente
            cursor.execute(
                f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({columns})"
            )
        else:
            # SQLite também suporta CREATE INDEX IF NOT EXISTS
            cursor.execute(
                f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({columns})"
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


def _format_datetime(dt: datetime) -> str:
    """Formata datetime para string compatível com ambos os bancos."""
    return dt.isoformat()


def _parse_datetime(dt_str: str) -> datetime:
    """Parse datetime string para objeto datetime."""
    if isinstance(dt_str, datetime):
        return dt_str
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


class HospitalAccountService:
    """Gerencia contas de hospitais e sessões."""

    def register_hospital(self, payload: dict) -> dict:
        hospital_id = payload.get("hospital_id") or str(uuid.uuid4())
        display_name = payload["display_name"].strip()
        short_code = payload.get("short_code") or f"{_slugify(display_name)[:20]}-{hospital_id[:8]}"
        password = payload["password"].encode("utf-8")
        password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")

        created_at = datetime.now(UTC)
        created_at_str = _format_datetime(created_at)

        record = {
            "hospital_id": hospital_id,
            "display_name": display_name,
            "cnes": payload.get("cnes"),
            "city": payload.get("city"),
            "state": payload.get("state"),
            "contact_email": payload.get("contact_email"),
            "password_hash": password_hash,
            "short_code": short_code,
            "created_at": created_at_str if not is_postgresql() else created_at,
        }

        is_pg = is_postgresql()
        conn = _get_connection()
        try:
            cursor = conn.cursor()
            if is_pg:
                cursor.execute(
                    """
                    INSERT INTO hospital_accounts (
                        hospital_id, display_name, cnes, city, state,
                        contact_email, password_hash, short_code, created_at
                    ) VALUES (
                        %(hospital_id)s, %(display_name)s, %(cnes)s, %(city)s, %(state)s,
                        %(contact_email)s, %(password_hash)s, %(short_code)s, %(created_at)s
                    )
                    """,
                    record,
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO hospital_accounts (
                        hospital_id, display_name, cnes, city, state,
                        contact_email, password_hash, short_code, created_at
                    ) VALUES (
                        :hospital_id, :display_name, :cnes, :city, :state,
                        :contact_email, :password_hash, :short_code, :created_at
                    )
                    """,
                    record,
                )
            conn.commit()
        finally:
            conn.close()

        return {
            "hospital_id": hospital_id,
            "display_name": display_name,
            "short_code": short_code,
            "created_at": created_at_str,
        }

    def authenticate(self, identifier: str, password: str) -> dict:
        is_pg = is_postgresql()
        conn = _get_connection()
        try:
            cursor = conn.cursor()
            if is_pg:
                cursor.execute(
                    """
                    SELECT hospital_id, display_name, password_hash, short_code
                    FROM hospital_accounts
                    WHERE hospital_id = %s OR short_code = %s
                    """,
                    (identifier, identifier),
                )
            else:
                cursor.execute(
                    """
                    SELECT hospital_id, display_name, password_hash, short_code
                    FROM hospital_accounts
                    WHERE hospital_id = ? OR short_code = ?
                    """,
                    (identifier, identifier),
                )
            row = cursor.fetchone()

            if not row:
                raise ValueError("Hospital não encontrado.")

            # Converter row para dict
            if is_pg:
                row_dict = dict(row)
            else:
                row_dict = dict(row)

            stored_hash = row_dict["password_hash"].encode("utf-8")
            if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
                raise ValueError("Senha inválida.")

            token = str(uuid.uuid4())
            expires_at = datetime.now(UTC) + timedelta(hours=12)

            session = {
                "token": token,
                "hospital_id": row_dict["hospital_id"],
                "expires_at": expires_at if is_pg else _format_datetime(expires_at),
                "created_at": datetime.now(UTC) if is_pg else _format_datetime(datetime.now(UTC)),
            }

            if is_pg:
                cursor.execute(
                    """
                    INSERT INTO hospital_sessions (token, hospital_id, expires_at, created_at)
                    VALUES (%(token)s, %(hospital_id)s, %(expires_at)s, %(created_at)s)
                    ON CONFLICT (token) DO UPDATE SET
                        hospital_id = EXCLUDED.hospital_id,
                        expires_at = EXCLUDED.expires_at,
                        created_at = EXCLUDED.created_at
                    """,
                    session,
                )
            else:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO hospital_sessions (token, hospital_id, expires_at, created_at)
                    VALUES (:token, :hospital_id, :expires_at, :created_at)
                    """,
                    session,
                )
            conn.commit()
        finally:
            conn.close()

        return {
            "hospital_id": row_dict["hospital_id"],
            "display_name": row_dict["display_name"],
            "short_code": row_dict["short_code"],
            "token": token,
            "expires_at": _format_datetime(expires_at),
        }

    def validate_session(self, hospital_id: str, token: str) -> bool:
        is_pg = is_postgresql()
        conn = _get_connection()
        try:
            cursor = conn.cursor()
            if is_pg:
                cursor.execute(
                    """
                    SELECT expires_at FROM hospital_sessions
                    WHERE token = %s AND hospital_id = %s
                    """,
                    (token, hospital_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT expires_at FROM hospital_sessions
                    WHERE token = ? AND hospital_id = ?
                    """,
                    (token, hospital_id),
                )
            row = cursor.fetchone()

            if not row:
                return False

            # Converter row para dict
            if is_pg:
                expires_at = row["expires_at"]
                if isinstance(expires_at, str):
                    expires_at = _parse_datetime(expires_at)
            else:
                expires_at = _parse_datetime(row["expires_at"])

            if expires_at < datetime.now(UTC):
                self.invalidate_session(token)
                return False
            return True
        finally:
            conn.close()

    def invalidate_session(self, token: str) -> None:
        is_pg = is_postgresql()
        conn = _get_connection()
        try:
            cursor = conn.cursor()
            if is_pg:
                cursor.execute("DELETE FROM hospital_sessions WHERE token = %s", (token,))
            else:
                cursor.execute("DELETE FROM hospital_sessions WHERE token = ?", (token,))
            conn.commit()
        finally:
            conn.close()

    def record_forecast(
        self,
        hospital_id: str,
        series_id: str,
        horizon: int,
        forecast_payload: dict,
        avg_yhat: float | None,
    ) -> None:
        normalized_payload = _normalize_json(forecast_payload)
        created_at = datetime.now(UTC)
        
        entry = {
            "forecast_id": str(uuid.uuid4()),
            "hospital_id": hospital_id,
            "series_id": series_id,
            "horizon": horizon,
            "payload": json.dumps(normalized_payload, ensure_ascii=False),
            "average_yhat": avg_yhat,
            "created_at": created_at if is_postgresql() else _format_datetime(created_at),
        }

        is_pg = is_postgresql()
        conn = _get_connection()
        try:
            cursor = conn.cursor()
            if is_pg:
                cursor.execute(
                    """
                    INSERT INTO hospital_forecasts (
                        forecast_id, hospital_id, series_id, horizon,
                        payload, average_yhat, created_at
                    ) VALUES (
                        %(forecast_id)s, %(hospital_id)s, %(series_id)s, %(horizon)s,
                        %(payload)s, %(average_yhat)s, %(created_at)s
                    )
                    """,
                    entry,
                )
            else:
                cursor.execute(
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
        finally:
            conn.close()

    def list_forecasts(self, hospital_id: str, limit: int = 20) -> list[dict]:
        is_pg = is_postgresql()
        conn = _get_connection()
        try:
            cursor = conn.cursor()
            if is_pg:
                cursor.execute(
                    """
                    SELECT forecast_id, series_id, horizon, payload, average_yhat, created_at
                    FROM hospital_forecasts
                    WHERE hospital_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (hospital_id, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT forecast_id, series_id, horizon, payload, average_yhat, created_at
                    FROM hospital_forecasts
                    WHERE hospital_id = ?
                    ORDER BY datetime(created_at) DESC
                    LIMIT ?
                    """,
                    (hospital_id, limit),
                )
            rows = cursor.fetchall()

            forecasts: list[dict] = []
            for row in rows:
                if is_pg:
                    row_dict = dict(row)
                else:
                    row_dict = dict(row)
                
                payload = json.loads(row_dict["payload"])
                created_at = row_dict["created_at"]
                if isinstance(created_at, datetime):
                    created_at = _format_datetime(created_at)
                
                forecasts.append(
                    {
                        "forecast_id": row_dict["forecast_id"],
                        "series_id": row_dict["series_id"],
                        "horizon": row_dict["horizon"],
                        "average_yhat": row_dict["average_yhat"],
                        "created_at": created_at,
                        "payload": payload,
                    }
                )
            return forecasts
        finally:
            conn.close()

    def get_hospital_metadata(self, hospital_id: str) -> dict | None:
        is_pg = is_postgresql()
        conn = _get_connection()
        try:
            cursor = conn.cursor()
            if is_pg:
                cursor.execute(
                    """
                    SELECT hospital_id, display_name, city, state, cnes, short_code, created_at
                    FROM hospital_accounts
                    WHERE hospital_id = %s
                    """,
                    (hospital_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT hospital_id, display_name, city, state, cnes, short_code, created_at
                    FROM hospital_accounts
                    WHERE hospital_id = ?
                    """,
                    (hospital_id,),
                )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            if is_pg:
                result = dict(row)
            else:
                result = dict(row)
            
            # Converter created_at para string se necessário
            if isinstance(result.get("created_at"), datetime):
                result["created_at"] = _format_datetime(result["created_at"])
            
            return result
        finally:
            conn.close()


hospital_account_service = HospitalAccountService()
