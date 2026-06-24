<template>
  <div class="container" style="max-width:520px; padding-top:60px; text-align:center;">
    <div class="card">
      <div class="check-icon">&#10003;</div>
      <h1 style="font-size:24px; font-weight:800; color:#1a365d; margin:16px 0 8px;">
        {{ t('survey.thankyou_title') }}
      </h1>
      <p style="color:#718096; margin-bottom:28px;">{{ t('survey.thankyou_desc') }}</p>
      <!-- Mahasiswa: tampilkan kode anonim -->
      <template v-if="!survey.isDosen">
        <AnonymousCodeCard v-if="survey.anonymousCode" :code="survey.anonymousCode" />
        <div style="margin-top:24px; display:flex; gap:12px; justify-content:center;">
          <RouterLink to="/result" class="btn btn-outline">{{ t('result.title') }}</RouterLink>
          <RouterLink to="/" class="btn btn-primary">{{ t('nav.home') }}</RouterLink>
        </div>
      </template>
      <!-- Dosen: tombol kembali ke dashboard -->
      <template v-else>
        <p style="color:#4a5568; font-size:14px; margin-bottom:24px;">
          Evaluasi Anda telah tersimpan dan dapat dilihat di dashboard.
        </p>
        <div style="display:flex; gap:12px; justify-content:center;">
          <RouterLink to="/admin" class="btn btn-primary">Kembali ke Dashboard</RouterLink>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useSurveyStore } from '@/stores/survey'
import AnonymousCodeCard from '@/components/survey/AnonymousCodeCard.vue'

const { t } = useI18n()
const survey = useSurveyStore()
</script>

<style scoped>
.check-icon {
  width: 64px; height: 64px; background: #48bb78; color: #fff;
  border-radius: 50%; font-size: 32px; display: flex; align-items: center;
  justify-content: center; margin: 0 auto;
}
</style>
