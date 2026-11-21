-- Gold Trust AI: Initial PostgreSQL Schema with DB-Enforced Integrity & RLS
-- Per ADR-0003, ADR-0004, ADR-0018 and §5.2, §6.4, §6.5

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. SHOP & USERS (Multi-Tenancy Core)
-- ============================================================================
CREATE TABLE IF NOT EXISTS shop (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    license_no TEXT,
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staff (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL, -- Argon2id
    role TEXT NOT NULL CHECK (role IN ('OWNER', 'MANAGER', 'APPRAISER', 'AUDITOR')),
    totp_secret TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (shop_id, username)
);

-- ============================================================================
-- 2. INSTRUMENTS & POLICY
-- ============================================================================
CREATE TABLE IF NOT EXISTS instrument (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    kind TEXT NOT NULL CHECK (kind IN ('SCALE', 'XRF', 'KARAT_METER', 'DENSITY_METER')),
    serial_no TEXT NOT NULL,
    make_model TEXT,
    calibration_date TIMESTAMPTZ NOT NULL,
    calibration_expiry TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shop_policy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1,
    max_deduction_bp BIGINT NOT NULL CHECK (max_deduction_bp >= 0 AND max_deduction_bp <= 10000),
    xrf_max_variance_permille BIGINT NOT NULL CHECK (xrf_max_variance_permille >= 0 AND xrf_max_variance_permille <= 1000),
    scale_calibration_required BOOLEAN NOT NULL DEFAULT TRUE,
    min_independent_purity_sources INTEGER NOT NULL DEFAULT 2,
    day_close_max_variance_ug BIGINT NOT NULL DEFAULT 100000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (shop_id, version)
);

CREATE TABLE IF NOT EXISTS rate_snapshot (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    rate_paise_per_g BIGINT NOT NULL CHECK (rate_paise_per_g > 0),
    source TEXT NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ NOT NULL,
    created_by UUID NOT NULL REFERENCES staff(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 3. EXCHANGES & EVIDENCE READINGS
-- ============================================================================
CREATE TABLE IF NOT EXISTS exchange (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    state TEXT NOT NULL CHECK (state IN (
        'DRAFT', 'INTAKE_LOCKED', 'EVIDENCE_CAPTURED', 'VALIDATION_CLEAR',
        'REVIEW_REQUIRED', 'QUOTED', 'CUSTOMER_REVIEW', 'COSIGNED',
        'SETTLEMENT_PENDING', 'SETTLED', 'CLOSED', 'CANCELLED'
    )),
    is_demo BOOLEAN NOT NULL DEFAULT FALSE,
    version INTEGER NOT NULL DEFAULT 1,
    customer_ref TEXT NOT NULL, -- HMAC-SHA256 pseudonym
    created_by UUID NOT NULL REFERENCES staff(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reading (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exchange_id UUID NOT NULL REFERENCES exchange(id) ON DELETE CASCADE,
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    kind TEXT NOT NULL CHECK (kind IN (
        'SCALE_GROSS', 'SCALE_STONES', 'XRF_POINT', 'KARAT_METER',
        'TOUCHSTONE_RANGE', 'ASSAY'
    )),
    value_int BIGINT NOT NULL,
    unit TEXT NOT NULL CHECK (unit IN ('mg', 'permille', 'ug')),
    tolerance_int BIGINT NOT NULL DEFAULT 0,
    instrument_id UUID REFERENCES instrument(id),
    point_index INTEGER NOT NULL DEFAULT 1,
    source_kind TEXT NOT NULL CHECK (source_kind IN ('MANUAL', 'OCR_CONFIRMED')),
    evidence_blob_sha256 TEXT,
    captured_by UUID NOT NULL REFERENCES staff(id),
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    superseded_by UUID REFERENCES reading(id)
);

CREATE TABLE IF NOT EXISTS weight_witness (
    exchange_id UUID PRIMARY KEY REFERENCES exchange(id) ON DELETE CASCADE,
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    customer_entry_mg BIGINT NOT NULL CHECK (customer_entry_mg >= 0),
    mode TEXT NOT NULL CHECK (mode IN ('OWN_DEVICE', 'ASSISTED')),
    entered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    matched BOOLEAN NOT NULL DEFAULT FALSE
);

-- ============================================================================
-- 4. RECEIPTS & AUDIT HASH CHAIN (Append-Only)
-- ============================================================================
CREATE TABLE IF NOT EXISTS receipt (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exchange_id UUID NOT NULL REFERENCES exchange(id) ON DELETE RESTRICT,
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    receipt_hash TEXT NOT NULL UNIQUE,
    canonical_payload JSONB NOT NULL,
    supersedes_receipt_hash TEXT REFERENCES receipt(receipt_hash),
    is_demo BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_event (
    seq BIGSERIAL PRIMARY KEY,
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor UUID NOT NULL REFERENCES staff(id),
    action TEXT NOT NULL,
    object_type TEXT NOT NULL,
    object_id UUID NOT NULL,
    payload JSONB NOT NULL,
    prev_hash TEXT NOT NULL,
    this_hash TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS daily_manifest (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    date_iso DATE NOT NULL,
    seq_start BIGINT NOT NULL,
    seq_end BIGINT NOT NULL,
    event_count BIGINT NOT NULL,
    last_event_hash TEXT NOT NULL,
    manifest_hash TEXT NOT NULL UNIQUE,
    signature_hex TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (shop_id, date_iso)
);

-- ============================================================================
-- 5. BALANCED DUAL LEDGERS (Gold in µg, Money in Paise)
-- ============================================================================
CREATE TABLE IF NOT EXISTS gold_journal_entry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    exchange_id UUID REFERENCES exchange(id) ON DELETE RESTRICT,
    receipt_hash TEXT REFERENCES receipt(receipt_hash),
    entry_name TEXT NOT NULL,
    description TEXT NOT NULL,
    reverses_entry_id UUID REFERENCES gold_journal_entry(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gold_journal_line (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID NOT NULL REFERENCES gold_journal_entry(id) ON DELETE CASCADE,
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    account TEXT NOT NULL,
    side CHAR(1) NOT NULL CHECK (side IN ('D', 'C')),
    amount_ug BIGINT NOT NULL CHECK (amount_ug >= 0)
);

CREATE TABLE IF NOT EXISTS money_journal_entry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    exchange_id UUID REFERENCES exchange(id) ON DELETE RESTRICT,
    receipt_hash TEXT REFERENCES receipt(receipt_hash),
    entry_name TEXT NOT NULL,
    description TEXT NOT NULL,
    reverses_entry_id UUID REFERENCES money_journal_entry(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS money_journal_line (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID NOT NULL REFERENCES money_journal_entry(id) ON DELETE CASCADE,
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    account TEXT NOT NULL,
    side CHAR(1) NOT NULL CHECK (side IN ('D', 'C')),
    amount_paise BIGINT NOT NULL CHECK (amount_paise >= 0)
);

-- ============================================================================
-- 6. DAY-CLOSE RECONCILIATION & ASYNC JOBS
-- ============================================================================
CREATE TABLE IF NOT EXISTS day_close (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    date_iso DATE NOT NULL,
    opening_gold_ug BIGINT NOT NULL,
    intake_gold_ug BIGINT NOT NULL,
    discharged_gold_ug BIGINT NOT NULL,
    expected_closing_gold_ug BIGINT NOT NULL,
    physical_count_gold_ug BIGINT NOT NULL,
    variance_gold_ug BIGINT NOT NULL,
    opening_cash_paise BIGINT NOT NULL,
    payout_cash_paise BIGINT NOT NULL,
    closing_cash_paise BIGINT NOT NULL,
    is_balanced BOOLEAN NOT NULL,
    closed_by UUID NOT NULL REFERENCES staff(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (shop_id, date_iso)
);

CREATE TABLE IF NOT EXISTS stock_variance_exception (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    day_close_id UUID NOT NULL REFERENCES day_close(id) ON DELETE RESTRICT,
    variance_gold_ug BIGINT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('WARNING', 'CRITICAL_MELT_GAIN', 'INVESTIGATION_REQUIRED')),
    explanation TEXT,
    logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS job (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shop(id) ON DELETE RESTRICT,
    kind TEXT NOT NULL CHECK (kind IN ('OCR_BILL', 'GENERATE_PDF', 'SIGN_MANIFEST')),
    payload JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    error_message TEXT,
    run_after TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 7. INTEGRITY TRIGGERS: APPEND-ONLY & DEFERRED BALANCE ENFORCEMENT
-- ============================================================================

-- Function: Forbid UPDATE, DELETE, or TRUNCATE on append-only audit & ledger records
CREATE OR REPLACE FUNCTION forbid_mutation() RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION '% is strictly append-only. UPDATE, DELETE, and TRUNCATE are prohibited.',
        TG_TABLE_NAME USING ERRCODE = 'integrity_constraint_violation';
END;
$$;

-- Function: Check Gold Journal Entry Balance at Transaction Commit
CREATE OR REPLACE FUNCTION check_gold_entry_balanced() RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    target_entry_id UUID := COALESCE(NEW.entry_id, OLD.entry_id);
    sum_diff BIGINT;
    line_count INT;
BEGIN
    SELECT COALESCE(SUM(CASE side WHEN 'D' THEN amount_ug ELSE -amount_ug END), 0), COUNT(*)
    INTO sum_diff, line_count
    FROM gold_journal_line
    WHERE entry_id = target_entry_id;

    IF line_count < 2 OR sum_diff <> 0 THEN
        RAISE EXCEPTION 'Unbalanced or empty gold journal entry %: net difference = % ug across % lines',
            target_entry_id, sum_diff, line_count USING ERRCODE = 'check_violation';
    END IF;
    RETURN NULL;
END;
$$;

-- Function: Check Money Journal Entry Balance at Transaction Commit
CREATE OR REPLACE FUNCTION check_money_entry_balanced() RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    target_entry_id UUID := COALESCE(NEW.entry_id, OLD.entry_id);
    sum_diff BIGINT;
    line_count INT;
BEGIN
    SELECT COALESCE(SUM(CASE side WHEN 'D' THEN amount_paise ELSE -amount_paise END), 0), COUNT(*)
    INTO sum_diff, line_count
    FROM money_journal_line
    WHERE entry_id = target_entry_id;

    IF line_count < 2 OR sum_diff <> 0 THEN
        RAISE EXCEPTION 'Unbalanced or empty money journal entry %: net difference = % paise across % lines',
            target_entry_id, sum_diff, line_count USING ERRCODE = 'check_violation';
    END IF;
    RETURN NULL;
END;
$$;

-- Apply Append-Only Triggers
CREATE OR REPLACE TRIGGER audit_no_mutation
    BEFORE UPDATE OR DELETE ON audit_event
    FOR EACH ROW EXECUTE FUNCTION forbid_mutation();

CREATE OR REPLACE TRIGGER receipt_no_mutation
    BEFORE UPDATE OR DELETE ON receipt
    FOR EACH ROW EXECUTE FUNCTION forbid_mutation();

CREATE OR REPLACE TRIGGER gold_entry_no_mutation
    BEFORE UPDATE OR DELETE ON gold_journal_entry
    FOR EACH ROW EXECUTE FUNCTION forbid_mutation();

CREATE OR REPLACE TRIGGER gold_line_no_mutation
    BEFORE UPDATE OR DELETE ON gold_journal_line
    FOR EACH ROW EXECUTE FUNCTION forbid_mutation();

CREATE OR REPLACE TRIGGER money_entry_no_mutation
    BEFORE UPDATE OR DELETE ON money_journal_entry
    FOR EACH ROW EXECUTE FUNCTION forbid_mutation();

CREATE OR REPLACE TRIGGER money_line_no_mutation
    BEFORE UPDATE OR DELETE ON money_journal_line
    FOR EACH ROW EXECUTE FUNCTION forbid_mutation();

-- Apply Deferred Constraint Triggers for Commit-Time Balance Enforcement
DROP TRIGGER IF EXISTS trg_gold_line_balanced ON gold_journal_line;
CREATE CONSTRAINT TRIGGER trg_gold_line_balanced
    AFTER INSERT ON gold_journal_line
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION check_gold_entry_balanced();

DROP TRIGGER IF EXISTS trg_money_line_balanced ON money_journal_line;
CREATE CONSTRAINT TRIGGER trg_money_line_balanced
    AFTER INSERT ON money_journal_line
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION check_money_entry_balanced();

-- ============================================================================
-- 8. ROW LEVEL SECURITY (RLS) FOR TENANT ISOLATION
-- ============================================================================
ALTER TABLE staff ENABLE ROW LEVEL SECURITY;
ALTER TABLE staff FORCE ROW LEVEL SECURITY;
CREATE POLICY staff_tenant_isolation ON staff
    USING (shop_id = current_setting('app.shop_id', TRUE)::uuid);

ALTER TABLE instrument ENABLE ROW LEVEL SECURITY;
ALTER TABLE instrument FORCE ROW LEVEL SECURITY;
CREATE POLICY instrument_tenant_isolation ON instrument
    USING (shop_id = current_setting('app.shop_id', TRUE)::uuid);

ALTER TABLE exchange ENABLE ROW LEVEL SECURITY;
ALTER TABLE exchange FORCE ROW LEVEL SECURITY;
CREATE POLICY exchange_tenant_isolation ON exchange
    USING (shop_id = current_setting('app.shop_id', TRUE)::uuid);

ALTER TABLE reading ENABLE ROW LEVEL SECURITY;
ALTER TABLE reading FORCE ROW LEVEL SECURITY;
CREATE POLICY reading_tenant_isolation ON reading
    USING (shop_id = current_setting('app.shop_id', TRUE)::uuid);

ALTER TABLE weight_witness ENABLE ROW LEVEL SECURITY;
ALTER TABLE weight_witness FORCE ROW LEVEL SECURITY;
CREATE POLICY witness_tenant_isolation ON weight_witness
    USING (shop_id = current_setting('app.shop_id', TRUE)::uuid);

ALTER TABLE receipt ENABLE ROW LEVEL SECURITY;
ALTER TABLE receipt FORCE ROW LEVEL SECURITY;
CREATE POLICY receipt_tenant_isolation ON receipt
    USING (shop_id = current_setting('app.shop_id', TRUE)::uuid);

ALTER TABLE audit_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_event FORCE ROW LEVEL SECURITY;
CREATE POLICY audit_tenant_isolation ON audit_event
    USING (shop_id = current_setting('app.shop_id', TRUE)::uuid);

ALTER TABLE gold_journal_entry ENABLE ROW LEVEL SECURITY;
ALTER TABLE gold_journal_entry FORCE ROW LEVEL SECURITY;
CREATE POLICY gold_entry_tenant_isolation ON gold_journal_entry
    USING (shop_id = current_setting('app.shop_id', TRUE)::uuid);

ALTER TABLE gold_journal_line ENABLE ROW LEVEL SECURITY;
ALTER TABLE gold_journal_line FORCE ROW LEVEL SECURITY;
CREATE POLICY gold_line_tenant_isolation ON gold_journal_line
    USING (shop_id = current_setting('app.shop_id', TRUE)::uuid);

ALTER TABLE money_journal_entry ENABLE ROW LEVEL SECURITY;
ALTER TABLE money_journal_entry FORCE ROW LEVEL SECURITY;
CREATE POLICY money_entry_tenant_isolation ON money_journal_entry
    USING (shop_id = current_setting('app.shop_id', TRUE)::uuid);

ALTER TABLE money_journal_line ENABLE ROW LEVEL SECURITY;
ALTER TABLE money_journal_line FORCE ROW LEVEL SECURITY;
CREATE POLICY money_line_tenant_isolation ON money_journal_line
    USING (shop_id = current_setting('app.shop_id', TRUE)::uuid);
