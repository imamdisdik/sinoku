-- =============================================================================
-- Migration 008: Riwayat Perubahan Item Instrumen (F-09.4 Versioning Item)
-- Menyimpan snapshot item sebelum setiap perubahan (audit trail).
-- Idempotent.
-- =============================================================================

BEGIN;

-- item_id dibuat nullable + ON DELETE SET NULL agar riwayat (termasuk aksi
-- delete) tetap tersimpan sebagai audit meski item-nya dihapus.
CREATE TABLE IF NOT EXISTS instrument_item_history (
    id           BIGSERIAL PRIMARY KEY,
    item_id      INTEGER REFERENCES instrument_items(id) ON DELETE SET NULL,
    snapshot     JSONB NOT NULL,          -- kondisi item SEBELUM diubah
    action       VARCHAR(20) NOT NULL,    -- update | delete
    changed_by   UUID REFERENCES users(id) ON DELETE SET NULL,
    changed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_item_history_item ON instrument_item_history(item_id);

COMMIT;
