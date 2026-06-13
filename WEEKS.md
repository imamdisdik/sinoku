# SINOKU — Pembagian Implementasi per Minggu

> Sistem Evaluasi CIPP untuk Mata Kuliah Bahasa dan Budaya Tionghoa

---

## Minggu 1 — Fondasi & Autentikasi

**Tujuan:** Setup proyek, autentikasi JWT, struktur database awal.

| Komponen | Detail |
|----------|--------|
| **Tech Stack** | FastAPI + SQLAlchemy async + Vue 3 + Docker Compose |
| **Database** | PostgreSQL 16, migrasi awal (universitas, program, MK, user) |
| **Auth** | `POST /auth/login` — JWT access (60 menit) + refresh (30 hari) |
| **Auth** | `POST /auth/logout`, `POST /auth/refresh` |
| **Public** | `GET /public/landing` — statistik ringkasan (UC-01) |
| **Seed** | 59 item instrumen CIPP (ID + ZH), universitas, program, MK contoh |
| **Docker** | `docker-compose.yml` — service: db, backend, frontend, nginx |

---

## Minggu 2 — Manajemen Akademik & Dashboard

**Tujuan:** CRUD lengkap data akademik + dashboard KPI admin.

| Use Case | Endpoint | Detail |
|----------|----------|--------|
| UC-13 | `GET /admin/dashboard/kpi` | KPI: total respons, rata-rata CIPP, tren |
| UC-13 | `GET /admin/dashboard/problem-heatmap` | Item bermasalah di bawah threshold |
| UC-14a | `/admin/universities` (CRUD) | Kelola universitas (superadmin) |
| UC-14b | `/admin/programs` (CRUD) | Kelola program studi |
| UC-14c | `/admin/courses` (CRUD) | Kelola mata kuliah + filter aktif |
| UC-14d | `/admin/cpls` (CRUD) | Kelola CPL per program studi |
| UC-14e | `POST /admin/courses/{id}/cpls` | Pemetaan MK → CPL |
| UC-14f | `/admin/cpmks` (CRUD) | Kelola CPMK per mata kuliah |
| UC-14g | `POST /admin/cpmks/{id}/cpls` | Pemetaan CPMK → CPL |
| — | `/admin/users` (CRUD) | Kelola akun admin/dosen (bonus) |

**Scoping:** Admin hanya melihat data universitas sendiri; dosen dibatasi ke program studi sendiri.

---

## Minggu 3 — Instrumen CIPP & Survey Mahasiswa

**Tujuan:** Manajemen instrumen evaluasi + alur pengisian kuesioner mahasiswa.

| Use Case | Endpoint | Detail |
|----------|----------|--------|
| UC-15 | `GET /admin/instruments/dimensions` | List 4 dimensi CIPP + sub-dimensi + item count |
| UC-15 | `GET /admin/instruments/dimensions/{id}/items` | Item per dimensi/sub-dimensi |
| UC-15 | `POST /admin/instruments/items` | Tambah item instrumen |
| UC-15 | `PUT /admin/instruments/items/{id}` | Edit item |
| UC-15 | `PATCH /admin/instruments/items/{id}/toggle` | Aktif/nonaktif item |
| UC-15 | `POST /admin/instruments/items/import` | **Import bulk via CSV** |
| UC-15 | Open questions CRUD | Pertanyaan terbuka (tambah/edit/toggle) |
| UC-16 | `GET /admin/anonymous-codes` | List kode anonim + filter |
| UC-16 | `PATCH /admin/anonymous-codes/{kode}/toggle` | Toggle aksesibilitas kode |
| UC-02 | `GET /public/universities`, `/programs`, `/courses` | Data untuk form survey |
| UC-03 | `POST /public/survey/start` | Mulai survey mahasiswa + simpan profil |
| UC-04 | `GET /public/survey/{id}/items` | Ambil item per dimensi CIPP |
| UC-06 | `POST /public/survey/{id}/answers` | Submit jawaban per dimensi |
| UC-07 | `POST /public/survey/{id}/submit` | Finalisasi + generate kode anonim |
| UC-08–10 | `GET /public/result/{kode}` | Lihat hasil evaluasi via kode anonim |

**Format CSV Import:**
```
kode,sub_dimension_id,nomor_urut,text_id_dosen,text_id_mahasiswa,text_zh_dosen,text_zh_mahasiswa,indikator,answer_type,scale_min,scale_max,is_required
B1.1.001,1,1,"Dosen menjelaskan...","Dosen saya menjelaskan...","","",,"likert",1,5,true
```

---

## Minggu 4 — Analitik CIPP, RPS & Survey Dosen

**Tujuan:** Analitik lengkap + manajemen RPS + alur survey dosen.

| Use Case | Endpoint | Detail |
|----------|----------|--------|
| UC-17a | `GET /admin/analytics/cipp-scores` | Skor per dimensi + sub-dimensi breakdown |
| UC-17b | `GET /admin/analytics/comparison` | Perbandingan skor dosen vs mahasiswa |
| UC-17c | `GET /admin/analytics/cpl-cpmk-matrix` | Matriks pemetaan CPL ↔ CPMK per MK |
| UC-17d | `GET /admin/analytics/distribution` | Distribusi histogram Likert 1–5 |
| UC-14h | `GET/POST /admin/rps` | CRUD RPS (Rencana Pembelajaran Semester) |
| UC-14i | `GET /admin/rps/{id}/checklist` | Checklist kelengkapan RPS (auto-create) |
| UC-14i | `PATCH /admin/rps/{id}/checklist/{item_id}` | Update status checklist |
| UC-05 | `POST /public/survey/start-dosen` | Mulai survey khusus dosen (JWT required) |

**Tab Analitik di Frontend:**
- **Ringkasan CIPP** — KPI cards + radar chart 4 dimensi
- **Skor Sub-Dimensi** — Breakdown per sub-dimensi dengan tabel + bar
- **Problem Heatmap** — Item di bawah threshold dengan gap dosen-mahasiswa
- **Dosen vs Mahasiswa** — Bar chart perbandingan per dimensi
- **Distribusi Skor** — Histogram Likert 1–5
- **Matriks CPL-CPMK** — Grid pemetaan akademik per MK
- **Tren Respons** — Bar chart jumlah respons per bulan

---

## Minggu 5 — Skema Penilaian, Rubrik & MBKM

**Tujuan:** Sistem penilaian akademik terintegrasi — skema, rubrik, dan MBKM.

| Use Case | Endpoint | Detail |
|----------|----------|--------|
| UC-14j | `GET/POST /admin/assessment/schemes` | Skema penilaian per MK |
| UC-14j | `PUT/DELETE /admin/assessment/schemes/{id}` | Edit/hapus skema |
| UC-14k | `GET/POST /admin/assessment/schemes/{id}/rubrics` | Rubrik per skema |
| UC-14k | `PUT/DELETE /admin/assessment/rubrics/{id}` | Edit/hapus rubrik |
| UC-14l | `GET/POST /admin/assessment/mbkm` | Data integrasi MBKM |
| UC-14l | `PUT/DELETE /admin/assessment/mbkm/{id}` | Edit/hapus MBKM |
| UC-14l | `PATCH /admin/assessment/mbkm/{id}/toggle` | Toggle aktif/nonaktif |

**Validasi Bisnis:**
- `skor_min < skor_max` pada rubrik (400 jika dilanggar)
- `bobot_persen` 0–100 dengan validasi total bobot per MK di frontend
- University scoping: admin/dosen hanya kelola MK di universitas sendiri

**Frontend:**
- `AssessmentScheme.vue` — Tabel skema + indikator total bobot (max 100%)
- `AssessmentRubric.vue` — Cascading filter MK → Skema → Rubrik
- `MbkmIntegration.vue` — Toggle aktif/nonaktif langsung di tabel

---

## Minggu 6 — Export Data & Laporan Diagnostik

**Tujuan:** Export data mentah + generate laporan diagnostik CIPP otomatis.

| Use Case | Endpoint | Detail |
|----------|----------|--------|
| UC-18 | `GET /admin/export/responses` | Export respons + profil responden (xlsx/csv) |
| UC-18 | `GET /admin/export/scores` | Export skor CIPP per item (xlsx/csv) |
| UC-18 | `GET /admin/export/respondents` | Export profil mahasiswa lengkap (xlsx/csv) |
| UC-19 | `POST /admin/reports` | Generate laporan diagnostik CIPP + snapshot JSONB |
| UC-19 | `GET /admin/reports` | List laporan (scoped per universitas) |
| UC-19 | `GET /admin/reports/{id}` | Detail laporan + snapshot lengkap |
| UC-19 | `DELETE /admin/reports/{id}` | Hapus laporan |

**Fitur Export:**
- Format: Excel (openpyxl, header biru tua) atau CSV
- Autentikasi: Bearer token di header (blob response di frontend)
- Filter: per MK, per role responden

**Fitur Laporan Diagnostik:**
- Snapshot JSONB: total respons, skor per dimensi, profil responden (gender/semester/HSK)
- Rekomendasi otomatis: 4 tier (Sangat Baik / Baik / Cukup / Perlu Perhatian)
- Preview: KPI cards, tabel dimensi, bar chart, cetak/PDF via `window.print()`
- Scoping: superadmin lihat semua, admin lihat per-universitas

---

## Ringkasan Status

| Minggu | Use Case | Endpoint | Status |
|--------|----------|----------|--------|
| 1 | UC-01, Auth | 3 | ✅ Selesai |
| 2 | UC-13, UC-14a–g | 16 | ✅ Selesai |
| 3 | UC-02–10, UC-15, UC-16 | 14 | ✅ Selesai |
| 4 | UC-14h–i, UC-17a–d | 9 | ✅ Selesai |
| 5 | UC-14j–l | 9 | ✅ Selesai |
| 6 | UC-18, UC-19 | 7 | ✅ Selesai |
| **Total** | | **58** | **✅ 100%** |

---

## Migrasi Database

| File | Isi | Dijalankan |
|------|-----|------------|
| `001_init.sql` | Tabel inti (users, univ, program, course, cpl, cpmk, instrument, response, respondent) | Minggu 1 |
| `002_rps.sql` | Tabel RPS + checklist | Minggu 4 |
| `003_seed_items.sql` | 59 item instrumen CIPP (ID+ZH) | Minggu 1 |
| `004_open_questions.sql` | Pertanyaan terbuka | Minggu 3 |
| `005_assessment_report.sql` | assessment_schemes, rubrics, mbkm_integrations, diagnostic_reports | Minggu 5–6 |
