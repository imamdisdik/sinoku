-- =============================================================================
-- Migration 010: Tingkat Fakultas + restrukturisasi peran (5 aktor)
--
-- 1. Tabel `faculties` (Universitas → Fakultas → Prodi).
-- 2. Kolom `programs.faculty_id` (prodi ditautkan ke fakultas, nullable).
-- 3. Kolom `users.faculty_id` (scoping Admin Fakultas).
-- 4. Migrasi peran: 'admin' lama → 'admin_universitas'.
--    Peran final: superadmin | admin_universitas | admin_fakultas | admin_prodi | dosen
--
-- Idempotent: IF NOT EXISTS + UPDATE bersyarat. Aman dijalankan berulang.
-- =============================================================================

BEGIN;

-- 1. Tabel fakultas ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS faculties (
    id              SERIAL PRIMARY KEY,
    university_id   INTEGER NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    nama            VARCHAR(200) NOT NULL,
    nama_singkat    VARCHAR(20)  NOT NULL,
    rumpun_keilmuan VARCHAR(200),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_faculties_university_id ON faculties(university_id);

-- 2. programs.faculty_id -----------------------------------------------------
ALTER TABLE programs ADD COLUMN IF NOT EXISTS faculty_id INTEGER
    REFERENCES faculties(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_programs_faculty_id ON programs(faculty_id);

-- 3. users.faculty_id --------------------------------------------------------
ALTER TABLE users ADD COLUMN IF NOT EXISTS faculty_id INTEGER
    REFERENCES faculties(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_users_faculty_id ON users(faculty_id);

-- 4. Migrasi peran 'admin' lama → 'admin_universitas' ------------------------
UPDATE users SET role = 'admin_universitas' WHERE role = 'admin';

COMMIT;
