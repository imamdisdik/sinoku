# SINOKU API Contract v1.0
> Base URL: `/api/v1` | Auth: JWT Bearer Token | Format: JSON

---

## ZONA PUBLIK — Tidak perlu auth

### Public / Landing (UC-01)
```
GET /public/landing
Response 200:
{
  "total_universities": int,
  "total_respondents": int,
  "total_courses_evaluated": int,
  "avg_cipp_score": float,
  "universities": [{ "id": int, "nama": str, "nama_singkat": str, "kota": str }]
}
```

### Public / Survey Setup (UC-02)
```
GET /public/universities
Query: ?is_active=true
Response 200:
{ "data": [{ "id": int, "nama": str, "nama_singkat": str, "kota": str, "provinsi": str }] }

GET /public/universities/{university_id}/programs
Response 200:
{ "data": [{ "id": int, "nama": str, "nama_singkat": str, "jenjang": str }] }

GET /public/programs/{program_id}/courses
Query: ?is_active=true
Response 200:
{ "data": [{ "id": int, "kode_mk": str, "nama_id": str, "nama_zh": str, "sks": int, "semester": int }] }
```

### Public / Mulai Kuesioner (UC-03 + UC-05)
```
POST /public/survey/start
Body:
{
  "course_id": int,
  "role": "dosen" | "mahasiswa",
  "bahasa": "id" | "zh",
  "full_name": str | null,          // null = anonim
  "university_id": int,
  "program_id": int | null,
  // Atribut dosen (jika role=dosen):
  "faculty": str | null,
  "academic_position": str | null,
  "teaching_duration": str | null,
  "education_level": str | null,
  "china_experience_dosen": str | null,
  "hsk_level_dosen": str | null,
  "avg_class_size": str | null,
  "course_taught": [{ "course_name": str, "course_id": int | null }],
  // Atribut mahasiswa (jika role=mahasiswa):
  "gender": str | null,
  "age": int | null,
  "current_semester": int | null,
  "mandarin_study_duration": str | null,
  "hsk_level_mahasiswa": str | null,
  "china_stay_duration": str | null,
  "chinese_friends": str | null,
  "has_taken_culture_course": bool | null,
  "culture_course_count": str | null,
  "course_status_taken": str | null,
  "cultural_interaction_freq": str | null,
  "course_taken": [{ "course_name": str, "course_id": int | null, "semester_taken": int, "final_grade": str }],
  "motivations": [str],             // multi-pilih
  "career_goals": [str],            // multi-pilih
  "media_usage": [str],             // multi-pilih
  "activities": [str]               // multi-pilih
}
Response 201:
{
  "response_id": uuid,
  "respondent_id": uuid,
  "role": str,
  "bahasa": str
}
```

### Public / Ambil Item Kuesioner (UC-04)
```
GET /public/survey/{response_id}/items
Query: ?dimensi=B|C|D|E   (kosong = semua dimensi)
Response 200:
{
  "dimensi": "B",
  "nama_dimensi": str,
  "sub_dimensions": [
    {
      "id": int,
      "kode": str,
      "nama": str,
      "items": [
        {
          "id": int,
          "kode": str,
          "nomor_urut": int,
          "teks": str,           // teks sesuai role + bahasa
          "answer_type": "likert",
          "scale_min": 1,
          "scale_max": 5,
          "is_required": bool
        }
      ]
    }
  ],
  "open_questions": [
    { "id": int, "kode": str, "pertanyaan": str, "is_required": bool }
  ]
}
```

### Public / Submit Jawaban (UC-06)
```
POST /public/survey/{response_id}/answers
Body:
{
  "items": [
    { "item_id": int, "skor": int }   // skor 1-5
  ],
  "open_answers": [
    { "open_question_id": int, "jawaban_teks": str }
  ]
}
Response 200:
{ "saved": int, "response_id": uuid }
```

### Public / Finalisasi & Kode Anonim (UC-07)
```
POST /public/survey/{response_id}/submit
Body: {}
Response 201:
{
  "kode_anonim": "SIN-2025-XXXX",
  "generated_at": datetime,
  "message_id": str,     // pesan konfirmasi (id/zh)
  "message_zh": str
}
```

### Public / Hasil via Kode Anonim (UC-08, UC-09, UC-10)
```
GET /public/result/{kode}
Response 200:
{
  "kode": str,
  "course": { "nama_id": str, "nama_zh": str, "kode_mk": str },
  "role": str,
  "bahasa": str,
  "submitted_at": datetime,
  "cipp_scores": [
    { "dimensi": str, "kode": str, "skor_rata": float, "std_dev": float, "jumlah_item": int }
  ],
  "open_answers": [
    { "pertanyaan": str, "jawaban": str }
  ]
}
Error 403: { "detail": "Akses kode anonim tidak aktif" }
Error 404: { "detail": "Kode tidak ditemukan" }

GET /public/result/{kode}/pdf
Response 200: application/pdf (jsPDF client-side — endpoint ini opsional, bisa diganti client-side only)
```

---

## AUTH

```
POST /auth/login
Body: { "email": str, "password": str }
Response 200:
{
  "access_token": str,
  "token_type": "bearer",
  "expires_in": 3600,
  "user": { "id": uuid, "email": str, "full_name": str, "role": str, "university_id": int | null }
}
Error 401: { "detail": "Email atau password salah" }

POST /auth/logout
Header: Authorization: Bearer {token}
Body: { "refresh_token": str }
Response 200: { "message": "Logout berhasil" }

POST /auth/refresh
Body: { "refresh_token": str }
Response 200:
{ "access_token": str, "expires_in": 3600 }
Error 401: { "detail": "Refresh token tidak valid atau sudah kadaluarsa" }
```

---

## ADMIN — Dashboard (UC-13)

```
GET /admin/dashboard/kpi
Header: Authorization: Bearer {token}
Query: ?university_id=&program_id=&course_id=&periode_start=&periode_end=
Response 200:
{
  "total_responses": int,
  "total_dosen": int,
  "total_mahasiswa": int,
  "avg_cipp_score": float,
  "cipp_by_dimension": [
    { "kode": str, "nama": str, "rata_rata": float, "std_dev": float }
  ],
  "response_trend": [
    { "bulan": str, "jumlah": int }
  ]
}

GET /admin/dashboard/problem-heatmap
Query: ?university_id=&program_id=&course_id=&threshold=3.0
Response 200:
{
  "items": [
    {
      "item_id": int, "kode": str, "teks_id": str,
      "dimensi": str, "sub_dimensi": str,
      "skor_dosen": float | null, "skor_mahasiswa": float | null,
      "gap": float
    }
  ]
}
```

---

## ADMIN — Akademik (UC-14a s/d UC-14g)

### Universitas
```
GET    /admin/universities               Query: ?page=&limit=&search=&is_active=
POST   /admin/universities               Body: UniversityCreate
GET    /admin/universities/{id}
PUT    /admin/universities/{id}          Body: UniversityUpdate
DELETE /admin/universities/{id}          Response 204

Schema UniversityCreate:
{ "nama": str, "nama_singkat": str, "jenis": str, "kota": str, "provinsi": str,
  "website": str|null, "akreditasi": str|null, "tahun_berdiri": int|null }
```

### Program Studi
```
GET    /admin/programs                   Query: ?university_id=&page=&limit=&search=
POST   /admin/programs                   Body: ProgramCreate
GET    /admin/programs/{id}
PUT    /admin/programs/{id}
DELETE /admin/programs/{id}

Schema ProgramCreate:
{ "university_id": int, "nama": str, "nama_singkat": str, "jenjang": str,
  "tahun_berdiri": int|null, "akreditasi": str|null }
```

### Mata Kuliah
```
GET    /admin/courses                    Query: ?program_id=&semester=&search=&is_active=
POST   /admin/courses                    Body: CourseCreate
GET    /admin/courses/{id}
PUT    /admin/courses/{id}
DELETE /admin/courses/{id}
POST   /admin/courses/{id}/cpls          Body: { "cpl_ids": [int] }    // mapping MK-CPL
DELETE /admin/courses/{id}/cpls/{cpl_id}

Schema CourseCreate:
{ "program_id": int, "kode_mk": str, "nama_id": str, "nama_zh": str,
  "sks": int, "semester": int, "status_mk": str, "deskripsi": str|null }
```

### CPL
```
GET    /admin/cpls                       Query: ?program_id=&kategori=
POST   /admin/cpls                       Body: CplCreate
GET    /admin/cpls/{id}
PUT    /admin/cpls/{id}
DELETE /admin/cpls/{id}

Schema CplCreate:
{ "program_id": int, "kode_cpl": str, "deskripsi_id": str, "deskripsi_zh": str, "kategori": str }
```

### CPMK
```
GET    /admin/cpmks                      Query: ?course_id=
POST   /admin/cpmks                      Body: CpmkCreate
GET    /admin/cpmks/{id}
PUT    /admin/cpmks/{id}
DELETE /admin/cpmks/{id}
POST   /admin/cpmks/{id}/cpls            Body: { "cpl_ids": [int] }    // mapping CPMK-CPL
DELETE /admin/cpmks/{id}/cpls/{cpl_id}

Schema CpmkCreate:
{ "course_id": int, "kode_cpmk": str, "deskripsi_id": str, "deskripsi_zh": str, "bobot_persen": float }
```

---

## ADMIN — RPS (UC-14h s/d UC-14i)

```
GET    /admin/rps                        Query: ?course_id=&tahun_akademik=&status=
POST   /admin/rps                        Body: RpsCreate
GET    /admin/rps/{id}
PUT    /admin/rps/{id}                   Body: RpsUpdate
DELETE /admin/rps/{id}

Schema RpsCreate:
{ "course_id": int, "tahun_akademik": str, "semester": str,
  "status": "draft"|"aktif"|"arsip", "file_url": str|null, "catatan": str|null }

GET    /admin/rps/{id}/checklist
Response 200:
{
  "rps_id": int,
  "items": [
    { "id": int, "kode": str, "nama_komponen": str, "is_mandatory": bool,
      "is_fulfilled": bool|null, "catatan": str|null, "checked_at": datetime|null }
  ],
  "completion_pct": float
}

PUT    /admin/rps/{id}/checklist
Body:
{
  "responses": [
    { "checklist_item_id": int, "is_fulfilled": bool, "catatan": str|null }
  ]
}
Response 200: { "updated": int }
```

---

## ADMIN — Asesmen (UC-14j s/d UC-14l)

### Skema Asesmen
```
GET    /admin/assessment/schemes         Query: ?course_id=&rps_version_id=
POST   /admin/assessment/schemes         Body: SchemeCreate
PUT    /admin/assessment/schemes/{id}
DELETE /admin/assessment/schemes/{id}

Schema SchemeCreate:
{ "course_id": int, "rps_version_id": int|null, "nama_komponen": str,
  "tipe": str, "bobot_persen": float, "deskripsi": str|null }
```

### Rubrik
```
GET    /admin/assessment/rubrics         Query: ?scheme_id=&cpmk_id=
POST   /admin/assessment/rubrics         Body: RubricCreate
PUT    /admin/assessment/rubrics/{id}
DELETE /admin/assessment/rubrics/{id}

Schema RubricCreate:
{ "assessment_scheme_id": int, "cpmk_id": int, "level": str,
  "skor_min": float, "skor_max": float, "deskriptor": str }
```

### MBKM
```
GET    /admin/mbkm                       Query: ?course_id=&is_active=
POST   /admin/mbkm                       Body: MbkmCreate
PUT    /admin/mbkm/{id}
DELETE /admin/mbkm/{id}

Schema MbkmCreate:
{ "course_id": int, "jenis_program": str, "nama_mitra": str,
  "deskripsi": str|null, "sks_diakui": int, "tahun_akademik": str }
```

---

## ADMIN — Instrumen (UC-15)

```
GET    /admin/instruments                Query: ?is_active=&page=&limit=
POST   /admin/instruments                Body: InstrumentCreate (dimensi/subdimensi baru)
GET    /admin/instruments/dimensions     // list 4 dimensi CIPP + sub-dimensi
GET    /admin/instruments/items          Query: ?sub_dimension_id=&dimensi=&search=&page=&limit=
POST   /admin/instruments/items          Body: ItemCreate
GET    /admin/instruments/items/{id}
PUT    /admin/instruments/items/{id}     Body: ItemUpdate
DELETE /admin/instruments/items/{id}
POST   /admin/instruments/items/import   Body: multipart/form-data { "file": csv/xlsx }
Response 200: { "imported": int, "skipped": int, "errors": [str] }

Schema ItemCreate:
{ "sub_dimension_id": int, "kode": str, "nomor_urut": int,
  "text_id_dosen": str, "text_id_mahasiswa": str,
  "text_zh_dosen": str, "text_zh_mahasiswa": str,
  "indikator": str|null, "kompetensi_dosen": str|null, "kompetensi_mahasiswa": str|null,
  "answer_type": "likert", "scale_min": 1, "scale_max": 5,
  "is_required": bool, "is_active": bool }
```

---

## ADMIN — Kode Anonim (UC-16)

```
GET    /admin/anonymous-codes
Query: ?course_id=&is_accessible=&page=&limit=&search=
Response 200:
{
  "data": [
    { "id": int, "kode": str, "response_id": uuid, "is_accessible": bool,
      "generated_at": datetime, "last_accessed": datetime|null,
      "respondent_role": str, "course_nama": str }
  ],
  "total": int, "page": int, "limit": int
}

PATCH  /admin/anonymous-codes/{kode}/toggle
Body: { "is_accessible": bool }
Response 200: { "kode": str, "is_accessible": bool }
```

---

## ADMIN — Analitik CIPP (UC-17)

### Filter Global (semua endpoint analitik menerima query params ini)
```
?university_id=int&program_id=int&course_id=int&role=dosen|mahasiswa|all
&periode_start=date&periode_end=date&bahasa=id|zh|all
```

### Skor CIPP per Dimensi (UC-17a)
```
GET /admin/analytics/cipp-scores
Response 200:
{
  "filters": { ... },
  "total_responses": int,
  "dimensions": [
    {
      "kode": str, "nama": str, "warna_hex": str,
      "rata_rata": float, "std_dev": float,
      "sub_dimensions": [
        { "kode": str, "nama": str, "rata_rata": float, "std_dev": float, "n": int }
      ]
    }
  ]
}
```

### Perbandingan (UC-17b)
```
GET /admin/analytics/comparison
Query: (+ filter global) &group_by=university|program|course
Response 200:
{
  "group_by": str,
  "data": [
    {
      "group_id": int, "group_nama": str,
      "n_responses": int,
      "cipp": { "B": float, "C": float, "D": float, "E": float }
    }
  ]
}
```

### Heatmap CPL-CPMK (UC-17c)
```
GET /admin/analytics/cpl-cpmk-matrix
Query: ?course_id=int (wajib)
Response 200:
{
  "course": { "id": int, "nama": str },
  "cpls": [{ "id": int, "kode": str }],
  "cpmks": [{ "id": int, "kode": str }],
  "matrix": [
    { "cpmk_id": int, "cpl_id": int, "has_mapping": bool,
      "avg_score": float|null, "n": int }
  ]
}
```

### Distribusi Histogram (UC-17d)
```
GET /admin/analytics/distribution
Query: (+ filter global) &item_id=int|null &dimensi=B|C|D|E|null
Response 200:
{
  "dimensi": str|null,
  "role_breakdown": {
    "dosen":     { "1": int, "2": int, "3": int, "4": int, "5": int },
    "mahasiswa": { "1": int, "2": int, "3": int, "4": int, "5": int }
  },
  "mean_dosen": float,
  "mean_mahasiswa": float
}
```

### Item Bermasalah / Problem Heatmap (UC-17e)
```
GET /admin/analytics/problem-items
Query: (+ filter global) &threshold=float (default 3.0) &limit=int (default 10)
Response 200:
{
  "threshold": float,
  "items": [
    {
      "item_id": int, "kode": str,
      "teks_id_dosen": str, "teks_id_mahasiswa": str,
      "dimensi": str, "sub_dimensi": str,
      "skor_dosen": float|null, "skor_mahasiswa": float|null,
      "n_dosen": int, "n_mahasiswa": int,
      "gap": float
    }
  ]
}
```

---

## ADMIN — Export (UC-18)

```
GET /admin/export/chart
Query: ?chart_type=bar|line|heatmap|histogram &dimensi= &course_id= &format=png|svg
Response 200: image/png atau image/svg+xml

GET /admin/export/pdf
Query: ?report_id=uuid|null &course_id= &periode_start= &periode_end=
Response 200: application/pdf
Header: Content-Disposition: attachment; filename="SINOKU-Report-{date}.pdf"
(Server-side Playwright render)

GET /admin/export/excel
Query: ?type=aggregate|raw &course_id= &periode_start= &periode_end=
Response 200: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Header: Content-Disposition: attachment; filename="SINOKU-Data-{date}.xlsx"

GET /admin/export/csv
Query: ?type=responses|items &course_id= &periode_start= &periode_end=
Response 200: text/csv
```

---

## ADMIN — Laporan Diagnostik (UC-19)

```
POST /admin/reports/generate
Header: Authorization: Bearer {token}
Body:
{
  "university_id": int,
  "program_id": int,
  "course_id": int,
  "periode_start": date,
  "periode_end": date,
  "title": str
}
Response 201:
{
  "id": uuid,
  "title": str,
  "generated_at": datetime,
  "summary": {
    "total_responses": int,
    "cipp_scores": { "B": float, "C": float, "D": float, "E": float },
    "problem_items_count": int,
    "rps_completion_pct": float
  }
}

GET  /admin/reports
Query: ?university_id=&program_id=&course_id=&page=&limit=
Response 200:
{ "data": [{ "id": uuid, "title": str, "course": str, "generated_at": datetime, "pdf_url": str|null }],
  "total": int }

GET  /admin/reports/{id}
Response 200:
{
  "id": uuid, "title": str, "generated_at": datetime,
  "course": { "nama_id": str, "kode_mk": str },
  "periode_start": date, "periode_end": date,
  "snapshot_json": {
    "cipp_scores": [...],
    "problem_items": [...],
    "recommendations": [...],    // auto-generated per dimensi
    "rps_checklist": {...},
    "open_answers_summary": [...]
  },
  "pdf_url": str|null
}

GET  /admin/reports/{id}/pdf
Response 200: application/pdf
```

---

## Konvensi Error Response

```json
// 400 Bad Request
{ "detail": "Pesan error validasi", "errors": { "field": "keterangan" } }

// 401 Unauthorized
{ "detail": "Token tidak valid atau sudah kadaluarsa" }

// 403 Forbidden
{ "detail": "Akses ditolak" }

// 404 Not Found
{ "detail": "Resource tidak ditemukan" }

// 422 Unprocessable Entity (Pydantic validation)
{ "detail": [{ "loc": ["body", "field"], "msg": "error", "type": "value_error" }] }

// 500 Internal Server Error
{ "detail": "Terjadi kesalahan server" }
```

---

## Ringkasan Endpoint

| Zona | Router File | Jumlah Endpoint |
|------|-------------|-----------------|
| Publik | public/landing, survey, result | 10 |
| Auth | auth | 3 |
| Admin — Dashboard | admin/dashboard | 2 |
| Admin — Akademik | admin/academic | 22 |
| Admin — RPS | admin/rps | 7 |
| Admin — Asesmen | admin/assessment | 9 |
| Admin — Instrumen | admin/instrument | 9 |
| Admin — Kode Anonim | admin/anonymous | 2 |
| Admin — Analitik | admin/analytics | 5 |
| Admin — Export | admin/export | 4 |
| Admin — Laporan | admin/report | 4 |
| **TOTAL** | | **77** |
