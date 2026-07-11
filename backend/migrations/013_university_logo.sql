-- =============================================================================
-- Migration 013: Logo per Universitas
--
-- Simpan logo sebagai data URI (base64) di kolom TEXT — tanpa perlu penyimpanan
-- file/CDN. Ditampilkan di sidebar, kop laporan, dan halaman survei.
--
-- Idempotent: ADD COLUMN IF NOT EXISTS.
-- =============================================================================

BEGIN;

ALTER TABLE universities ADD COLUMN IF NOT EXISTS logo_url TEXT;

COMMIT;
