-- =============================================================================
-- Migration 006: Seed akun Superadmin default
-- Membuat satu akun superadmin agar fresh deploy langsung bisa login.
-- Idempotent: hanya membuat jika BELUM ADA user dengan role 'superadmin',
-- sehingga aman pada VPS yang sudah memiliki superadmin (menjadi no-op).
--
-- Password di-hash dengan bcrypt via pgcrypto crypt()/gen_salt('bf'),
-- kompatibel dengan bcrypt.checkpw() yang dipakai aplikasi.
--
-- AKUN DEFAULT:
--   email    : superadmin@sinoku.ac.id
--   password : admin123
-- >> WAJIB ganti password setelah login pertama di lingkungan produksi. <<
-- =============================================================================

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO users (email, full_name, hashed_password, role, is_active)
SELECT
    'superadmin@sinoku.ac.id',
    'Super Administrator',
    crypt('admin123', gen_salt('bf')),
    'superadmin',
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE role = 'superadmin'
);

COMMIT;
