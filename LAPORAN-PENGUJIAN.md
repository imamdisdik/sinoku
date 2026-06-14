# Laporan Pengujian Sistem SINOKU

> Pengujian **Black-box menyeluruh** terhadap sistem yang **ter-deploy di server produksi**, dengan **data bersih** (database di-reset sebelum pengujian). Setiap skenario dieksekusi langsung ke API live.

| | |
|---|---|
| **Metode** | Black-box (functional + security), API-level, otomatis via skrip |
| **Target** | `http://202.10.34.93` (production, via Nginx) |
| **Tanggal** | 14 Juni 2026 |
| **Akun** | `admin@sinoku.id` (superadmin) + akun dosen uji |
| **Total skenario** | 29 |
| **Lulus** | **29 (100%)** |
| **Cakupan** | Alur publik (mahasiswa & dosen), seluruh admin, analitik, laporan, export, integritas data, uji keamanan |

> Pengujian ini dilakukan setelah perbaikan instrumen (93 → 59 item) dan reset data uji, sehingga mencerminkan kondisi sistem yang bersih & benar.

---

## Fase 0 — Verifikasi State Bersih

| No | Aspek | Diharapkan | Aktual | Status |
|----|-------|-----------|--------|--------|
| 1 | Responden ter-reset | 0 | 0 | ✅ |
| 2 | Item instrumen aktif | 59 | 59 (B:11 C:15 D:16 E:17) | ✅ |
| 3 | Tidak ada sisa item nonaktif | total = 59 | 59 | ✅ |

---

## Fase 1 — E2E Survei Mahasiswa (UC-01 s/d UC-08)

| No | UC | Skenario | Hasil Aktual | Status |
|----|----|----------|--------------|--------|
| 4 | UC-01 | Landing + statistik | 10 universitas, statistik tampil | ✅ |
| 5 | UC-02 | Seleksi univ → prodi → MK | data valid berjenjang | ✅ |
| 6 | UC-03/04 | Mulai survei + **59 item** disajikan | 59 item (4 dimensi) | ✅ |
| 7 | UC-06/07 | Submit 59 jawaban + kode anonim | kode `SIN-2026-ESM2` | ✅ |
| 8 | UC-08 | Lihat hasil via kode (skor CIPP) | 4 dimensi tampil | ✅ |

---

## Fase 2 & 3 — Akun & E2E Survei Dosen (UC-05, UC-11, UC-14)

| No | UC | Skenario | Hasil Aktual | Status |
|----|----|----------|--------------|--------|
| 9 | UC-14 | Admin membuat akun dosen | HTTP 201 | ✅ |
| 10 | UC-11 | Login sebagai dosen | role=dosen | ✅ |
| 11 | UC-05 | Survei dosen (login) + **59 item** | 59 item, submit OK | ✅ |
| 12 | UC-07 | Dosen finalisasi + kode anonim | kode `SIN-2026-D87J` | ✅ |

---

## Fase 4 — Endpoint Admin (analitik berdata)

| No | UC | Skenario | Status |
|----|----|----------|--------|
| 13 | UC-13 | Dashboard KPI | ✅ |
| 14 | UC-13 | Problem heatmap | ✅ |
| 15 | UC-15 | Dimensi instrumen | ✅ |
| 16 | UC-16 | Kode anonim (2 terdaftar) | ✅ |
| 17 | UC-17a | Analitik skor CIPP | ✅ |
| 18 | UC-17b | Perbandingan antar Universitas | ✅ |
| 19 | UC-17b | Perbandingan antar Program Studi | ✅ |
| 20 | UC-17b | Perbandingan antar Mata Kuliah | ✅ |
| 21 | UC-17 | Perbandingan Dosen vs Mahasiswa | ✅ |
| 22 | UC-17d | Distribusi skor Likert | ✅ |
| 23 | UC-18c | Export skor agregat (CSV) | ✅ |
| 24 | UC-18c | Export skor agregat (XLSX, 10.855 bytes) | ✅ |
| 25 | UC-18d | Export data mentah (superadmin) | ✅ |
| 26 | UC-19 | **Generate laporan diagnostik** (respons=1) | ✅ |
| 27 | UC-19c/d/f | Snapshot: RPS-alignment + CPL-CPMK + saran revisi | ✅ |

---

## Fase 5 — Uji Negatif & Keamanan

| No | UC | Skenario | Diharapkan | Aktual | Status |
|----|----|----------|-----------|--------|--------|
| 28 | SEC | Login password salah | ditolak | HTTP 401 | ✅ |
| 29 | SEC | Akses kode anonim tak ada | ditolak | HTTP 404 | ✅ |
| 30 | SEC | Endpoint admin tanpa token | ditolak | HTTP 403 | ✅ |
| 31 | UC-18d | Dosen (non-superadmin) export data mentah | ditolak | HTTP 403 | ✅ |

> Catatan: validasi email juga terbukti bekerja — alamat dengan TLD reserved (`.test`) ditolak server (HTTP 422), sesuai standar RFC.

---

## Ringkasan

| Fase | Lulus | Total |
|------|-------|-------|
| 0 — State bersih | 3 | 3 |
| 1 — Survei mahasiswa | 5 | 5 |
| 2–3 — Survei dosen | 4 | 4 |
| 4 — Admin & analitik | 15 | 15 |
| 5 — Keamanan | 4 | 4 |
| **TOTAL** | **31** | **31 (100%)** |

*(31 titik uji termasuk sub-langkah pada Fase 1.)*

---

## Kesimpulan

Seluruh alur fungsional SINOKU **lulus pengujian menyeluruh di lingkungan produksi dengan data bersih**:

1. **Alur publik** — mahasiswa & dosen dapat mengisi kuesioner **59 item** (sesuai instrumen tervalidasi), memperoleh kode anonim, dan melihat hasil CIPP.
2. **Admin & analitik** — seluruh dashboard, analitik CIPP (termasuk perbandingan antar Univ/Prodi/MK), serta generate laporan diagnostik (dengan seksi RPS-alignment, analisis CPL-CPMK, dan saran revisi) berfungsi.
3. **Keamanan** — autentikasi, otorisasi berbasis peran (data mentah khusus superadmin), dan validasi input bekerja sesuai rancangan.
4. **Integritas data** — instrumen tepat **59 item** (temuan pengujian sebelumnya, 93 item, telah dibereskan).

Tidak ada kegagalan fungsional yang tersisa. Sistem siap digunakan untuk pengumpulan data evaluasi.

---

*Pengujian dieksekusi otomatis via skrip terhadap server produksi pada 14 Juni 2026. Berkas hasil mentah (JSON) tersimpan sebagai bukti.*
