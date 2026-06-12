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
        <strong style="color:#2d3748;">Peran:</strong> Mahasiswa<br/>
        <strong style="color:#2d3748;">Bahasa:</strong>
          {{ survey.selectedBahasa === 'id' ? t('survey.lang_id') : t('survey.lang_zh') }}
      </div>

      <!-- Poin kesepakatan -->
      <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:14px; margin-bottom:24px; font-size:13px; color:#78350f;">
        <strong>Dengan menyetujui, Anda menyatakan:</strong>
        <ul style="margin:8px 0 0 16px; line-height:1.8;">
          <li>Data yang diisi adalah benar dan jujur</li>
          <li>Data akan digunakan hanya untuk keperluan penelitian akademik</li>
          <li>Identitas Anda terlindungi — survei bersifat anonim</li>
          <li>Anda berhak menghentikan pengisian kapan saja</li>
        </ul>
      </div>

      <div style="display:flex; gap:12px;">
        <button class="btn btn-outline" @click="router.push({ name: 'survey' })">{{ t('survey.prev') }}</button>
        <button class="btn btn-primary" style="flex:1;" @click="proceed">
          {{ t('survey.consent_agree') }} →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSurveyStore } from '@/stores/survey'

const { t } = useI18n()
const router = useRouter()
const survey = useSurveyStore()

function proceed() {
  if (!survey.selectedCourse || !survey.selectedUniversity) {
    router.push({ name: 'survey' })
    return
  }
  router.push({ name: 'survey-profile' })
}
</script>
