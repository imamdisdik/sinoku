-- =============================================================================
-- Migration 009: Koreksi nama 15 subdimensi sesuai instrumen asli
-- (Data kuisioner.xlsx) & template laporan CIPP.
--
-- Nama lama (dari seed awal) tidak sesuai konten item. Contoh: B.1 berisi
-- item penilaian kebutuhan (CD1.x) tapi diberi nama "Relevansi Kurikulum".
-- Idempotent: UPDATE by kode.
-- =============================================================================

BEGIN;

UPDATE cipp_sub_dimensions SET nama_id = 'Penilaian Kebutuhan'                    WHERE kode = 'B.1';
UPDATE cipp_sub_dimensions SET nama_id = 'Relevansi dan Keselarasan'             WHERE kode = 'B.2';
UPDATE cipp_sub_dimensions SET nama_id = 'Dukungan Institusional'                WHERE kode = 'B.3';
UPDATE cipp_sub_dimensions SET nama_id = 'Kompetensi Dosen'                      WHERE kode = 'C.1';
UPDATE cipp_sub_dimensions SET nama_id = 'Kurikulum dan Silabus'                 WHERE kode = 'C.2';
UPDATE cipp_sub_dimensions SET nama_id = 'Sumber Belajar dan Fasilitas'          WHERE kode = 'C.3';
UPDATE cipp_sub_dimensions SET nama_id = 'Kesiapan Mahasiswa'                    WHERE kode = 'C.4';
UPDATE cipp_sub_dimensions SET nama_id = 'Metodologi Pengajaran'                 WHERE kode = 'D.1';
UPDATE cipp_sub_dimensions SET nama_id = 'Interaksi di Kelas'                    WHERE kode = 'D.2';
UPDATE cipp_sub_dimensions SET nama_id = 'Imersi dan Pembelajaran Eksperiensial' WHERE kode = 'D.3';
UPDATE cipp_sub_dimensions SET nama_id = 'Sistem Penilaian dan Umpan Balik'      WHERE kode = 'D.4';
UPDATE cipp_sub_dimensions SET nama_id = 'Perolehan Pengetahuan dan Kompetensi'  WHERE kode = 'E.1';
UPDATE cipp_sub_dimensions SET nama_id = 'Efektivitas Program'                   WHERE kode = 'E.2';
UPDATE cipp_sub_dimensions SET nama_id = 'Dampak dan Reputasi'                   WHERE kode = 'E.3';
UPDATE cipp_sub_dimensions SET nama_id = 'Refleksi dan Kepuasan'                 WHERE kode = 'E.4';

COMMIT;
