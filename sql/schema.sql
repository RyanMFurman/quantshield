-- QuantShield foundational schema

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS market_prices (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price NUMERIC(12,4) NOT NULL,
    volume BIGINT,
    prev_close NUMERIC(12,4),
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_price_positive CHECK (price > 0)
);

CREATE INDEX IF NOT EXISTS idx_prices_symbol_time
ON market_prices (symbol, captured_at DESC);

CREATE TABLE IF NOT EXISTS security_events (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID NOT NULL UNIQUE,
    event_type VARCHAR(100) NOT NULL,
    source_ip INET,
    username VARCHAR(255),
    user_agent TEXT,
    result VARCHAR(20),
    raw_payload JSONB,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_type ON security_events (event_type);
CREATE INDEX IF NOT EXISTS idx_events_ip ON security_events (source_ip);
CREATE INDEX IF NOT EXISTS idx_events_occurred ON security_events (occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_payload ON security_events USING GIN (raw_payload);

CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    rule_id VARCHAR(50) NOT NULL,
    rule_name VARCHAR(255) NOT NULL,
    severity VARCHAR(10) NOT NULL CHECK (severity IN ('P1','P2','P3','P4')),
    mitre_tactic VARCHAR(100),
    mitre_technique VARCHAR(20),
    affected_user VARCHAR(255),
    source_ip INET,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','ACK','RESOLVED','FP')),
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_alerts_status_time
ON alerts (status, triggered_at DESC);

CREATE TABLE IF NOT EXISTS incidents (
    id BIGSERIAL PRIMARY KEY,
    incident_code VARCHAR(40) NOT NULL UNIQUE,
    alert_id BIGINT NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    priority VARCHAR(10) NOT NULL CHECK (priority IN ('P1','P2','P3','P4')),
    owner VARCHAR(255),
    summary TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','IN_PROGRESS','RESOLVED')),
    opened_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_incidents_status_opened
ON incidents (status, opened_at DESC);
