<template>
  <div class="container" style="max-width:600px; padding-top:40px;">
    <div class="card">
      <h1 style="font-size:20px; font-weight:800; margin:0 0 16px; color:#1a365d;">
        {{ t('survey.consent_title') }}
      </h1>
      <p style="color:#4a5568; line-height:1.7; margin-bottom:24px;">{{ t('survey.consent_text') }}</p>
      <div style="background:#f7fafc; border-radius:8px; padding:16px; margin-bottom:24px; font-size:13px; color:#718096;">
        <strong style="color:#2d3748;">Universitas:</strong> {{ survey.selectedUniversity?.nama }}<br/>
        <strong style="color:#2d3748;">Program Studi:</strong> {{ survey.selectedProgram?.nama }}<br/>
        <strong style="color:#2d3748;">Mata Kuliah:</strong>
          {{ survey.selectedBahasa === 'zh' ? survey.selectedCourse?.nama_zh : survey.selectedCourse?.nama_id }}<br/>
        <strong style="color:#2d3748;">Peran:</strong>
          {{ survey.selectedRole === 'dosen' ? t('survey.role_dosen') : t('survey.role_mahasiswa') }}<br/>
        <strong style="color:#2d3748;">Bahasa:</strong>
          {{ survey.selectedBahasa === 'id' ? t('survey.lang_id') : t('survey.lang_zh') }}
      </div>
      <div style="display:flex; gap:12px;">
        <button class="btn btn-outline" @click="router.back()">{{ t('survey.prev') }}</button>
        <button class="btn btn-primary" style="flex:1;" @click="proceed" :disabled="loading">
          {{ loading ? t('common.loading') : t('survey.consent_agree') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSurveyStore } from '@/stores/survey'
import { useUiStore } from '@/stores/ui'
import { publicApi } from '@/api/public'

const { t } = useI18n()
const router = useRouter()
const survey = useSurveyStore()
const ui = useUiStore()
const loading = ref(false)

async function proceed() {
  if (!survey.selectedCourse || !survey.selectedUniversity) return
  loading.value = true
  try {
    const body = {
      course_id: survey.selectedCourse.id,
      role: survey.selectedRole,
      bahasa: survey.selectedBahasa,
      university_id: survey.selectedUniversity.id,
      program_id: survey.selectedProgram?.id ?? null,
    }
    const { data } = await publicApi.startSurvey(body)
    survey.responseId = data.response_id
    survey.respondentId = data.respondent_id
    router.push({ name: 'survey-B' })
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || t('common.error'), 'error')
  } finally {
    loading.value = false
  }
}
</script>
