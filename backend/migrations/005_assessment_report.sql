-- Migration 005: Assessment Scheme, Rubrik, MBKM, dan Diagnostic Report
BEGIN;

-- UC-14j: Skema Penilaian
CREATE TABLE IF NOT EXISTS assessment_schemes (
    id              SERIAL PRIMARY KEY,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    rps_version_id  INTEGER REFERENCES rps_versions(id) ON DELETE SET NULL,
    nama_komponen   VARCHAR(200) NOT NULL,
    tipe            VARCHAR(50) NOT NULL,
    bobot_persen    NUMERIC(5,2) NOT NULL,
    deskripsi       TEXT
);

-- UC-14k: Rubrik Penilaian
CREATE TABLE IF NOT EXISTS assessment_rubrics (
    id                   SERIAL PRIMARY KEY,
    assessment_scheme_id INTEGER NOT NULL REFERENCES assessment_schemes(id) ON DELETE CASCADE,
    cpmk_id              INTEGER NOT NULL REFERENCES cpmks(id) ON DELETE CASCADE,
    level                VARCHAR(20) NOT NULL,
    skor_min             NUMERIC(5,2) NOT NULL,
    skor_max             NUMERIC(5,2) NOT NULL,
    deskriptor           TEXT NOT NULL
);

-- UC-14l: Integrasi MBKM
CREATE TABLE IF NOT EXISTS mbkm_integrations (
    id              SERIAL PRIMARY KEY,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    jenis_program   VARCHAR(100) NOT NULL,
    nama_mitra      VARCHAR(200) NOT NULL,
    deskripsi       TEXT,
    sks_diakui      SMALLINT NOT NULL,
    tahun_akademik  VARCHAR(10) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

-- UC-19: Laporan Diagnostik
CREATE TABLE IF NOT EXISTS diagnostic_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generated_by    UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    university_id   INTEGER NOT NULL REFERENCES universities(id) ON DELETE RESTRICT,
    program_id      INTEGER NOT NULL REFERENCES programs(id) ON DELETE RESTRICT,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    periode_start   DATE NOT NULL,
    periode_end     DATE NOT NULL,
    title           VARCHAR(300) NOT NULL,
    snapshot_json   JSONB NOT NULL DEFAULT '{}',
    pdf_url         VARCHAR(500),
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_diagnostic_reports_course ON diagnostic_reports(course_id);
CREATE INDEX IF NOT EXISTS idx_diagnostic_reports_university ON diagnostic_reports(university_id);
CREATE INDEX IF NOT EXISTS idx_assessment_schemes_course ON assessment_schemes(course_id);
CREATE INDEX IF NOT EXISTS idx_assessment_rubrics_scheme ON assessment_rubrics(assessment_scheme_id);
CREATE INDEX IF NOT EXISTS idx_mbkm_course ON mbkm_integrations(course_id);

COMMIT;
