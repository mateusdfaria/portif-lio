"""Serviço de banco de dados para dados SUS de Joinville"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

# Diretório de dados
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "joinville_sus.db"

@dataclass
class HospitalRecord:
    """Registro de hospital"""
    cnes: str
    nome: str
    endereco: str
    telefone: str
    tipo_gestao: str
    capacidade_total: int
    capacidade_uti: int
    capacidade_emergencia: int
    especialidades: List[str]
    latitude: float
    longitude: float
    municipio: str
    uf: str

@dataclass
class SusDataRecord:
    """Registro de dados SUS"""
    cnes: str
    data: str
    ocupacao_leitos: float
    ocupacao_uti: float
    ocupacao_emergencia: float
    pacientes_internados: int
    pacientes_uti: int
    pacientes_emergencia: int
    admissoes_dia: int
    altas_dia: int
    procedimentos_realizados: int
    tempo_espera_medio: float
    taxa_ocupacao: float

def _get_connection() -> sqlite3.Connection:
    """Retorna conexão com o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Cria as tabelas se não existirem"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            cnes TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            endereco TEXT,
            telefone TEXT,
            tipo_gestao TEXT,
            capacidade_total INTEGER,
            capacidade_uti INTEGER,
            capacidade_emergencia INTEGER,
            especialidades TEXT,  -- JSON array
            latitude REAL,
            longitude REAL,
            municipio TEXT,
            uf TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sus_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnes TEXT NOT NULL,
            data TEXT NOT NULL,
            ocupacao_leitos REAL,
            ocupacao_uti REAL,
            ocupacao_emergencia REAL,
            pacientes_internados INTEGER,
            pacientes_uti INTEGER,
            pacientes_emergencia INTEGER,
            admissoes_dia INTEGER,
            altas_dia INTEGER,
            procedimentos_realizados INTEGER,
            tempo_espera_medio REAL,
            taxa_ocupacao REAL,
            created_at TEXT,
            UNIQUE(cnes, data),
            FOREIGN KEY (cnes) REFERENCES hospitals(cnes)
        )
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sus_data_cnes ON sus_data(cnes);
        CREATE INDEX IF NOT EXISTS idx_sus_data_date ON sus_data(data);
        CREATE INDEX IF NOT EXISTS idx_sus_data_cnes_date ON sus_data(cnes, data);
    """)
    
    conn.commit()

def init_database() -> None:
    """Inicializa o banco de dados"""
    with _get_connection() as conn:
        _ensure_schema(conn)

def save_hospital(hospital: HospitalRecord) -> None:
    """Salva ou atualiza um hospital"""
    with _get_connection() as conn:
        _ensure_schema(conn)
        
        now = datetime.now().isoformat()
        especialidades_json = json.dumps(hospital.especialidades)
        
        conn.execute("""
            INSERT OR REPLACE INTO hospitals (
                cnes, nome, endereco, telefone, tipo_gestao,
                capacidade_total, capacidade_uti, capacidade_emergencia,
                especialidades, latitude, longitude, municipio, uf,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                     COALESCE((SELECT created_at FROM hospitals WHERE cnes = ?), ?),
                     ?)
        """, (
            hospital.cnes, hospital.nome, hospital.endereco, hospital.telefone,
            hospital.tipo_gestao, hospital.capacidade_total, hospital.capacidade_uti,
            hospital.capacidade_emergencia, especialidades_json,
            hospital.latitude, hospital.longitude, hospital.municipio, hospital.uf,
            hospital.cnes, now, now
        ))
        conn.commit()

def get_all_hospitals() -> List[HospitalRecord]:
    """Retorna todos os hospitais"""
    with _get_connection() as conn:
        _ensure_schema(conn)
        
        rows = conn.execute("SELECT * FROM hospitals").fetchall()
        
        hospitals = []
        for row in rows:
            especialidades = json.loads(row['especialidades']) if row['especialidades'] else []
            hospitals.append(HospitalRecord(
                cnes=row['cnes'],
                nome=row['nome'],
                endereco=row['endereco'],
                telefone=row['telefone'],
                tipo_gestao=row['tipo_gestao'],
                capacidade_total=row['capacidade_total'],
                capacidade_uti=row['capacidade_uti'],
                capacidade_emergencia=row['capacidade_emergencia'],
                especialidades=especialidades,
                latitude=row['latitude'],
                longitude=row['longitude'],
                municipio=row['municipio'],
                uf=row['uf']
            ))
        
        return hospitals

def get_hospital_by_cnes(cnes: str) -> Optional[HospitalRecord]:
    """Retorna hospital por CNES"""
    with _get_connection() as conn:
        _ensure_schema(conn)
        
        row = conn.execute("SELECT * FROM hospitals WHERE cnes = ?", (cnes,)).fetchone()
        
        if not row:
            return None
        
        especialidades = json.loads(row['especialidades']) if row['especialidades'] else []
        return HospitalRecord(
            cnes=row['cnes'],
            nome=row['nome'],
            endereco=row['endereco'],
            telefone=row['telefone'],
            tipo_gestao=row['tipo_gestao'],
            capacidade_total=row['capacidade_total'],
            capacidade_uti=row['capacidade_uti'],
            capacidade_emergencia=row['capacidade_emergencia'],
            especialidades=especialidades,
            latitude=row['latitude'],
            longitude=row['longitude'],
            municipio=row['municipio'],
            uf=row['uf']
        )

def save_sus_data(data: SusDataRecord) -> None:
    """Salva dados SUS"""
    with _get_connection() as conn:
        _ensure_schema(conn)
        
        now = datetime.now().isoformat()
        
        conn.execute("""
            INSERT OR REPLACE INTO sus_data (
                cnes, data, ocupacao_leitos, ocupacao_uti, ocupacao_emergencia,
                pacientes_internados, pacientes_uti, pacientes_emergencia,
                admissoes_dia, altas_dia, procedimentos_realizados,
                tempo_espera_medio, taxa_ocupacao, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.cnes, data.data, data.ocupacao_leitos, data.ocupacao_uti,
            data.ocupacao_emergencia, data.pacientes_internados, data.pacientes_uti,
            data.pacientes_emergencia, data.admissoes_dia, data.altas_dia,
            data.procedimentos_realizados, data.tempo_espera_medio,
            data.taxa_ocupacao, now
        ))
        conn.commit()

def save_multiple_sus_data(data_list: List[SusDataRecord]) -> None:
    """Salva múltiplos registros de dados SUS"""
    with _get_connection() as conn:
        _ensure_schema(conn)
        
        now = datetime.now().isoformat()
        
        for data in data_list:
            conn.execute("""
                INSERT OR REPLACE INTO sus_data (
                    cnes, data, ocupacao_leitos, ocupacao_uti, ocupacao_emergencia,
                    pacientes_internados, pacientes_uti, pacientes_emergencia,
                    admissoes_dia, altas_dia, procedimentos_realizados,
                    tempo_espera_medio, taxa_ocupacao, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.cnes, data.data, data.ocupacao_leitos, data.ocupacao_uti,
                data.ocupacao_emergencia, data.pacientes_internados, data.pacientes_uti,
                data.pacientes_emergencia, data.admissoes_dia, data.altas_dia,
                data.procedimentos_realizados, data.tempo_espera_medio,
                data.taxa_ocupacao, now
            ))
        
        conn.commit()

def get_sus_data(cnes: str, start_date: str, end_date: str) -> List[SusDataRecord]:
    """Retorna dados SUS de um hospital no período"""
    with _get_connection() as conn:
        _ensure_schema(conn)
        
        rows = conn.execute("""
            SELECT * FROM sus_data
            WHERE cnes = ? AND data >= ? AND data <= ?
            ORDER BY data ASC
        """, (cnes, start_date, end_date)).fetchall()
        
        data_list = []
        for row in rows:
            data_list.append(SusDataRecord(
                cnes=row['cnes'],
                data=row['data'],
                ocupacao_leitos=row['ocupacao_leitos'],
                ocupacao_uti=row['ocupacao_uti'],
                ocupacao_emergencia=row['ocupacao_emergencia'],
                pacientes_internados=row['pacientes_internados'],
                pacientes_uti=row['pacientes_uti'],
                pacientes_emergencia=row['pacientes_emergencia'],
                admissoes_dia=row['admissoes_dia'],
                altas_dia=row['altas_dia'],
                procedimentos_realizados=row['procedimentos_realizados'],
                tempo_espera_medio=row['tempo_espera_medio'],
                taxa_ocupacao=row['taxa_ocupacao']
            ))
        
        return data_list

def has_sus_data(cnes: str, start_date: str, end_date: str) -> bool:
    """Verifica se existem dados SUS salvos para o período"""
    with _get_connection() as conn:
        _ensure_schema(conn)
        
        count = conn.execute("""
            SELECT COUNT(*) as count FROM sus_data
            WHERE cnes = ? AND data >= ? AND data <= ?
        """, (cnes, start_date, end_date)).fetchone()['count']
        
        return count > 0

# Inicializar banco na importação
init_database()

