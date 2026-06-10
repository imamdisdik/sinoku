<template>
  <div class="landing">
    <!-- Hero -->
    <section class="hero">
      <div class="container hero__content">
        <h1 class="hero__title">{{ t('landing.hero_title') }}</h1>
        <p class="hero__subtitle">{{ t('landing.hero_subtitle') }}</p>
        <div class="hero__actions">
          <RouterLink to="/survey" class="btn btn-primary">{{ t('landing.start_survey') }}</RouterLink>
          <RouterLink to="/result" class="btn btn-outline" style="color:#fff;border-color:#fff">{{ t('landing.view_result') }}</RouterLink>
        </div>
        <!-- Stats -->
        <div class="stats" v-if="stats">
          <div class="stat">
            <div class="stat__num">{{ stats.total_universities }}</div>
            <div class="stat__lbl">{{ t('landing.stats_universities') }}</div>
          </div>
          <div class="stat">
            <div class="stat__num">{{ stats.total_respondents }}</div>
            <div class="stat__lbl">{{ t('landing.stats_respondents') }}</div>
          </div>
          <div class="stat">
            <div class="stat__num">{{ stats.total_courses_evaluated }}</div>
            <div class="stat__lbl">{{ t('landing.stats_courses') }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CIPP Penjelasan -->
    <section class="cipp-section container">
      <h2 class="section-title">Metodologi Evaluasi CIPP</h2>
      <div class="cipp-grid">
        <div v-for="dim in cippDims" :key="dim.kode" class="cipp-card" :style="{ borderTopColor: dim.color }">
          <div class="cipp-card__kode" :style="{ background: dim.color }">{{ dim.kode }}</div>
          <div class="cipp-card__name">{{ dim.name }}</div>
          <div class="cipp-card__desc">{{ dim.desc }}</div>
        </div>
      </div>
    </section>

    <!-- Universitas -->
    <section class="univ-section container" v-if="universities.length">
      <h2 class="section-title">Universitas Mitra</h2>
      <div class="univ-grid">
        <div v-for="u in universities" :key="u.id" class="univ-card">
          <div class="univ-card__singkat">{{ u.nama_singkat }}</div>
          <div class="univ-card__nama">{{ u.nama }}</div>
          <div class="univ-card__kota">{{ u.kota }}, {{ u.provinsi }}</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { publicApi } from '@/api/public'
import type { University } from '@/types'

const { t } = useI18n()
const stats = ref<any>(null)
const universities = ref<University[]>([])

const cippDims = [
  { kode: 'C', name: 'Context / Konteks', color: '#3182CE', desc: 'Relevansi program terhadap kebutuhan masyarakat dan kebijakan pendidikan' },
  { kode: 'I', name: 'Input / Masukan',   color: '#38A169', desc: 'Kualitas sumber daya, kurikulum, kompetensi dosen, dan fasilitas' },
  { kode: 'P', name: 'Process / Proses',  color: '#D69E2E', desc: 'Pelaksanaan pembelajaran, interaksi, dan strategi pengajaran' },
  { kode: 'P', name: 'Product / Produk',  color: '#E53E3E', desc: 'Capaian kompetensi, sikap budaya, dan dampak program' },
]

onMounted(async () => {
  try {
    const { data } = await publicApi.getLandingData()
    stats.value = data
    universities.value = data.universities || []
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 100%);
  color: #fff; padding: 80px 0 60px;
}
.hero__content { text-align: center; }
.hero__title { font-size: 32px; font-weight: 800; margin: 0 0 16px; line-height: 1.2; }
.hero__subtitle { font-size: 16px; color: rgba(255,255,255,.85); max-width: 600px; margin: 0 auto 32px; }
.hero__actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-bottom: 40px; }
.stats { display: flex; gap: 40px; justify-content: center; flex-wrap: wrap; }
.stat { text-align: center; }
.stat__num { font-size: 36px; font-weight: 800; }
.stat__lbl { font-size: 12px; opacity: .8; margin-top: 4px; }

.section-title { font-size: 22px; font-weight: 700; color: #1a365d; margin: 40px 0 20px; }
.cipp-section { padding-bottom: 40px; }
.cipp-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
.cipp-card { background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.08); border-top: 4px solid #e2e8f0; }
.cipp-card__kode { display: inline-block; color: #fff; width: 36px; height: 36px; border-radius: 8px; font-size: 18px; font-weight: 800; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
.cipp-card__name { font-size: 14px; font-weight: 700; color: #2d3748; margin-bottom: 8px; }
.cipp-card__desc { font-size: 12px; color: #718096; line-height: 1.5; }

.univ-section { padding-bottom: 60px; }
.univ-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
.univ-card { background: #fff; border-radius: 8px; padding: 14px; border: 1px solid #e2e8f0; }
.univ-card__singkat { font-size: 18px; font-weight: 800; color: #2b6cb0; margin-bottom: 4px; }
.univ-card__nama { font-size: 12px; color: #2d3748; font-weight: 500; margin-bottom: 4px; }
.univ-card__kota { font-size: 11px; color: #718096; }
</style>
