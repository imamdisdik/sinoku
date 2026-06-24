-- =============================================================================
-- Migration 012: Dosen pengampu yang dievaluasi pada respons mahasiswa
--
-- Mahasiswa memilih dosen pengampu mana yang sedang dievaluasi (bila MK punya
-- pengampu). Disimpan di responses.evaluated_lecturer_id (FK users, nullable).
--
-- Idempotent: ADD COLUMN IF NOT EXISTS.
-- =============================================================================

BEGIN;

ALTER TABLE responses ADD COLUMN IF NOT EXISTS evaluated_lecturer_id UUID
    REFERENCES users(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_responses_evaluated_lecturer_id ON responses(evaluated_lecturer_id);

COMMIT;
