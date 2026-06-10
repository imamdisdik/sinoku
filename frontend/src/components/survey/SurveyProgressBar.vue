<template>
  <div class="progress">
    <div class="progress__steps">
      <div
        v-for="(step, i) in steps"
        :key="step.key"
        :class="['progress__step', {
          'progress__step--done': i < currentIndex,
          'progress__step--active': i === currentIndex,
        }]"
      >
        <div class="step-circle">{{ i + 1 }}</div>
        <div class="step-label">{{ step.label }}</div>
      </div>
    </div>
    <div class="progress__bar">
      <div class="progress__fill" :style="{ width: `${(currentIndex / (steps.length - 1)) * 100}%` }" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = defineProps<{ currentStep: string }>()

const steps = [
  { key: 'B', label: computed(() => t('survey.step_context')).value },
  { key: 'C', label: computed(() => t('survey.step_input')).value },
  { key: 'D', label: computed(() => t('survey.step_process')).value },
  { key: 'E', label: computed(() => t('survey.step_product')).value },
]
const currentIndex = computed(() => steps.findIndex(s => s.key === props.currentStep))
</script>

<style scoped>
.progress { margin-bottom: 28px; }
.progress__steps { display: flex; justify-content: space-between; position: relative; z-index: 1; }
.progress__step { display: flex; flex-direction: column; align-items: center; gap: 6px; flex: 1; }
.step-circle {
  width: 32px; height: 32px; border-radius: 50%; background: #e2e8f0; color: #718096;
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px;
  transition: all .2s;
}
.progress__step--done .step-circle  { background: #48bb78; color: #fff; }
.progress__step--active .step-circle { background: #3182ce; color: #fff; }
.step-label { font-size: 11px; color: #718096; font-weight: 600; }
.progress__step--active .step-label { color: #3182ce; }
.progress__bar { height: 4px; background: #e2e8f0; border-radius: 2px; margin: -20px 16px 0; position: relative; }
.progress__fill { height: 100%; background: #3182ce; border-radius: 2px; transition: width .3s ease; }
</style>
