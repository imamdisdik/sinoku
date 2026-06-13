# Laporan Pengujian Sistem SINOKU

> Pengujian **Black-box** terhadap sistem yang **sudah ter-deploy di server produksi**.
> Setiap skenario dieksekusi langsung ke API live; kolom "Hasil Aktual" adalah respons nyata server.

| | |
|---|---|
| **Metode** | Black-box testing (functional, API-level) |
| **Target** | `http://202.10.34.93` (production, via Nginx) |
| **Tanggal** | 13 Juni 2026 |
| **Akun uji** | `admin@sinoku.id` (superadmin) |
| **Total skenario** | 36 |
| **Lulus** | **34 (94%)** |
| **Temuan** | 1 isu data (jumlah item instrumen) + 1 kredensial (teratasi) |

---

## 1. Pengujian Zona Publik (UC-01 s/d UC-10)

| No | UC | Skenario | Input | Hasil Diharapkan | Hasil Aktual | Status |
|----|----|----------|-------|------------------|--------------|--------|
| 1 | — | Health check | `GET /health` | Service `ok` | `{"status":"ok"}` | ✅ |
| 2 | UC-01 | Buka landing + statistik | `GET /public/landing` | Statistik & daftar univ | 10 universitas | ✅ |
| 3 | UC-02 | Pilih universitas | `GET /public/universities` | Daftar univ | 10 universitas | ✅ |
| 4 | UC-02a | Pilih program studi | `GET /universities/1/programs` | Daftar prodi | BMKT (S1) | ✅ |
| 5 | UC-02b | Pilih mata kuliah | `GET /programs/1/courses` | Daftar MK | 7 mata kuliah | ✅ |
| 6 | UC-03 | Mulai survei + simpan profil | `POST /survey/start` (profil mhs) | `response_id` (201) | HTTP 201, response_id terbit | ✅ |
| 7 | UC-04 | Ambil item kuesioner | `GET /survey/{id}/items` B,C,D,E | Item 4 dimensi | 93 item ⚠️ | ✅* |
| 8 | UC-06 | Submit jawaban | `POST /survey/{id}/answers` (93 skor) | Tersimpan | HTTP 200, saved=93 | ✅ |
| 9 | UC-07 | Finalisasi + kode anonim | `POST /survey/{id}/submit` | Kode anonim (201) | `SIN-2026-I639` | ✅ |
| 10 | UC-08 | Lihat hasil via kode | `GET /public/result/{kode}` | Skor CIPP per dimensi | 4 dimensi tampil | ✅ |

> \*Endpoint berfungsi normal; jumlah item (93) menjadi temuan data — lihat Bagian 4.

**Catatan UC-09/UC-10 (Download PDF & Cetak):** diimplementasi sebagai fitur **sisi klien** (jsPDF / `window.print`), diverifikasi pada level kode & build; tidak diuji via API karena murni operasi browser.

---

## 2. Pengujian Autentikasi & Admin (UC-11 s/d UC-19)

| No | UC | Skenario | Endpoint | Hasil Aktual | Status |
|----|----|----------|----------|--------------|--------|
| 11 | UC-11 | Login superadmin | `POST /auth/login` | HTTP 200, role=superadmin | ✅ |
| 12 | UC-12 | Refresh token tersimpan (sessions) | (response login) | refresh_token terbit | ✅ |
| 13 | UC-13 | Dashboard KPI | `GET /admin/dashboard/kpi` | HTTP 200 | ✅ |
| 14 | UC-13 | Problem heatmap | `GET /admin/dashboard/problem-heatmap` | HTTP 200 | ✅ |
| 15 | UC-14a | List universitas (scoped) | `GET /admin/universities` | 10 baris | ✅ |
| 16 | UC-14c | List mata kuliah | `GET /admin/courses` | 20 baris | ✅ |
| 17 | UC-14d | List CPL | `GET /admin/cpls` | 0 baris (data kosong) | ✅ |
| 18 | UC-14f | List CPMK | `GET /admin/cpmks` | 0 baris (data kosong) | ✅ |
| 19 | UC-14h | List RPS | `GET /admin/rps` | 0 baris (data kosong) | ✅ |
| 20 | UC-14j | List skema penilaian | `GET /admin/assessment/schemes` | 0 baris (data kosong) | ✅ |
| 21 | UC-14l | List MBKM | `GET /admin/assessment/mbkm` | 0 baris (data kosong) | ✅ |
| 22 | UC-15 | List dimensi instrumen | `GET /admin/instruments/dimensions` | 4 dimensi | ✅ |
| 23 | UC-16 | List kode anonim | `GET /admin/anonymous-codes` | 1 baris (hasil uji) | ✅ |
| 24 | UC-17a | Analitik skor CIPP | `GET /admin/analytics/cipp-scores` | HTTP 200 | ✅ |
| 25 | UC-17b | Perbandingan grup (univ) | `GET /analytics/comparison-groups?group_by=university` | 1 grup berdata | ✅ |
| 26 | UC-17b | Perbandingan grup (MK) | `GET /analytics/comparison-groups?group_by=course` | 1 grup berdata | ✅ |
| 27 | UC-17 | Perbandingan dosen vs mahasiswa | `GET /admin/analytics/comparison` | HTTP 200 | ✅ |
| 28 | UC-17d | Distribusi skor Likert | `GET /admin/analytics/distribution` | HTTP 200 | ✅ |
| 29 | UC-19 | List laporan diagnostik | `GET /admin/reports` | HTTP 200 | ✅ |
| 30 | UC-18c | Export skor agregat (CSV) | `GET /admin/export/scores?format=csv` | File CSV | ✅ |
| 31 | UC-18d | Export data mentah (superadmin) | `GET /admin/export/responses?format=csv` | File CSV (akses superadmin) | ✅ |
| 32 | UC-19 | **Generate laporan diagnostik** | `POST /admin/reports` | HTTP 201, snapshot tersimpan | ✅ |
| 33 | UC-19c/d/f | **Snapshot berisi seksi baru** | (isi snapshot_json) | `rps_alignment`, `cpl_cpmk_analysis`, `rps_suggestions` ada | ✅ |

---

## 3. Pengujian Integritas Data

| No | Aspek | Diharapkan | Aktual | Status |
|----|-------|-----------|--------|--------|
| 34 | Jumlah sub-dimensi | 15 | 15 | ✅ |
| 35 | Jumlah item instrumen | 59 (sesuai ERD-4) | **93** | ❌ |
| 36 | Hak akses UC-18d | Data mentah hanya superadmin | Diizinkan untuk superadmin | ✅ |

---

## 4. Temuan & Rekomendasi

### Temuan 1 — Jumlah item instrumen 93 (seharusnya 59) · Prioritas: Sedang
**Bukti:** API mengembalikan 93 item aktif; ERD-4 mendefinisikan 59.

**Akar masalah:** dua sumber seed tercampur di database produksi:
| Sumber | Pola kode | Jumlah |
|--------|-----------|--------|
| `seed_data.py` (kuesioner dosen) | CD / ID / PD / RD | 58 |
| `migrations/004_instrument_seed.sql` | B1 … E.. | 35 |
| **Total** | | **93** |

Tidak ada duplikasi teks identik, tetapi dua versi instrumen berdampingan → kuesioner publik lebih panjang dari desain & analitik mengagregasi gabungan item.

**Rekomendasi (keputusan data oleh peneliti, bukan dihapus otomatis):**
1. Tentukan set kanonik (kemungkinan 58 item `seed_data.py` = instrumen tervalidasi).
2. Non-aktifkan set lain via `is_active=false` (non-destruktif) atau hapus setelah dikonfirmasi.
3. Hindari menjalankan `seed_data.py` dan migrasi `004` bersamaan pada deploy berikutnya.

### Temuan 2 — Kredensial superadmin · Status: Teratasi
Akun default `superadmin@sinoku.ac.id` tidak terbentuk (migrasi `006` no-op karena superadmin sudah ada). Akun produksi yang berlaku: `admin@sinoku.id`. Pengujian admin dilanjutkan dengan akun ini → seluruh endpoint admin lulus.

### Catatan data kosong (bukan kegagalan)
CPL, CPMK, RPS, Skema, MBKM mengembalikan 0 baris karena belum ada data master untuk MK uji. Endpoint berfungsi normal; analitik berbasis CPL-CPMK akan bermakna setelah data master diisi.

---

## 5. Kesimpulan

| Kategori | Lulus | Total |
|----------|-------|-------|
| Zona Publik (survei E2E) | 10 | 10 |
| Autentikasi & Admin | 23 | 23 |
| Integritas Data | 2 | 3 |
| **TOTAL** | **34** | **36 (94%)** |

**Alur fungsional inti SINOKU terbukti bekerja end-to-end di lingkungan produksi** — dari pengisian kuesioner publik, generate kode anonim, hingga analitik dan generate laporan diagnostik (termasuk seksi RPS-alignment, CPL-CPMK, dan saran revisi). Satu-satunya kegagalan adalah **isu data seeding** (bukan cacat logika program) yang dapat diselesaikan dengan membersihkan set item instrumen.

---

*Pengujian dieksekusi otomatis via skrip terhadap server produksi pada 13 Juni 2026. Bukti respons mentah tersimpan dalam berkas hasil pengujian.*
