# Pemetaan Aktor OBE ↔ SINOKU

> Penyelarasan **model aktor kurikulum OBE 5-tingkat** (Universitas → Fakultas → Prodi → Dosen → Mahasiswa) terhadap peran & fitur yang **sudah didukung** SINOKU (sistem evaluasi CIPP). Dokumen ini menyelaraskan penamaan/peran + mencatat **gap** (tanpa membangun fitur baru besar).

| | |
|---|---|
| **Tanggal** | 16 Juni 2026 |
| **Status sistem** | SINOKU = alat evaluasi CIPP; peran teknis: `superadmin`, `admin`, `dosen` + responden |
| **Tujuan dokumen** | Selaraskan aktor + tugas yang ada, dokumentasikan kekurangan untuk pengembangan lanjut |

---

## Ringkasan Pemetaan Peran

| Aktor OBE | Peran teknis SINOKU | Cakupan |
|-----------|---------------------|---------|
| **1. Universitas** (LPM/WR I) | `superadmin` | Semua institusi |
| **2. Fakultas** (Dekanat/GKM) | — *(belum ada)* | — |
| **3. Program Studi** (Kaprodi/Tim Kurikulum) | `admin` | Per-universitas *(idealnya per-prodi)* |
| **4. Dosen Pengampu** | `dosen` | Per-program studi |
| **5. Mahasiswa** | Responden (anonim) | Per-respons |

---

## 1. Universitas (LPM / WR I) → `superadmin`

**Tugas utama (model OBE):** Input Visi-Misi PT, standar akademik, kebijakan MBKM, template nasional (RPS/Rubrik); Dashboard Mutu Makro; standarisasi dokumen kurikulum nasional.

| Tugas | Status SINOKU |
|-------|---------------|
| Kelola seluruh Universitas, Prodi, MK, CPL, CPMK (CRUD master) | ✅ Didukung |
| Kelola semua akun (admin/dosen) | ✅ Didukung |
| Dashboard mutu lintas-universitas (KPI, rata-rata CIPP, perbandingan antar univ) | ✅ Didukung (analitik) |
| Export data mentah (eksklusif) | ✅ Didukung |
| Input **Visi-Misi PT, standar akademik, kebijakan MBKM** (sebagai field/dokumen) | ❌ Gap |
| **Template nasional RPS/Rubrik** (standarisasi) | ❌ Gap |
| Dashboard Mutu **Makro** khusus (indeks mutu PT) | 🟡 Sebagian (analitik CIPP, belum indeks mutu makro) |

## 2. Fakultas (Dekanat / GKM) → *belum ada*

**Tugas utama:** Menerjemahkan kebijakan universitas, input profil fakultas & rumpun keilmuan; monitoring performa prodi; penyelarasan fasilitas lintas prodi.

| Tugas | Status SINOKU |
|-------|---------------|
| **Seluruh tingkat Fakultas** (entitas, peran, dashboard) | ❌ **Gap total** — struktur saat ini langsung Universitas → Prodi, tanpa lapisan Fakultas |
| Profil fakultas & rumpun keilmuan | ❌ Gap |
| Monitoring performa prodi lintas-prodi | 🟡 Sebagian (superadmin bisa lihat semua prodi, tapi bukan scope fakultas) |

## 3. Program Studi (Kaprodi / Tim Kurikulum) → `admin`

**Tugas utama (jantung sistem):** Input Profil Lulusan, rumusan CPL, struktur MK, pemetaan CPL↔CPMK, Sub-CPMK, konversi SKS MBKM; kurikulum OBE, matriks kompetensi, peta jalan lulusan.

| Tugas | Status SINOKU |
|-------|---------------|
| Rumusan **CPL** (CRUD) | ✅ Didukung |
| Struktur **Mata Kuliah** | ✅ Didukung |
| **CPMK** + pemetaan **CPL ↔ CPMK** | ✅ Didukung (matriks CPL-CPMK di analitik) |
| Integrasi **MBKM** (jenis program, mitra, SKS) | ✅ Didukung |
| **Profil Lulusan** (entitas tersendiri) | ❌ Gap |
| **Sub-CPMK** (turunan CPMK) | ❌ Gap — baru sampai level CPMK |
| **Konversi SKS MBKM** (pemetaan mata kuliah ↔ aktivitas MBKM) | ❌ Gap |
| Matriks kompetensi / peta jalan lulusan OBE | 🟡 Sebagian (matriks CPL-CPMK ada) |
| *Catatan scope:* `admin` saat ini scoped **per-universitas**, model OBE idealnya **per-prodi** | 🟡 Perlu penyesuaian scoping |

## 4. Dosen Pengampu → `dosen`

**Tugas utama:** Memilih Sub-CPMK, menyusun materi/metode, membuat Rubrik OBE (Tugas/Proyek), input nilai komponen mahasiswa; output RPS otomatis, grafik ketercapaian CPMK mahasiswa.

| Tugas | Status SINOKU |
|-------|---------------|
| Kelola **RPS** + checklist kelengkapan | ✅ Didukung |
| **Rubrik** penilaian (level capaian + deskriptor) | ✅ Didukung (via admin) |
| Lihat analitik & laporan (scope prodi) | ✅ Didukung |
| Mengisi evaluasi (sebagai responden dosen) | ✅ Didukung |
| Memilih **Sub-CPMK** | ❌ Gap (Sub-CPMK belum ada) |
| **Rubrik OBE per Tugas/Proyek** | 🟡 Sebagian (rubrik ada, belum terikat tugas/proyek) |
| **Input nilai komponen mahasiswa** | ❌ Gap (tidak ada modul penilaian mahasiswa) |
| **RPS otomatis** (generate dari CPMK/template) | ❌ Gap (RPS manual + checklist) |
| **Grafik ketercapaian CPMK per mahasiswa** | ❌ Gap (analitik saat ini berbasis survei CIPP, bukan nilai) |

## 5. Mahasiswa → Responden (anonim)

**Tugas utama:** Lihat RPS, kumpulkan tugas/proyek, isi logbook & unggah laporan MBKM; Portofolio Akademik Digital.

| Tugas | Status SINOKU |
|-------|---------------|
| Mengisi kuesioner evaluasi CIPP + lihat hasil pribadi (via kode anonim) | ✅ Didukung |
| **Login sebagai mahasiswa** (akun) | ❌ Gap — mahasiswa hanya responden anonim |
| Lihat **RPS** | ❌ Gap |
| **Kumpul tugas/proyek** | ❌ Gap |
| **Logbook MBKM + unggah laporan** | ❌ Gap |
| **Portofolio Akademik Digital** | ❌ Gap |

---

## Kesimpulan & Rekomendasi

**Yang sudah selaras (didukung sekarang):**
- Hierarki **Universitas (superadmin) → Prodi (admin) → Dosen** beserta kelola akademik inti (CPL, CPMK, pemetaan, MK, RPS, rubrik, MBKM) dan **evaluasi CIPP**.

**Gap utama untuk model OBE penuh (pengembangan lanjut, belum dibangun):**
1. **Lapisan Fakultas** (entitas + peran + dashboard).
2. **Sub-CPMK**, **Profil Lulusan**, **konversi SKS MBKM**.
3. **Modul penilaian mahasiswa** (nilai komponen, ketercapaian CPMK per mahasiswa, RPS otomatis).
4. **Mahasiswa sebagai aktor login**: portofolio digital, logbook MBKM, pengumpulan tugas.

**Rekomendasi penyelarasan minimal (opsional, tanpa fitur besar):**
- Sesuaikan **label peran** di UI agar mencerminkan hierarki OBE: `superadmin` → "Universitas/LPM", `admin` → "Program Studi", `dosen` → "Dosen Pengampu".
- Sesuaikan **scoping `admin`** dari per-universitas menjadi per-prodi bila ingin tepat sesuai peran Kaprodi.

> Catatan: SINOKU dibangun & teruji sebagai **sistem evaluasi CIPP**. Model OBE 5-aktor di atas dipetakan sebagai arah penyelarasan + pengembangan; item ❌/🟡 adalah cakupan yang belum tersedia dan dapat dijadikan rencana pengembangan pada tesis.
