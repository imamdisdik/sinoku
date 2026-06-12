<template>
  <div class="container" style="max-width:680px; padding-top:32px; padding-bottom:40px;">
    <!-- Progress indicator -->
    <div class="step-indicator">
      <span class="step done">✓ Pilih MK</span>
      <span class="sep">›</span>
      <span class="step done">✓ Persetujuan</span>
      <span class="sep">›</span>
      <span class="step active">Profil</span>
      <span class="sep">›</span>
      <span class="step">Evaluasi</span>
    </div>

    <form @submit.prevent="submit">

      <!-- SEKSI 1: Identitas Dasar -->
      <div class="section-card">
        <div class="section-title">&#128100; Identitas Diri</div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Nama Lengkap <span class="opt">(opsional)</span></label>
            <input v-model="form.full_name" class="form-input" placeholder="Boleh dikosongkan untuk anonim" />
          </div>
          <div class="form-group">
            <label class="form-label">Jenis Kelamin *</label>
            <select v-model="form.gender" required class="form-input">
              <option value="">— Pilih —</option>
              <option value="Laki-laki">Laki-laki</option>
              <option value="Perempuan">Perempuan</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Usia *</label>
            <input v-model.number="form.age" type="number" min="15" max="60" required class="form-input" placeholder="Tahun" />
          </div>
          <div class="form-group">
            <label class="form-label">Semester Saat Ini *</label>
            <select v-model.number="form.current_semester" required class="form-input">
              <option value="">— Pilih —</option>
              <option v-for="s in 14" :key="s" :value="s">Semester {{ s }}</option>
            </select>
          </div>
          <div class="form-group" style="grid-column:1/-1">
            <label class="form-label">Fakultas <span class="opt">(opsional)</span></label>
            <input v-model="form.faculty" class="form-input" placeholder="Contoh: Fakultas Ilmu Budaya" />
          </div>
        </div>
      </div>

      <!-- SEKSI 2: Pengalaman Bahasa Mandarin -->
      <div class="section-card">
        <div class="section-title">&#127800; Pengalaman Bahasa Mandarin</div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Lama Belajar Mandarin *</label>
            <select v-model="form.mandarin_study_duration" required class="form-input">
              <option value="">— Pilih —</option>
              <option value="< 1 tahun">Kurang dari 1 tahun</option>
              <option value="1-2 tahun">1–2 tahun</option>
              <option value="3-4 tahun">3–4 tahun</option>
              <option value="> 4 tahun">Lebih dari 4 tahun</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Level HSK *</label>
            <select v-model="form.hsk_level_mahasiswa" required class="form-input">
              <option value="">— Pilih —</option>
              <option value="Belum ada">Belum memiliki sertifikat HSK</option>
              <option value="HSK 1">HSK 1</option>
              <option value="HSK 2">HSK 2</option>
              <option value="HSK 3">HSK 3</option>
              <option value="HSK 4">HSK 4</option>
              <option value="HSK 5">HSK 5</option>
              <option value="HSK 6">HSK 6</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Pernah Tinggal di China? *</label>
            <select v-model="form.china_stay_duration" required class="form-input">
              <option value="">— Pilih —</option>
              <option value="Tidak pernah">Tidak pernah</option>
              <option value="< 1 bulan">Kurang dari 1 bulan</option>
              <option value="1-6 bulan">1–6 bulan</option>
              <option value="6-12 bulan">6–12 bulan</option>
              <option value="> 1 tahun">Lebih dari 1 tahun</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Memiliki Teman Orang Tionghoa? *</label>
            <select v-model="form.chinese_friends" required class="form-input">
              <option value="">— Pilih —</option>
              <option value="Ya, banyak">Ya, banyak</option>
              <option value="Ya, beberapa">Ya, beberapa</option>
              <option value="Tidak">Tidak</option>
            </select>
          </div>
        </div>
      </div>

      <!-- SEKSI 3: Pengalaman Mata Kuliah Budaya -->
      <div class="section-card">
        <div class="section-title">&#127891; Pengalaman MK Budaya Tiongkok</div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Sudah Pernah Mengambil MK Budaya Tiongkok? *</label>
            <div class="radio-row">
              <label class="radio-opt" :class="{ active: form.has_taken_culture_course === true }">
                <input type="radio" :value="true" v-model="form.has_taken_culture_course" /> Ya
              </label>
              <label class="radio-opt" :class="{ active: form.has_taken_culture_course === false }">
                <input type="radio" :value="false" v-model="form.has_taken_culture_course" /> Belum
              </label>
            </div>
          </div>
          <div class="form-group" v-if="form.has_taken_culture_course">
            <label class="form-label">Berapa MK Budaya yang Sudah Diambil?</label>
            <select v-model="form.culture_course_count" class="form-input">
              <option value="">— Pilih —</option>
              <option value="1">1 mata kuliah</option>
              <option value="2">2 mata kuliah</option>
              <option value="3">3 mata kuliah</option>
              <option value="> 3">> 3 mata kuliah</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Status MK Ini *</label>
            <select v-model="form.course_status_taken" required class="form-input">
              <option value="">— Pilih —</option>
              <option value="Sedang diambil">Sedang diambil semester ini</option>
              <option value="Sudah selesai">Sudah selesai sebelumnya</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Frekuensi Interaksi Budaya Tiongkok *</label>
            <select v-model="form.cultural_interaction_freq" required class="form-input">
              <option value="">— Pilih —</option>
              <option value="Setiap hari">Setiap hari</option>
              <option value="Beberapa kali seminggu">Beberapa kali seminggu</option>
              <option value="Beberapa kali sebulan">Beberapa kali sebulan</option>
              <option value="Jarang">Jarang</option>
              <option value="Tidak pernah">Tidak pernah</option>
            </select>
          </div>
        </div>

        <!-- MK yang sudah pernah diambil -->
        <div v-if="form.has_taken_culture_course" style="margin-top:16px;">
          <label class="form-label">Daftar MK Budaya yang Pernah Diambil</label>
          <div v-for="(c, i) in form.course_taken" :key="i" class="course-row">
            <input v-model="c.course_name" class="form-input" placeholder="Nama mata kuliah" style="flex:2" />
            <select v-model.number="c.semester_taken" class="form-input" style="flex:1">
              <option :value="null">Semester?</option>
              <option v-for="s in 14" :key="s" :value="s">Sem {{ s }}</option>
            </select>
            <select v-model="c.final_grade" class="form-input" style="flex:1">
              <option value="">Nilai?</option>
              <option v-for="g in ['A','AB','B','BC','C','D','E']" :key="g" :value="g">{{ g }}</option>
            </select>
            <button type="button" class="btn-remove" @click="form.course_taken.splice(i,1)">×</button>
          </div>
          <button type="button" class="btn-add-row" @click="form.course_taken.push({ course_name:'', course_id: null, semester_taken: null, final_grade:'' })">
            + Tambah MK
          </button>
        </div>
      </div>

      <!-- SEKSI 4: Motivasi & Tujuan (multi-pilih) -->
      <div class="section-card">
        <div class="section-title">&#127919; Motivasi & Tujuan</div>

        <div class="form-group">
          <label class="form-label">Motivasi Mempelajari Budaya Tiongkok * <span class="opt">(pilih semua yang sesuai)</span></label>
          <div class="checkbox-grid">
            <label v-for="opt in motivasiOptions" :key="opt" class="check-opt" :class="{ active: form.motivations.includes(opt) }">
              <input type="checkbox" :value="opt" v-model="form.motivations" /> {{ opt }}
            </label>
          </div>
        </div>

        <div class="form-group" style="margin-top:16px;">
          <label class="form-label">Tujuan Karir yang Berhubungan dengan China <span class="opt">(pilih semua yang sesuai)</span></label>
          <div class="checkbox-grid">
            <label v-for="opt in careerOptions" :key="opt" class="check-opt" :class="{ active: form.career_goals.includes(opt) }">
              <input type="checkbox" :value="opt" v-model="form.career_goals" /> {{ opt }}
            </label>
          </div>
        </div>
      </div>

      <!-- SEKSI 5: Media & Aktivitas -->
      <div class="section-card">
        <div class="section-title">&#128247; Media & Aktivitas Budaya</div>

        <div class="form-group">
          <label class="form-label">Media yang Digunakan untuk Belajar Budaya Tiongkok <span class="opt">(pilih semua yang sesuai)</span></label>
          <div class="checkbox-grid">
            <label v-for="opt in mediaOptions" :key="opt" class="check-opt" :class="{ active: form.media_usage.includes(opt) }">
              <input type="checkbox" :value="opt" v-model="form.media_usage" /> {{ opt }}
            </label>
          </div>
        </div>

        <div class="form-group" style="margin-top:16px;">
          <label class="form-label">Aktivitas Budaya yang Pernah Diikuti <span class="opt">(pilih semua yang sesuai)</span></label>
          <div class="checkbox-grid">
            <label v-for="opt in activityOptions" :key="opt" class="check-opt" :class="{ active: form.activities.includes(opt) }">
              <input type="checkbox" :value="opt" v-model="form.activities" /> {{ opt }}
            </label>
          </div>
        </div>
      </div>

      <!-- Validasi error -->
      <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>

      <!-- Tombol navigasi -->
      <div class="nav-btns">
        <button type="button" class="btn btn-outline" @click="router.back()">← Kembali</button>
        <button type="submit" class="btn btn-primary" :disabled="submitting || !canSubmit">
          {{ submitting ? 'Memulai survei...' : 'Lanjut ke Evaluasi →' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSurveyStore } from '@/stores/survey'
import { useUiStore } from '@/stores/ui'
import { publicApi } from '@/api/public'

const router = useRouter()
const survey = useSurveyStore()
const ui = useUiStore()

const submitting = ref(false)
const errorMsg = ref('')

// ── Pilihan multi-select ──────────────────────────────────────────────────
const motivasiOptions = [
  'Ketertarikan pada budaya Asia Timur',
  'Kebutuhan akademik / kurikulum wajib',
  'Rencana studi atau kerja di China',
  'Pengembangan karir di bidang bisnis internasional',
  'Minat pribadi pada bahasa Mandarin',
  'Pengaruh keluarga atau lingkungan',
  'Memahami mitra bisnis Tionghoa',
  'Lainnya',
]
const careerOptions = [
  'Diplomat / hubungan internasional',
  'Bisnis / perdagangan dengan China',
  'Pariwisata & perhotelan',
  'Penerjemah / interpreter Mandarin',
  'Pengajar bahasa / budaya Tionghoa',
  'Penelitian / akademisi',
  'Tidak ada rencana karir khusus',
  'Lainnya',
]
const mediaOptions = [
  'Film & serial TV China',
  'Musik Mandarin (C-pop)',
  'Platform media sosial China (Weibo, Douyin)',
  'Buku & literatur berbahasa Mandarin',
  'Podcast & YouTube berbahasa Mandarin',
  'Koran / berita online China',
  'Aplikasi belajar bahasa (HSK Online, HelloChinese)',
  'Lainnya',
]
const activityOptions = [
  'Festival budaya Tionghoa (Imlek, dll)',
  'Lomba pidato / kaligrafi Mandarin',
  'Pertukaran pelajar ke China',
  'Komunitas / club Mandarin di kampus',
  'Kunjungan ke kawasan pecinan',
  'Program summer / winter di China',
  'Magang di perusahaan China',
  'Belum pernah mengikuti aktivitas budaya',
]

// ── Form state ────────────────────────────────────────────────────────────
const form = ref({
  full_name: '',
  gender: '',
  age: null as number | null,
  current_semester: null as number | null,
  faculty: '',
  mandarin_study_duration: '',
  hsk_level_mahasiswa: '',
  china_stay_duration: '',
  chinese_friends: '',
  has_taken_culture_course: null as boolean | null,
  culture_course_count: '',
  course_status_taken: '',
  cultural_interaction_freq: '',
  course_taken: [] as Array<{ course_name: string; course_id: number | null; semester_taken: number | null; final_grade: string }>,
  motivations: [] as string[],
  career_goals: [] as string[],
  media_usage: [] as string[],
  activities: [] as string[],
})

const canSubmit = computed(() =>
  !!form.value.gender &&
  !!form.value.age &&
  !!form.value.current_semester &&
  !!form.value.mandarin_study_duration &&
  !!form.value.hsk_level_mahasiswa &&
  !!form.value.china_stay_duration &&
  !!form.value.chinese_friends &&
  form.value.has_taken_culture_course !== null &&
  !!form.value.course_status_taken &&
  !!form.value.cultural_interaction_freq
)

async function submit() {
  if (!canSubmit.value) {
    errorMsg.value = 'Harap lengkapi semua field yang wajib diisi (*)'
    return
  }
  if (!survey.selectedCourse || !survey.selectedUniversity) {
    router.push({ name: 'survey' })
    return
  }

  submitting.value = true
  errorMsg.value = ''

  try {
    const body = {
      course_id: survey.selectedCourse.id,
      role: 'mahasiswa',
      bahasa: survey.selectedBahasa,
      university_id: survey.selectedUniversity.id,
      program_id: survey.selectedProgram?.id ?? null,
      // Identitas
      full_name: form.value.full_name || null,
      faculty: form.value.faculty || null,
      // Profil mahasiswa
      gender: form.value.gender,
      age: form.value.age,
      current_semester: form.value.current_semester,
      mandarin_study_duration: form.value.mandarin_study_duration,
      hsk_level_mahasiswa: form.value.hsk_level_mahasiswa,
      china_stay_duration: form.value.china_stay_duration,
      chinese_friends: form.value.chinese_friends,
      has_taken_culture_course: form.value.has_taken_culture_course,
      culture_course_count: form.value.culture_course_count || null,
      course_status_taken: form.value.course_status_taken,
      cultural_interaction_freq: form.value.cultural_interaction_freq,
      course_taken: form.value.course_taken.filter(c => c.course_name.trim()),
      // Multi-pilih
      motivations: form.value.motivations,
      career_goals: form.value.career_goals,
      media_usage: form.value.media_usage,
      activities: form.value.activities,
    }

    const { data } = await publicApi.startSurvey(body)
    survey.initFromServer({
      response_id: data.response_id,
      respondent_id: data.respondent_id,
      role: 'mahasiswa',
      bahasa: survey.selectedBahasa,
      isDosen: false,
    })
    router.push({ name: 'survey-B' })
  } catch (e: any) {
    errorMsg.value = e.response?.data?.detail || 'Gagal memulai survei. Coba lagi.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.step-indicator { display:flex; align-items:center; gap:8px; font-size:12px; margin-bottom:24px; flex-wrap:wrap }
.step { color:#a0aec0; font-weight:500 }
.step.done { color:#38a169; font-weight:600 }
.step.active { color:#1a365d; font-weight:700; background:#ebf8ff; padding:2px 10px; border-radius:12px }
.sep { color:#cbd5e0 }

.section-card { background:#fff; border-radius:12px; padding:24px; margin-bottom:16px; box-shadow:0 1px 3px rgba(0,0,0,0.07) }
.section-title { font-size:15px; font-weight:700; color:#1a365d; margin-bottom:18px; padding-bottom:10px; border-bottom:2px solid #ebf8ff }

.form-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px }
.form-group { display:flex; flex-direction:column; gap:6px }
.form-label { font-size:12px; font-weight:600; color:#4a5568 }
.opt { font-weight:400; color:#a0aec0 }
.form-input { padding:9px 12px; border:1px solid #e2e8f0; border-radius:8px; font-size:13px; color:#2d3748; width:100%; box-sizing:border-box }
.form-input:focus { outline:none; border-color:#3182ce; box-shadow:0 0 0 3px rgba(49,130,206,0.1) }

.radio-row { display:flex; gap:10px }
.radio-opt { display:flex; align-items:center; gap:6px; padding:8px 16px; border:2px solid #e2e8f0; border-radius:8px; cursor:pointer; font-size:13px; flex:1; justify-content:center; transition:all .15s }
.radio-opt.active { border-color:#3182ce; background:#ebf8ff; color:#2b6cb0; font-weight:700 }
.radio-opt input { display:none }

.checkbox-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:6px }
.check-opt { display:flex; align-items:center; gap:8px; padding:8px 12px; border:1.5px solid #e2e8f0; border-radius:8px; cursor:pointer; font-size:12px; color:#4a5568; transition:all .15s }
.check-opt.active { border-color:#3182ce; background:#ebf8ff; color:#2b6cb0; font-weight:600 }
.check-opt input { accent-color:#3182ce }

.course-row { display:flex; gap:8px; margin-bottom:8px; align-items:center }
.btn-remove { background:#fff5f5; color:#e53e3e; border:1px solid #fed7d7; border-radius:6px; padding:6px 10px; cursor:pointer; font-size:16px; flex-shrink:0 }
.btn-add-row { background:none; border:1px dashed #cbd5e0; color:#718096; border-radius:6px; padding:7px 14px; font-size:12px; cursor:pointer; margin-top:4px; width:100% }
.btn-add-row:hover { border-color:#3182ce; color:#3182ce }

.error-banner { background:#fff5f5; color:#e53e3e; border:1px solid #fed7d7; border-radius:8px; padding:12px 16px; font-size:13px; margin-bottom:16px }

.nav-btns { display:flex; gap:12px; margin-top:24px }
.btn { padding:12px 24px; border-radius:8px; font-size:14px; font-weight:600; cursor:pointer; border:none; transition:all .15s }
.btn-outline { background:#fff; border:2px solid #e2e8f0; color:#4a5568 }
.btn-outline:hover { border-color:#3182ce; color:#3182ce }
.btn-primary { background:#1a365d; color:#fff; flex:1 }
.btn-primary:disabled { background:#a0aec0; cursor:not-allowed }
.btn-primary:not(:disabled):hover { background:#2a4a7f }

@media (max-width: 600px) {
  .form-grid { grid-template-columns:1fr }
  .checkbox-grid { grid-template-columns:1fr }
  .course-row { flex-wrap:wrap }
}
</style>
