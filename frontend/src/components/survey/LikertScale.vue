<template>
  <div class="likert">
    <div class="likert__labels">
      <span>{{ t('survey.likert_1') }}</span>
      <span>{{ t('survey.likert_5') }}</span>
    </div>
    <div class="likert__buttons">
      <button
        v-for="n in 5"
        :key="n"
        :class="['likert__btn', { selected: modelValue === n }]"
        @click="emit('update:modelValue', n)"
        :aria-label="`Pilih ${n}`"
      >
        {{ n }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
defineProps<{ modelValue?: number }>()
const emit = defineEmits<{ 'update:modelValue': [n: number] }>()
</script>

<style scoped>
.likert { margin: 4px 0; }
.likert__labels { display: flex; justify-content: space-between; font-size: 11px; color: #718096; margin-bottom: 6px; }
.likert__buttons { display: flex; gap: 8px; }
.likert__btn {
  width: 42px; height: 42px; border-radius: 50%; border: 2px solid #e2e8f0;
  font-size: 15px; font-weight: 700; background: #fff; color: #4a5568;
  transition: all .15s; flex-shrink: 0;
}
.likert__btn:hover { border-color: #3182ce; color: #3182ce; }
.likert__btn.selected { background: #3182ce; border-color: #3182ce; color: #fff; }
</style>
