-- Migration 002: Dosen Survey Flow + Role Scoping
-- Jalankan di VPS: psql -U sinoku_user -d sinoku_db -f migrations/002_dosen_flow.sql

BEGIN;

-- 1. Tambah kolom user_id di responses (nullable, untuk dosen)
ALTER TABLE responses
  ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE SET NULL;

-- 2. Buat respondent_id nullable (dosen tidak punya respondent anonim)
ALTER TABLE responses
  ALTER COLUMN respondent_id DROP NOT NULL;

-- 3. Index untuk query dosen
CREATE INDEX IF NOT EXISTS idx_responses_user_id ON responses(user_id);

-- 4. Constraint: salah satu harus terisi (user_id untuk dosen, respondent_id untuk mahasiswa)
ALTER TABLE responses
  ADD CONSTRAINT chk_responses_identity
  CHECK (user_id IS NOT NULL OR respondent_id IS NOT NULL);

COMMIT;
