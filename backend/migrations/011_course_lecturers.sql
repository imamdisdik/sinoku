-- =============================================================================
-- Migration 011: Dosen Pengampu per Mata Kuliah (many-to-many)
--
-- Tabel pemetaan course_lecturers: satu MK bisa diampu banyak dosen, satu dosen
-- bisa mengampu banyak MK. Dikelola Admin Prodi (scope prodi).
--
-- Idempotent: IF NOT EXISTS + UNIQUE(course_id, user_id).
-- =============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS course_lecturers (
    id         SERIAL PRIMARY KEY,
    course_id  INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    user_id    UUID    NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    UNIQUE (course_id, user_id)
);
CREATE INDEX IF NOT EXISTS ix_course_lecturers_course_id ON course_lecturers(course_id);
CREATE INDEX IF NOT EXISTS ix_course_lecturers_user_id   ON course_lecturers(user_id);

COMMIT;
