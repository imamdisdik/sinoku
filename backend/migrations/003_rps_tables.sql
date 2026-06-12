-- Migration 003: RPS tables
BEGIN;

CREATE TABLE IF NOT EXISTS rps_versions (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    tahun_akademik VARCHAR(10) NOT NULL,
    semester VARCHAR(10) NOT NULL,
    status VARCHAR(10) NOT NULL DEFAULT 'draft',
    file_url VARCHAR(500),
    catatan TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rps_versions_course ON rps_versions(course_id);

CREATE TABLE IF NOT EXISTS rps_checklist_items (
    id SERIAL PRIMARY KEY,
    kode VARCHAR(10) UNIQUE NOT NULL,
    nama_komponen VARCHAR(200) NOT NULL,
    deskripsi TEXT,
    is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
    urutan SMALLINT NOT NULL
);

CREATE TABLE IF NOT EXISTS rps_checklist_responses (
    id SERIAL PRIMARY KEY,
    rps_version_id INTEGER NOT NULL REFERENCES rps_versions(id) ON DELETE CASCADE,
    checklist_item_id INTEGER NOT NULL REFERENCES rps_checklist_items(id) ON DELETE RESTRICT,
    is_fulfilled BOOLEAN NOT NULL DEFAULT FALSE,
    catatan TEXT,
    checked_by UUID REFERENCES users(id) ON DELETE SET NULL,
    checked_at TIMESTAMPTZ
);

-- Seed data: komponen standar checklist RPS MBKM
INSERT INTO rps_checklist_items (kode, nama_komponen, deskripsi, is_mandatory, urutan)
VALUES
  ('RPS-01', 'Identitas Mata Kuliah', 'Nama MK, kode, SKS, semester, program studi', TRUE, 1),
  ('RPS-02', 'Deskripsi Singkat MK', 'Gambaran umum tentang mata kuliah', TRUE, 2),
  ('RPS-03', 'Capaian Pembelajaran Lulusan (CPL)', 'CPL yang dibebankan pada MK ini', TRUE, 3),
  ('RPS-04', 'Capaian Pembelajaran MK (CPMK)', 'CPMK yang diturunkan dari CPL', TRUE, 4),
  ('RPS-05', 'Bahan Kajian/Materi Pembelajaran', 'Topik-topik yang akan dipelajari', TRUE, 5),
  ('RPS-06', 'Metode Pembelajaran', 'Pendekatan dan metode yang digunakan', TRUE, 6),
  ('RPS-07', 'Waktu/Jadwal Pembelajaran', 'Alokasi waktu per pertemuan', TRUE, 7),
  ('RPS-08', 'Pengalaman Belajar Mahasiswa', 'Aktivitas belajar yang dirancang', FALSE, 8),
  ('RPS-09', 'Kriteria & Indikator Penilaian', 'Rubrik dan indikator pencapaian', TRUE, 9),
  ('RPS-10', 'Bobot Penilaian', 'Persentase setiap komponen penilaian', TRUE, 10),
  ('RPS-11', 'Referensi/Pustaka', 'Daftar referensi yang digunakan', TRUE, 11),
  ('RPS-12', 'Integrasi Budaya Tiongkok', 'Konten budaya Tiongkok yang terintegrasi dalam MK', TRUE, 12),
  ('RPS-13', 'Komponen MBKM (jika ada)', 'Keterkaitan dengan program MBKM', FALSE, 13)
ON CONFLICT (kode) DO NOTHING;

COMMIT;
