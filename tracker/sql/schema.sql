-- Schema do Rastreador de Oportunidades — Danzeroum (V1)
-- PostgreSQL 13+ (usa gen_random_uuid(), nativo desde a 13 — sem extensões).
-- Aplicado automaticamente pelo Docker (docker-entrypoint-initdb.d).

-- ── LICITAÇÕES (normalizadas de todas as fontes) ───────────────────────────────
CREATE TABLE IF NOT EXISTS tenders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source          VARCHAR(20)  NOT NULL,   -- 'PNCP', 'COMPRAS_GOV', 'COMPRAS_SP', 'PREF_SP'
    external_id     VARCHAR(120) NOT NULL,   -- id nativo do portal de origem
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    status          VARCHAR(20),             -- 'OPEN','CLOSED','AWARDED','CANCELLED'
    category        VARCHAR(30),             -- 'TI','TELECOM','OUTROS'
    budget_estimate NUMERIC(14,2),
    publish_date    TIMESTAMP,
    deadline        TIMESTAMP,
    url             VARCHAR(500),
    uf              VARCHAR(2),
    raw_json        JSONB,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (source, external_id)             -- dedupe por origem
);

CREATE INDEX IF NOT EXISTS idx_tenders_status   ON tenders (status);
CREATE INDEX IF NOT EXISTS idx_tenders_deadline ON tenders (deadline);
CREATE INDEX IF NOT EXISTS idx_tenders_category ON tenders (category, status);
CREATE INDEX IF NOT EXISTS idx_tenders_fts ON tenders
    USING gin (to_tsvector('portuguese', coalesce(title, '') || ' ' || coalesce(description, '')));

-- ── SCORING (resultado da análise — heurística na V1, LLM no futuro) ───────────
CREATE TABLE IF NOT EXISTS tender_scores (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tender_id        UUID NOT NULL REFERENCES tenders(id) ON DELETE CASCADE,
    risk_score       NUMERIC(3,2) CHECK (risk_score BETWEEN 0 AND 1),
    fit_score        NUMERIC(3,2) CHECK (fit_score BETWEEN 0 AND 1),
    complexity_score NUMERIC(3,2) CHECK (complexity_score BETWEEN 0 AND 1),
    recommendation   VARCHAR(10) CHECK (recommendation IN ('GO', 'REVIEW', 'SKIP')),
    key_requirements JSONB,
    pricing_guidance TEXT,
    analysis_text    TEXT,
    analyzed_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tender_scores_tender ON tender_scores (tender_id);
CREATE INDEX IF NOT EXISTS idx_tender_scores_fit    ON tender_scores (fit_score DESC);

-- ── DOCUMENTOS DA EMPRESA (certidões, atestados) ───────────────────────────────
-- Nota: 'is_valid' é coluna comum (não gerada): CURRENT_DATE não é imutável e o
-- Postgres rejeita GENERATED com função volátil. A validade é calculada na app
-- ou via consulta (expiry_date IS NULL OR expiry_date > CURRENT_DATE).
CREATE TABLE IF NOT EXISTS documents (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type        VARCHAR(40) NOT NULL,  -- 'CND','CRF','FGTS','CERTIDAO_ESTADUAL','ATESTADO_TECNICO'
    subtype     VARCHAR(40),
    name        VARCHAR(120),
    file_path   VARCHAR(500),
    issue_date  DATE,
    expiry_date DATE,
    is_valid    BOOLEAN NOT NULL DEFAULT TRUE,
    notes       TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ── PROPOSTAS ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS proposals (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tender_id     UUID NOT NULL REFERENCES tenders(id) ON DELETE CASCADE,
    submitted_at  TIMESTAMP,
    status        VARCHAR(20),  -- 'SENT','UNDER_REVIEW','WIN','LOST','DISQUALIFIED'
    price_offered NUMERIC(14,2),
    validity_days INT,
    version       INT NOT NULL DEFAULT 1,
    notes         TEXT
);

CREATE INDEX IF NOT EXISTS idx_proposals_tender ON proposals (tender_id);

-- ── ATESTADOS TÉCNICOS ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS technical_certificates (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_name         VARCHAR(120),
    project_description VARCHAR(255),
    start_date          DATE,
    end_date            DATE,
    project_value       NUMERIC(14,2),
    scope               TEXT,
    file_path           VARCHAR(500),
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ── CLIENTES (CRM — evolução futura de crm/*.json) ─────────────────────────────
CREATE TABLE IF NOT EXISTS clients (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source           VARCHAR(20) DEFAULT 'INTERNAL',
    name             VARCHAR(120),
    type             VARCHAR(20),  -- 'PUBLIC','PRIVATE','LEAD'
    cnpj             VARCHAR(14),
    contact_name     VARCHAR(120),
    email            VARCHAR(120),
    phone            VARCHAR(30),
    status           VARCHAR(20),  -- 'LEAD','CLIENT','ARCHIVED'
    notes            TEXT,
    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    last_interaction TIMESTAMP
);
