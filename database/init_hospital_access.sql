-- HospiCast Hospital Access Schema
-- PostgreSQL initialization script para tabelas de autenticação e previsões

-- Create extensions (se necessário)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de contas de hospitais
CREATE TABLE IF NOT EXISTS hospital_accounts (
    hospital_id VARCHAR(255) PRIMARY KEY,
    display_name VARCHAR(255) NOT NULL,
    cnes VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(255),
    contact_email VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    short_code VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de sessões (tokens)
CREATE TABLE IF NOT EXISTS hospital_sessions (
    token VARCHAR(255) PRIMARY KEY,
    hospital_id VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospital_accounts(hospital_id) ON DELETE CASCADE
);

-- Tabela de previsões (histórico)
CREATE TABLE IF NOT EXISTS hospital_forecasts (
    forecast_id VARCHAR(255) PRIMARY KEY,
    hospital_id VARCHAR(255) NOT NULL,
    series_id VARCHAR(255) NOT NULL,
    horizon INTEGER NOT NULL,
    payload TEXT NOT NULL,
    average_yhat REAL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospital_accounts(hospital_id) ON DELETE CASCADE
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_sessions_hospital_id ON hospital_sessions(hospital_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON hospital_sessions(token);
CREATE INDEX IF NOT EXISTS idx_forecasts_hospital_id ON hospital_forecasts(hospital_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_created_at ON hospital_forecasts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forecasts_hospital_created ON hospital_forecasts(hospital_id, created_at DESC);

-- Comentários nas tabelas
COMMENT ON TABLE hospital_accounts IS 'Armazena informações de cadastro dos hospitais';
COMMENT ON TABLE hospital_sessions IS 'Armazena tokens de sessão dos hospitais autenticados';
COMMENT ON TABLE hospital_forecasts IS 'Armazena histórico de previsões geradas para cada hospital';



