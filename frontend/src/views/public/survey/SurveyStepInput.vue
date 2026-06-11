<template>
  <div class="container" style="max-width:720px; padding-top:32px;">
    <SurveyProgressBar current-step="C" />
    <div class="card" v-if="stepData">
      <h2 style="font-size:18px; font-weight:800; color:#1a365d; margin:0 0 24px;">
        {{ stepData.nama_dimensi }}
      </h2>

      <div v-for="sd in stepData.sub_dimensions" :key="sd.id" class="sub-dim">
        <h3 class="sub-dim__title">{{ sd.kode }} — {{ sd.nama }}</h3>
        <div v-for="item in sd.items" :key="item.id" class="item-row">
          <div class="item-row__text">
            <span class="item-row__num">{{ item.nomor_urut }}.</span>
            {{ item.teks }}
            <span class="item-required" v-if="item.is_required">*</span>
          </div>
          <LikertScale v-model="answers[item.id]" />
        </div>
      </div>

      <div v-if="stepData.open_questions.length" class="open-section">
        <h3 class="sub-dim__title">Pertanyaan Terbuka</h3>
        <div v-for="q in stepData.open_questions" :key="q.id" class="form-group">
          <label class="form-label">{{ q.pertanyaan }}<span class="item-required" v-if="q.is_required"> *</span></label>
          <textarea class="form-input" rows="3" v-model="openAnswers[q.id]" />
        </div>
      </div>

      <p v-if="!canProceed" class="validation-hint">* Harap isi semua pernyataan yang wajib sebelum melanjutkan.</p>

      <StepNavigation
        :is-first="false"
        :is-last="false"
        :loading="loading"
        :disabled="!canProceed"
        @prev="goBack"
        @next="saveAndNext"
      />
    </div>
    <div v-else class="card" style="text-align:center; color:#718096;">
      {{ t('common.loading') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import { useSurveyStore } from '@/stores/survey'
import { useUiStore } from '@/stores/ui'
import { publicApi } from '@/api/public'
import SurveyProgressBar from '@/components/survey/SurveyProgressBar.vue'
import LikertScale from '@/components/survey/LikertScale.vue'
import StepNavigation from '@/components/survey/StepNavigation.vue'

const { t } = useI18n()
const router = useRouter()
const survey = useSurveyStore()
const ui = useUiStore()
const loading = ref(false)
const { stepData, answers, openAnswers } = storeToRefs(survey)

const canProceed = computed(() => {
  if (!stepData.value) return false
  const likertOk = stepData.value.sub_dimensions
    .flatMap(sd => sd.items)
    .filter(item => item.is_required)
    .every(item => answers.value[item.id] !== undefined)
  const openOk = stepData.value.open_questions
    .filter(q => q.is_required)
    .every(q => !!openAnswers.value[q.id]?.trim())
  return likertOk && openOk
})

onMounted(async () => {
  if (!survey.responseId) return router.push({ name: 'survey' })
  try {
    const { data } = await publicApi.getSurveyItems(survey.responseId, 'C')
    survey.stepData = data
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || t('common.error'), 'error')
  }
})

function goBack() {
  router.push({ name: 'survey-B' })
}

async function saveAndNext() {
  if (!survey.responseId || !canProceed.value) return
  loading.value = true
  try {
    const items = survey.getAnswersForStep('C')
    await publicApi.saveAnswers(survey.responseId, { items, open_answers: [] })
    router.push({ name: 'survey-D' })
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || t('common.error'), 'error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.sub-dim { margin-bottom: 28px; }
.sub-dim__title { font-size: 13px; font-weight: 700; color: #4a5568; text-transform: uppercase; letter-spacing: .05em; margin: 0 0 14px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0; }
.item-row { display: flex; flex-direction: column; gap: 8px; padding: 14px 0; border-bottom: 1px solid #f4f7fb; }
.item-row__text { font-size: 14px; color: #2d3748; line-height: 1.5; }
.item-row__num { font-weight: 700; color: #3182ce; margin-right: 6px; }
.item-required { color: #e53e3e; margin-left: 4px; }
.open-section { margin-top: 28px; padding-top: 20px; border-top: 2px solid #e2e8f0; }
.validation-hint { color: #e53e3e; font-size: 13px; margin-top: 12px; }
</style>
