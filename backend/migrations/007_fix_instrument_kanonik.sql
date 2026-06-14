-- =============================================================================
-- Migration 007: Perbaiki instrumen ke set kanonik (59 item)
--
-- Masalah: DB berisi 93 item = 58 item kanonik (kode CD/ID/PD/RD, sesuai
-- "Data kuisioner.xlsx") + 35 item keliru (kode B1..E.., dari seed migrasi 004
-- lama). Survei jadi menampilkan 93 item, bukan 59.
--
-- Perbaikan (non-destruktif):
--   1. Non-aktifkan 35 item keliru (is_active=false) — data tidak dihapus.
--   2. Tambah 1 item kanonik yang hilang: RD3.4 (sub-dimensi E.3).
-- Hasil akhir: 59 item aktif sesuai instrumen tervalidasi.
--
-- Idempotent: aman dijalankan ulang.
-- Catatan: teks Mandarin (ZH) RD3.4 belum tersedia di sumber → diisi kosong,
--          lengkapi kemudian lewat menu admin Instrumen.
-- =============================================================================

BEGIN;

-- 1. Non-aktifkan item keliru berkode B1.., C1.., D1.., E1.. (bukan CD/ID/PD/RD)
UPDATE instrument_items
SET is_active = false
WHERE kode ~ '^[BCDE][0-9]';

-- 2. Tambahkan item kanonik yang hilang: RD3.4 pada sub-dimensi E.3
INSERT INTO instrument_items
    (sub_dimension_id, kode, nomor_urut,
     text_id_dosen, text_id_mahasiswa, text_zh_dosen, text_zh_mahasiswa,
     indikator, kompetensi_dosen, kompetensi_mahasiswa,
     answer_type, scale_min, scale_max, is_required, is_active)
SELECT sd.id, 'RD3.4', 54,
    'Kursus ini berkontribusi pada pengembangan kemitraan internasional institusi',
    'Pengetahuan dari kelas ini membuka peluang bagi saya untuk terlibat dalam kegiatan bertaraf internasional (seperti beasiswa/pertukaran pelajar).',
    '', '',
    'International partnership',
    'Pencapaian hasil dan refleksi pengajar',
    'Pencapaian hasil belajar',
    'likert', 1, 5, TRUE, TRUE
FROM cipp_sub_dimensions sd
WHERE sd.kode = 'E.3'
  AND NOT EXISTS (SELECT 1 FROM instrument_items WHERE kode = 'RD3.4');

COMMIT;
