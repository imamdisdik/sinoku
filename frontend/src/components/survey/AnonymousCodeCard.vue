<template>
  <div class="code-card">
    <div class="code-display">{{ code }}</div>
    <button class="btn btn-outline" @click="copy">
      {{ copied ? t('survey.copied') : t('survey.copy_code') }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
const props = defineProps<{ code: string }>()
const copied = ref(false)
async function copy() {
  await navigator.clipboard.writeText(props.code)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>

<style scoped>
.code-card { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 24px; background: #ebf8ff; border-radius: 12px; border: 2px dashed #3182ce; }
.code-display { font-size: 28px; font-weight: 900; letter-spacing: 4px; color: #2b6cb0; font-family: 'Consolas', monospace; }
</style>
