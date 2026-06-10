<template>
  <div class="container" style="max-width:700px; padding-top:40px;">
    <!-- Form cari kode -->
    <div class="card" style="margin-bottom:24px;">
      <h1 style="font-size:20px; font-weight:800; color:#1a365d; margin:0 0 16px;">{{ t('result.title') }}</h1>
      <div style="display:flex; gap:12px;">
        <input class="form-input" v-model="kode" :placeholder="t('result.code_placeholder')" style="flex:1;" @keyup.enter="search" />
        <button class="btn btn-primary" @click="search" :disabled="!kode || loading">
          {{ loading ? t('common.loading') : t('result.search') }}
        </button>
      </div>
      <p v-if="error" style="color:#e53e3e; font-size:13px; margin-top:8px;">{{ error }}</p>
    </div>

    <!-- Hasil -->
    <div v-if="result" class="card">
      <div style="margin-bottom:20px;">
        <div style="font-size:12px; color:#718096;">{{ result.course.kode_mk }}</div>
        <div style="font-size:18px; font-weight:700;">{{ result.course.nama_id }}</div>
        <div style="font-size:12px; color:#718096; margin-top:4px;">
          Peran: {{ result.role }} | Bahasa: {{ result.bahasa }} |
          Submit: {{ new Date(result.submitted_at).toLocaleDateString('id-ID') }}
        </div>
      </div>

      <h3 style="font-size:14px; font-weight:700; color:#4a5568; margin:0 0 12px;">{{ t('result.cipp_score') }}</h3>
      <div class="score-grid">
        <div v-for="s in result.cipp_scores" :key="s.kode" class="score-card">
          <div class="score-card__kode">{{ s.kode }}</div>
          <div class="score-card__name">{{ s.dimensi }}</div>
          <div class="score-card__score">{{ s.skor_rata.toFixed(2) }}</div>
          <div class="score-card__bar">
            <div class="score-fill" :style="{ width: `${(s.skor_rata / 5) * 100}%` }" />
          </div>
          <div class="score-card__n">n={{ s.jumlah_item }}</div>
        </div>
      </div>

      <div v-if="result.open_answers.length" style="margin-top:24px;">
        <h3 style="font-size:14px; font-weight:700; color:#4a5568; margin:0 0 12px;">{{ t('result.open_answers') }}</h3>
        <div v-for="(oa, i) in result.open_answers" :key="i" style="margin-bottom:14px; padding:12px; background:#f7fafc; border-radius:8px;">
          <div style="font-size:13px; font-weight:600; color:#2d3748; margin-bottom:6px;">{{ oa.pertanyaan }}</div>
          <div style="font-size:13px; color:#4a5568;">{{ oa.jawaban }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { publicApi } from '@/api/public'

const { t } = useI18n()
const kode = ref('')
const loading = ref(false)
const error = ref('')
const result = ref<any>(null)

async function search() {
  if (!kode.value.trim()) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const { data } = await publicApi.getResult(kode.value.trim().toUpperCase())
    result.value = data
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('common.error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.score-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
.score-card { background: #f7fafc; border-radius: 10px; padding: 14px; text-align: center; border: 1px solid #e2e8f0; }
.score-card__kode { font-size: 20px; font-weight: 900; color: #3182ce; }
.score-card__name { font-size: 11px; color: #718096; margin: 2px 0 8px; }
.score-card__score { font-size: 26px; font-weight: 800; color: #2d3748; }
.score-card__bar { height: 4px; background: #e2e8f0; border-radius: 2px; margin: 8px 0; }
.score-fill { height: 100%; background: #3182ce; border-radius: 2px; }
.score-card__n { font-size: 11px; color: #a0aec0; }
</style>
