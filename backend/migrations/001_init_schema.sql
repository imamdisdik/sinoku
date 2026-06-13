-- =============================================================================
-- Migration 001: Skema Inti SINOKU (base schema)
-- Membuat seluruh tabel inti sesuai model SQLAlchemy & ERD.
-- Idempotent (CREATE TABLE IF NOT EXISTS) — aman dijalankan ulang pada DB
-- yang sudah berisi tabel maupun pada database kosong (fresh deploy).
--
-- Urutan migrasi: 001 (skema inti) → 002 (kolom dosen) → 003 (RPS)
--                 → 004 (seed instrumen) → 005 (asesmen & laporan)
-- =============================================================================

BEGIN;

-- Ekstensi untuk gen_random_uuid() (PostgreSQL 13+ menyediakannya via pgcrypto)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ── AKADEMIK ─────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS universities (
    id              SERIAL PRIMARY KEY,
    nama            VARCHAR(200) NOT NULL,
    nama_singkat    VARCHAR(20)  NOT NULL,
    jenis           VARCHAR(50)  NOT NULL,
    kota            VARCHAR(100) NOT NULL,
    provinsi        VARCHAR(100) NOT NULL,
    website         VARCHAR(255),
    akreditasi      VARCHAR(10),
    tahun_berdiri   SMALLINT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS programs (
    id              SERIAL PRIMARY KEY,
    university_id   INTEGER NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    nama            VARCHAR(200) NOT NULL,
    nama_singkat    VARCHAR(20)  NOT NULL,
    jenjang         VARCHAR(10)  NOT NULL,
    tahun_berdiri   SMALLINT,
    akreditasi      VARCHAR(10),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS courses (
    id              SERIAL PRIMARY KEY,
    program_id      INTEGER NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    kode_mk         VARCHAR(20)  NOT NULL,
    nama_id         VARCHAR(200) NOT NULL,
    nama_zh         VARCHAR(200) NOT NULL,
    sks             SMALLINT NOT NULL,
    semester        SMALLINT NOT NULL,
    status_mk       VARCHAR(20) NOT NULL DEFAULT 'wajib',
    deskripsi       TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cpls (
    id              SERIAL PRIMARY KEY,
    program_id      INTEGER NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    kode_cpl        VARCHAR(20) NOT NULL,
    deskripsi_id    TEXT NOT NULL,
    deskripsi_zh    TEXT NOT NULL,
    kategori        VARCHAR(50) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cpmks (
    id              SERIAL PRIMARY KEY,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    kode_cpmk       VARCHAR(20) NOT NULL,
    deskripsi_id    TEXT NOT NULL,
    deskripsi_zh    TEXT NOT NULL,
    bobot_persen    DOUBLE PRECISION NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS course_cpl_mapping (
    id              SERIAL PRIMARY KEY,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    cpl_id          INTEGER NOT NULL REFERENCES cpls(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cpmk_cpl_mapping (
    id              SERIAL PRIMARY KEY,
    cpmk_id         INTEGER NOT NULL REFERENCES cpmks(id) ON DELETE CASCADE,
    cpl_id          INTEGER NOT NULL REFERENCES cpls(id) ON DELETE CASCADE
);

-- ── AUTH ─────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    full_name       VARCHAR(200) NOT NULL,
    hashed_password TEXT NOT NULL,
    role            VARCHAR(20) NOT NULL,
    university_id   INTEGER REFERENCES universities(id) ON DELETE SET NULL,
    program_id      INTEGER REFERENCES programs(id) ON DELETE SET NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_login      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
    id              SERIAL PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token   TEXT NOT NULL UNIQUE,
    expires_at      TIMESTAMPTZ NOT NULL,
    is_revoked      BOOLEAN NOT NULL DEFAULT FALSE,
    ip_address      VARCHAR(45),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── INSTRUMEN CIPP ───────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS cipp_dimensions (
    id              SERIAL PRIMARY KEY,
    kode            CHAR(1) NOT NULL UNIQUE,
    nama_dimensi    VARCHAR(50)  NOT NULL,
    nama_id         VARCHAR(100) NOT NULL,
    nama_zh         VARCHAR(100) NOT NULL,
    deskripsi_id    TEXT NOT NULL,
    urutan          SMALLINT NOT NULL,
    warna_hex       VARCHAR(7) NOT NULL
);

CREATE TABLE IF NOT EXISTS cipp_sub_dimensions (
    id              SERIAL PRIMARY KEY,
    dimension_id    INTEGER NOT NULL REFERENCES cipp_dimensions(id) ON DELETE CASCADE,
    kode            VARCHAR(10) NOT NULL UNIQUE,
    nama_id         VARCHAR(200) NOT NULL,
    nama_zh         VARCHAR(200) NOT NULL,
    urutan          SMALLINT NOT NULL
);

CREATE TABLE IF NOT EXISTS instrument_items (
    id                   SERIAL PRIMARY KEY,
    sub_dimension_id     INTEGER NOT NULL REFERENCES cipp_sub_dimensions(id) ON DELETE CASCADE,
    kode                 VARCHAR(10) NOT NULL UNIQUE,
    nomor_urut           SMALLINT NOT NULL,
    text_id_dosen        TEXT NOT NULL,
    text_id_mahasiswa    TEXT NOT NULL,
    text_zh_dosen        TEXT NOT NULL,
    text_zh_mahasiswa    TEXT NOT NULL,
    indikator            VARCHAR(200),
    kompetensi_dosen     VARCHAR(200),
    kompetensi_mahasiswa VARCHAR(200),
    answer_type          VARCHAR(20) NOT NULL DEFAULT 'likert',
    scale_min            SMALLINT NOT NULL DEFAULT 1,
    scale_max            SMALLINT NOT NULL DEFAULT 5,
    is_required          BOOLEAN NOT NULL DEFAULT TRUE,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS open_questions (
    id              SERIAL PRIMARY KEY,
    kode            VARCHAR(10) NOT NULL UNIQUE,
    pertanyaan_id   TEXT NOT NULL,
    pertanyaan_zh   TEXT NOT NULL,
    tujuan          VARCHAR(200) NOT NULL,
    target_role     VARCHAR(20) NOT NULL,
    is_required     BOOLEAN NOT NULL DEFAULT FALSE,
    urutan          SMALLINT NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

-- ── RESPONDEN (profil dosen & mahasiswa + junction multi-pilih) ───────────────

CREATE TABLE IF NOT EXISTS respondents (
    id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role                      VARCHAR(20) NOT NULL,
    full_name                 VARCHAR(200),
    university_id             INTEGER NOT NULL REFERENCES universities(id) ON DELETE RESTRICT,
    faculty                   VARCHAR(200),
    program_id                INTEGER REFERENCES programs(id) ON DELETE SET NULL,
    academic_position         VARCHAR(100),
    teaching_duration         VARCHAR(50),
    education_level           VARCHAR(20),
    china_experience_dosen    VARCHAR(50),
    hsk_level_dosen           VARCHAR(10),
    avg_class_size            VARCHAR(20),
    gender                    VARCHAR(20),
    age                       SMALLINT,
    current_semester          SMALLINT,
    mandarin_study_duration   VARCHAR(50),
    hsk_level_mahasiswa       VARCHAR(10),
    china_stay_duration       VARCHAR(50),
    chinese_friends           VARCHAR(50),
    has_taken_culture_course  BOOLEAN,
    culture_course_count      VARCHAR(20),
    course_status_taken       VARCHAR(50),
    cultural_interaction_freq VARCHAR(50),
    created_at                TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS respondent_course_taught (
    id              SERIAL PRIMARY KEY,
    respondent_id   UUID NOT NULL REFERENCES respondents(id) ON DELETE CASCADE,
    course_name     VARCHAR(200) NOT NULL,
    course_id       INTEGER REFERENCES courses(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS respondent_course_taken (
    id              SERIAL PRIMARY KEY,
    respondent_id   UUID NOT NULL REFERENCES respondents(id) ON DELETE CASCADE,
    course_name     VARCHAR(200) NOT NULL,
    course_id       INTEGER REFERENCES courses(id) ON DELETE SET NULL,
    semester_taken  SMALLINT,
    final_grade     VARCHAR(5)
);

CREATE TABLE IF NOT EXISTS respondent_motivations (
    id              SERIAL PRIMARY KEY,
    respondent_id   UUID NOT NULL REFERENCES respondents(id) ON DELETE CASCADE,
    motivasi        VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS respondent_career_goals (
    id              SERIAL PRIMARY KEY,
    respondent_id   UUID NOT NULL REFERENCES respondents(id) ON DELETE CASCADE,
    bidang_karir    VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS respondent_media_usage (
    id              SERIAL PRIMARY KEY,
    respondent_id   UUID NOT NULL REFERENCES respondents(id) ON DELETE CASCADE,
    media           VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS respondent_activities (
    id              SERIAL PRIMARY KEY,
    respondent_id   UUID NOT NULL REFERENCES respondents(id) ON DELETE CASCADE,
    aktivitas       VARCHAR(200) NOT NULL
);

-- ── RESPONS & KODE ANONIM ────────────────────────────────────────────────────
-- Catatan: kolom user_id ditambahkan di sini agar fresh deploy langsung benar.
-- Migration 002 (ADD COLUMN IF NOT EXISTS user_id) menjadi no-op yang aman.

CREATE TABLE IF NOT EXISTS responses (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    respondent_id       UUID REFERENCES respondents(id) ON DELETE RESTRICT,
    user_id             UUID REFERENCES users(id) ON DELETE SET NULL,
    course_id           INTEGER NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    instrument_version  VARCHAR(20) NOT NULL DEFAULT '1.0',
    role                VARCHAR(20) NOT NULL,
    bahasa              VARCHAR(5) NOT NULL,
    is_complete         BOOLEAN NOT NULL DEFAULT FALSE,
    submitted_at        TIMESTAMPTZ,
    ip_hash             VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS response_items (
    id              BIGSERIAL PRIMARY KEY,
    response_id     UUID NOT NULL REFERENCES responses(id) ON DELETE CASCADE,
    item_id         INTEGER NOT NULL REFERENCES instrument_items(id) ON DELETE RESTRICT,
    skor            SMALLINT NOT NULL,
    answered_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_response_item UNIQUE (response_id, item_id)
);

CREATE TABLE IF NOT EXISTS response_open_answers (
    id               BIGSERIAL PRIMARY KEY,
    response_id      UUID NOT NULL REFERENCES responses(id) ON DELETE CASCADE,
    open_question_id INTEGER NOT NULL REFERENCES open_questions(id) ON DELETE RESTRICT,
    jawaban_teks     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS anonymous_codes (
    id              SERIAL PRIMARY KEY,
    kode            VARCHAR(20) NOT NULL UNIQUE,
    response_id     UUID NOT NULL UNIQUE REFERENCES responses(id) ON DELETE CASCADE,
    is_accessible   BOOLEAN NOT NULL DEFAULT TRUE,
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_accessed   TIMESTAMPTZ
);

-- ── INDEX untuk query panas (scoping & lookup) ───────────────────────────────

CREATE INDEX IF NOT EXISTS idx_programs_university   ON programs(university_id);
CREATE INDEX IF NOT EXISTS idx_courses_program       ON courses(program_id);
CREATE INDEX IF NOT EXISTS idx_cpls_program          ON cpls(program_id);
CREATE INDEX IF NOT EXISTS idx_cpmks_course          ON cpmks(course_id);
CREATE INDEX IF NOT EXISTS idx_subdim_dimension      ON cipp_sub_dimensions(dimension_id);
CREATE INDEX IF NOT EXISTS idx_items_subdim          ON instrument_items(sub_dimension_id);
CREATE INDEX IF NOT EXISTS idx_respondents_univ      ON respondents(university_id);
CREATE INDEX IF NOT EXISTS idx_responses_course      ON responses(course_id);
CREATE INDEX IF NOT EXISTS idx_responses_respondent  ON responses(respondent_id);
CREATE INDEX IF NOT EXISTS idx_response_items_resp   ON response_items(response_id);
CREATE INDEX IF NOT EXISTS idx_response_items_item   ON response_items(item_id);
CREATE INDEX IF NOT EXISTS idx_open_answers_resp     ON response_open_answers(response_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user         ON sessions(user_id);

COMMIT;
