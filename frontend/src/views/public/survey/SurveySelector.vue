<template>
  <div class="container" style="max-width:600px; padding-top:40px;">
    <div class="card">
      <h1 style="font-size:20px; font-weight:800; margin:0 0 24px; color:#1a365d;">
        {{ t('survey.select_title') }}
      </h1>

      <div class="form-group">
        <label class="form-label">{{ t('survey.select_university') }} *</label>
        <select class="form-select" v-model="survey.selectedUniversity" @change="onUnivChange">
          <option :value="null">{{ t('common.placeholder_select') }}</option>
          <option v-for="u in universities" :key="u.id" :value="u">{{ u.nama }}</option>
        </select>
      </div>

      <div class="form-group" v-if="programs.length">
        <label class="form-label">{{ t('survey.select_program') }} *</label>
        <select class="form-select" v-model="survey.selectedProgram" @change="onProgramChange">
          <option :value="null">{{ t('common.placeholder_select') }}</option>
          <option v-for="p in programs" :key="p.id" :value="p">{{ p.nama }} ({{ p.jenjang }})</option>
        </select>
      </div>

      <div class="form-group" v-if="courses.length">
        <label class="form-label">{{ t('survey.select_course') }} *</label>
        <select class="form-select" v-model="survey.selectedCourse" @change="onCourseChange">
          <option :value="null">{{ t('common.placeholder_select') }}</option>
          <option v-for="c in courses" :key="c.id" :value="c">{{ c.kode_mk }} — {{ survey.selectedBahasa === 'zh' ? c.nama_zh : c.nama_id }}</option>
        </select>
      </div>

      <div class="form-group" v-if="survey.selectedCourse && lecturers.length">
        <label class="form-label">Dosen Pengampu yang Dievaluasi *</label>
        <select class="form-select" v-model="survey.selectedLecturerId">
          <option :value="null">{{ t('common.placeholder_select') }}</option>
          <option v-for="d in lecturers" :key="d.id" :value="d.id">{{ d.full_name }}</option>
        </select>
      </div>

      <!-- Role: hanya mahasiswa. Dosen punya alur sendiri via /survey/dosen (login) -->
      <div class="form-group">
        <label class="form-label">{{ t('survey.select_role') }}</label>
        <div style="background:#f7fafc; border-radius:8px; padding:10px 14px; font-size:13px; color:#4a5568; border:1px solid #e2e8f0;">
          &#127891; {{ t('survey.role_mahasiswa') }}
          <span style="color:#718096; margin-left:8px;">(Survey ini untuk mahasiswa. Dosen? <router-link to="/login" style="color:#3182ce;">Login di sini</router-link>)</span>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">{{ t('survey.select_language') }}</label>
        <div style="display:flex; gap:12px;">
          <label class="radio-option" :class="{ active: survey.selectedBahasa === 'id' }">
            <input type="radio" v-model="survey.selectedBahasa" value="id" />
            {{ t('survey.lang_id') }}
          </label>
          <label class="radio-option" :class="{ active: survey.selectedBahasa === 'zh' }">
            <input type="radio" v-model="survey.selectedBahasa" value="zh" />
            {{ t('survey.lang_zh') }}
          </label>
        </div>
      </div>

      <button class="btn btn-primary" style="width:100%; margin-top:8px;" :disabled="!canProceed" @click="proceed">
        {{ t('survey.next') }} →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSurveyStore } from '@/stores/survey'
import { publicApi } from '@/api/public'
import type { University, Program, Course } from '@/types'

const { t } = useI18n()
const router = useRouter()
const survey = useSurveyStore()

const universities = ref<University[]>([])
const programs = ref<Program[]>([])
const courses = ref<Course[]>([])
const lecturers = ref<{ id: string; full_name: string }[]>([])

const canProceed = computed(() =>
  !!survey.selectedUniversity && !!survey.selectedProgram && !!survey.selectedCourse &&
  (lecturers.value.length === 0 || !!survey.selectedLecturerId)
)

onMounted(async () => {
  survey.selectedRole = 'mahasiswa'
  survey.isDosen = false
  const { data } = await publicApi.getUniversities()
  universities.value = data.data
})

async function onUnivChange() {
  survey.selectedProgram = null
  survey.selectedCourse = null
  programs.value = []
  courses.value = []
  if (!survey.selectedUniversity) return
  const { data } = await publicApi.getPrograms(survey.selectedUniversity.id)
  programs.value = data.data
}

async function onProgramChange() {
  survey.selectedCourse = null
  survey.selectedLecturerId = null
  courses.value = []
  lecturers.value = []
  if (!survey.selectedProgram) return
  const { data } = await publicApi.getCourses(survey.selectedProgram.id)
  courses.value = data.data
}

async function onCourseChange() {
  survey.selectedLecturerId = null
  lecturers.value = []
  if (!survey.selectedCourse) return
  const { data } = await publicApi.getCourseLecturers(survey.selectedCourse.id)
  lecturers.value = data.data
}

function proceed() {
  if (canProceed.value) router.push({ name: 'survey-consent' })
}
</script>

<style scoped>
.radio-option {
  flex: 1; display: flex; align-items: center; gap: 8px; padding: 10px 14px;
  border: 1.5px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500;
  transition: all .15s;
}
.radio-option.active { border-color: #3182ce; background: #ebf8ff; color: #2b6cb0; }
.radio-option input { display: none; }
</style>
