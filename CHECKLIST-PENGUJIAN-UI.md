# Checklist Pengujian UI — Sistem SINOKU

> Pengujian antarmuka (UI/UX) manual & menyeluruh di browser terhadap sistem produksi.
> Lengkapi kolom **Hasil** (✅/❌) dan **Catatan** saat menguji.

| | |
|---|---|
| **URL** | `http://202.10.34.93` |
| **Akun admin** | `admin@sinoku.id` / `admin123` |
| **Browser uji** | Chrome / Edge terbaru (disarankan layar ≥ 1366px) |
| **Tanggal uji** | __________ |
| **Penguji** | __________ |

> 🆕 = fitur hasil penutupan gap (perlu perhatian khusus).

---

## A. Modul Publik — Tanpa Login

### A1. Landing Page
| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 1 | Buka `http://202.10.34.93` | Hero section "SINOKU" + tagline tampil | ☐ | |
| 2 | Lihat bagian penjelasan CIPP | 4 dimensi (Context/Input/Process/Product) dijelaskan | ☐ | |
| 3 | Klik toggle bahasa (ID/中文) | Teks UI berubah bahasa, tersimpan saat refresh | ☐ | |
| 4 | Klik tombol "Mulai Evaluasi" | Diarahkan ke alur seleksi kuesioner | ☐ | |

### A2. Seleksi & Pengisian Kuesioner (Mahasiswa)
| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 5 | Pilih Universitas → Prodi → MK | Dropdown ber-cascade (prodi muncul setelah univ, dst.) | ☐ | |
| 6 | Pilih Peran = Mahasiswa, Bahasa = Indonesia | Pilihan tersimpan | ☐ | |
| 7 | Halaman Consent — baca, centang setuju | Tombol lanjut aktif setelah centang | ☐ | |
| 8 | Isi form profil mahasiswa | Validasi field wajib bekerja | ☐ | |
| 9 | Step 1 Context — progress bar tampil "1/4" | Indikator langkah benar | ☐ | |
| 10 | Coba klik Next tanpa isi item wajib | Ditolak + pesan "harap isi item wajib" | ☐ | |
| 11 | Isi semua item, navigasi Next/Prev | Jawaban tersimpan saat kembali (Prev) | ☐ | |
| 12 | Selesaikan Step 2,3,4 (total **59 item**) | Semua dimensi terisi | ☐ | |
| 13 | Submit kuesioner | Halaman Terima Kasih + **kode anonim** tampil | ☐ | |
| 14 | Klik tombol "Copy" kode | Kode tersalin ke clipboard | ☐ | |

### A3. Lihat Hasil via Kode Anonim
| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 15 | Buka menu Hasil, masukkan kode anonim | Skor CIPP per dimensi (4 kartu) tampil | ☐ | |
| 16 🆕 | Lihat "Ringkasan Capaian Pembelajaran" | Tabel sub-dimensi Produk: skor vs target + status Tercapai/Belum | ☐ | |
| 17 | Lihat jawaban pertanyaan terbuka (jika ada) | Tampil | ☐ | |
| 18 🆕 | Klik tombol **"⬇ PDF"** | File `SINOKU-Hasil-{kode}.pdf` terunduh, isi rapi (skor + capaian + jawaban) | ☐ | |
| 19 🆕 | Klik tombol **"🖨 Cetak"** | Dialog print muncul, form pencarian tersembunyi (print-friendly) | ☐ | |

---

## B. Autentikasi

| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 20 | Buka `/login`, login `admin@sinoku.id` | Masuk ke dashboard admin | ☐ | |
| 21 | Login dengan password salah | Pesan "Email atau password salah" | ☐ | |
| 22 | Klik Logout | Kembali ke login, sesi berakhir | ☐ | |

---

## C. Dashboard Admin

| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 23 | Buka Dashboard | KPI cards (total respons, rata-rata CIPP, dll.) tampil | ☐ | |
| 24 | Lihat grafik ringkasan | Chart ter-render tanpa error | ☐ | |

---

## D. Kelola Kurikulum (CRUD)

| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 25 | Universitas: Tambah → isi → Simpan | Data baru muncul di tabel | ☐ | |
| 26 | Universitas: Edit → ubah → Simpan | Perubahan tersimpan & tampil | ☐ | |
| 27 | Universitas: Hapus | Data hilang dari tabel | ☐ | |
| 28 | Program Studi: CRUD (relasi ke univ) | Berfungsi | ☐ | |
| 29 | Mata Kuliah: CRUD | Berfungsi | ☐ | |
| 30 🆕 | **CPL**: filter "Semua Program Studi" | **Semua CPL tampil** (bukan kosong) | ☐ | |
| 31 🆕 | CPL: Tambah baru | **Langsung muncul** di tabel tanpa pilih filter | ☐ | |
| 32 | CPL: Edit & Hapus | Berfungsi | ☐ | |
| 33 | Mapping MK → CPL (multi-select) | Tersimpan | ☐ | |
| 34 🆕 | **CPMK**: filter "Semua Mata Kuliah" | **Semua CPMK tampil** | ☐ | |
| 35 | CPMK: CRUD + Mapping CPMK → CPL | Berfungsi | ☐ | |

---

## E. Kelola Instrumen

| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 36 | Buka Instrumen → pilih dimensi B/C/D/E | Item per sub-dimensi tampil, total **59** | ☐ | |
| 37 | Tambah Item → isi → Simpan | Item baru tampil | ☐ | |
| 38 | Edit Item | Perubahan tersimpan | ☐ | |
| 39 | Toggle aktif/nonaktif item | Status berubah | ☐ | |
| 40 🆕 | Klik **"⟲ Riwayat"** pada item yang pernah diedit | Modal timeline snapshot perubahan tampil | ☐ | |
| 41 🆕 | Klik **"📄 Template"** | File `template_item_instrumen.csv` terunduh | ☐ | |
| 42 🆕 | Klik **"⭳ Export CSV"** | File `item_instrumen.csv` (59 item, Mandarin terbaca) terunduh | ☐ | |
| 43 | Klik "Import CSV" → unggah file | Notifikasi jumlah diimpor/dilewati | ☐ | |
| 44 | Tab Pertanyaan Terbuka: CRUD + toggle | Berfungsi | ☐ | |

---

## F. Kode Anonim

| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 45 | Buka Kode Anonim | Tabel kode + metadata (MK, peran, tanggal) | ☐ | |
| 46 | Toggle akses hasil sebuah kode | Status akses berubah | ☐ | |
| 47 | Filter per MK | Tabel terfilter | ☐ | |

---

## G. Analitik & Visualisasi

| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 48 | Tab "Ringkasan CIPP" | KPI cards + kartu per dimensi + **radar chart** tampil | ☐ | |
| 49 🆕 | Pada radar, klik **"📷 PNG"** | File `radar-cipp.png` terunduh (resolusi tinggi) | ☐ | |
| 50 🆕 | Klik **"💾 SVG"** | File `radar-cipp.svg` terunduh | ☐ | |
| 51 🆕 | Klik **"📄 PDF Analisis"** (header) | PDF (KPI + tabel dimensi) terunduh | ☐ | |
| 52 | Tab "Skor Sub-Dimensi" | Tabel breakdown per sub-dimensi | ☐ | |
| 53 | Tab "Problem Heatmap" + ubah threshold | Item bermasalah ter-update | ☐ | |
| 54 | Tab "Dosen vs Mahasiswa" | Bar perbandingan tampil | ☐ | |
| 55 | Tab "Perbandingan Univ/Prodi/MK" — ganti group_by | Tabel ranking per grup | ☐ | |
| 56 | Tab "Distribusi Skor" | Histogram Likert 1–5 | ☐ | |
| 57 | Tab "Matriks CPL-CPMK" — pilih MK | Grid pemetaan tampil | ☐ | |
| 58 🆕 | **Filter global**: ubah Peran / Periode | Semua tab ikut terfilter | ☐ | |
| 59 🆕 | **Filter global (superadmin)**: pilih Universitas → Prodi | Selektor prodi ter-cascade + data terfilter | ☐ | |
| 60 🆕 | Klik **"✕ Reset"** filter | Semua filter kembali kosong | ☐ | |

---

## H. RPS & Asesmen

| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 61 | RPS: Tambah versi → Simpan | Tampil di tabel | ☐ | |
| 62 | RPS: buka Checklist → toggle komponen | Persentase kelengkapan ter-update | ☐ | |
| 63 | Skema Asesmen: CRUD + indikator total bobot | Berfungsi, peringatan bila bobot ≠ 100% | ☐ | |
| 64 | Rubrik: pilih MK → Skema → CRUD rubrik | Cascade benar, validasi skor_min<skor_max | ☐ | |
| 65 | MBKM: CRUD + toggle aktif | Berfungsi | ☐ | |

---

## I. Laporan Diagnostik

| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 66 | Buka Laporan → klik "Generate" → isi wizard (MK + periode) | Laporan ter-generate, redirect ke preview | ☐ | |
| 67 | Preview: KPI cards + tabel dimensi + bar chart | Tampil | ☐ | |
| 68 🆕 | Seksi **"Keselarasan RPS & Asesmen"** | Status RPS, % checklist, total bobot | ☐ | |
| 69 🆕 | Seksi **"Analisis CPL-CPMK"** | Jumlah CPMK, cakupan pemetaan | ☐ | |
| 70 🆕 | Seksi **"Saran Revisi RPS"** | Daftar saran otomatis | ☐ | |
| 71 | Klik "Cetak/PDF" | Print-friendly tampil | ☐ | |
| 72 | Histori: laporan tersimpan di daftar | Tampil | ☐ | |

---

## J. Export Data

| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 73 | Buka Export Data (sebagai superadmin) | 3 kartu (Respons, Skor, Profil) tampil | ☐ | |
| 74 | Export Skor → Excel & CSV | File terunduh | ☐ | |
| 75 🆕 | Login sebagai **dosen** → buka Export | Kartu data mentah **tersembunyi** + catatan superadmin-only | ☐ | |

---

## K. Manajemen Akun & Survei Dosen

| # | Langkah | Hasil Diharapkan | Hasil | Catatan |
|---|---------|------------------|:----:|---------|
| 76 | Kelola Akun: buat akun dosen | Akun baru tampil | ☐ | |
| 77 | Login sebagai dosen → "Isi Evaluasi" | Alur survei dosen (59 item) berfungsi | ☐ | |
| 78 | Dosen: data ter-scope ke MK/prodinya saja | Tidak bisa lihat data univ lain | ☐ | |

---

## Ringkasan Hasil

| Modul | Lulus | Total |
|-------|:----:|:----:|
| A. Publik | | 19 |
| B. Auth | | 3 |
| C. Dashboard | | 2 |
| D. Kurikulum | | 11 |
| E. Instrumen | | 9 |
| F. Kode Anonim | | 3 |
| G. Analitik | | 13 |
| H. RPS & Asesmen | | 5 |
| I. Laporan | | 7 |
| J. Export | | 3 |
| K. Akun & Dosen | | 3 |
| **TOTAL** | | **78** |

**Kesimpulan:** _______________________________________________

---

*Item bertanda 🆕 adalah fitur hasil penutupan gap (15 Juni 2026) yang sebaiknya diuji dengan teliti.*
