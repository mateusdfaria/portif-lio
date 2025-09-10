-- HospiCast Database Schema
-- PostgreSQL initialization script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS hospicast;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set default schema
SET search_path TO hospicast, public;

-- Hospitals table
CREATE TABLE IF NOT EXISTS hospitals (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    region VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    capacity INTEGER NOT NULL,
    specialties TEXT[],
    emergency_capacity INTEGER NOT NULL,
    icu_capacity INTEGER NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Hospital metrics table
CREATE TABLE IF NOT EXISTS hospital_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_id VARCHAR(50) REFERENCES hospitals(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    occupancy_rate DECIMAL(5, 3) NOT NULL,
    emergency_occupancy DECIMAL(5, 3) NOT NULL,
    icu_occupancy DECIMAL(5, 3) NOT NULL,
    avg_wait_time DECIMAL(8, 2) NOT NULL,
    total_patients INTEGER NOT NULL,
    emergency_patients INTEGER NOT NULL,
    icu_patients INTEGER NOT NULL,
    discharges INTEGER NOT NULL,
    admissions INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hospital_id, date)
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id VARCHAR(50) PRIMARY KEY,
    hospital_id VARCHAR(50) REFERENCES hospitals(id) ON DELETE CASCADE,
    hospital_name VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    level VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    value DECIMAL(10, 3) NOT NULL,
    threshold DECIMAL(10, 3) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    acknowledged BOOLEAN NOT NULL DEFAULT false,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved BOOLEAN NOT NULL DEFAULT false,
    resolved_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Forecast models table
CREATE TABLE IF NOT EXISTS forecast_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    series_id VARCHAR(100) NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(50) NOT NULL DEFAULT 'prophet',
    parameters JSONB,
    metrics JSONB,
    training_data_size INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(series_id)
);

-- Forecast predictions table
CREATE TABLE IF NOT EXISTS forecast_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES forecast_models(id) ON DELETE CASCADE,
    hospital_id VARCHAR(50) REFERENCES hospitals(id) ON DELETE CASCADE,
    prediction_date DATE NOT NULL,
    horizon INTEGER NOT NULL,
    predictions JSONB NOT NULL,
    confidence_interval JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User sessions table (for future authentication)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100) NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_hospital_metrics_hospital_date ON hospital_metrics(hospital_id, date);
CREATE INDEX IF NOT EXISTS idx_hospital_metrics_date ON hospital_metrics(date);
CREATE INDEX IF NOT EXISTS idx_alerts_hospital_active ON alerts(hospital_id, is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_level_active ON alerts(level, is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_forecast_predictions_hospital_date ON forecast_predictions(hospital_id, prediction_date);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_hospitals_updated_at BEFORE UPDATE ON hospitals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_forecast_models_updated_at BEFORE UPDATE ON forecast_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample hospitals data
INSERT INTO hospitals (id, name, city, state, region, latitude, longitude, capacity, specialties, emergency_capacity, icu_capacity, is_public) VALUES
('hosp_joinville_ps', 'Hospital Municipal São José - Joinville', 'Joinville', 'SC', 'Sul', -26.3044, -48.8456, 200, ARRAY['Emergência', 'Cardiologia', 'Neurologia', 'Pediatria'], 50, 20, true),
('hosp_florianopolis_central', 'Hospital Universitário - Florianópolis', 'Florianópolis', 'SC', 'Sul', -27.5954, -48.5480, 300, ARRAY['Emergência', 'Cardiologia', 'Neurologia', 'Pediatria', 'Oncologia'], 80, 30, true),
('hosp_curitiba_central', 'Hospital de Clínicas - Curitiba', 'Curitiba', 'PR', 'Sul', -25.4284, -49.2733, 500, ARRAY['Emergência', 'Cardiologia', 'Neurologia', 'Pediatria', 'Oncologia', 'Transplantes'], 120, 50, true),
('hosp_sao_paulo_central', 'Hospital das Clínicas - São Paulo', 'São Paulo', 'SP', 'Sudeste', -23.5505, -46.6333, 1000, ARRAY['Emergência', 'Cardiologia', 'Neurologia', 'Pediatria', 'Oncologia', 'Transplantes', 'Trauma'], 200, 100, true),
('hosp_rio_janeiro_central', 'Hospital Universitário Clementino Fraga Filho - Rio de Janeiro', 'Rio de Janeiro', 'RJ', 'Sudeste', -22.9068, -43.1729, 400, ARRAY['Emergência', 'Cardiologia', 'Neurologia', 'Pediatria', 'Oncologia'], 100, 40, true)
ON CONFLICT (id) DO NOTHING;

-- Create views for analytics
CREATE OR REPLACE VIEW analytics.hospital_performance AS
SELECT 
    h.id,
    h.name,
    h.city,
    h.state,
    h.region,
    COUNT(hm.id) as metrics_count,
    AVG(hm.occupancy_rate) as avg_occupancy_rate,
    AVG(hm.emergency_occupancy) as avg_emergency_occupancy,
    AVG(hm.icu_occupancy) as avg_icu_occupancy,
    AVG(hm.avg_wait_time) as avg_wait_time,
    SUM(hm.total_patients) as total_patients,
    SUM(hm.admissions) as total_admissions,
    SUM(hm.discharges) as total_discharges
FROM hospitals h
LEFT JOIN hospital_metrics hm ON h.id = hm.hospital_id
GROUP BY h.id, h.name, h.city, h.state, h.region;

CREATE OR REPLACE VIEW analytics.alert_summary AS
SELECT 
    hospital_id,
    COUNT(*) as total_alerts,
    COUNT(CASE WHEN is_active = true AND resolved = false THEN 1 END) as active_alerts,
    COUNT(CASE WHEN level = 'critical' AND is_active = true THEN 1 END) as critical_alerts,
    COUNT(CASE WHEN level = 'high' AND is_active = true THEN 1 END) as high_alerts,
    COUNT(CASE WHEN level = 'medium' AND is_active = true THEN 1 END) as medium_alerts,
    COUNT(CASE WHEN level = 'low' AND is_active = true THEN 1 END) as low_alerts,
    MAX(timestamp) as latest_alert
FROM alerts
GROUP BY hospital_id;

-- Grant permissions
GRANT USAGE ON SCHEMA hospicast TO hospicast_user;
GRANT USAGE ON SCHEMA analytics TO hospicast_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA hospicast TO hospicast_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO hospicast_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA hospicast TO hospicast_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO hospicast_user;
