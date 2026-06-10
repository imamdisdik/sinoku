<template>
  <div class="step-nav">
    <button class="btn btn-outline" @click="emit('prev')" :disabled="isFirst">
      ← {{ t('survey.prev') }}
    </button>
    <slot />
    <button class="btn btn-primary" @click="emit('next')" :disabled="isLast || loading">
      <span v-if="loading">{{ t('common.loading') }}</span>
      <span v-else-if="isLast">{{ t('survey.submit') }}</span>
      <span v-else>{{ t('survey.next') }} →</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
defineProps<{ isFirst?: boolean; isLast?: boolean; loading?: boolean }>()
const emit = defineEmits<{ prev: []; next: [] }>()
</script>

<style scoped>
.step-nav { display: flex; justify-content: space-between; align-items: center; margin-top: 32px; padding-top: 20px; border-top: 1px solid #e2e8f0; }
</style>
