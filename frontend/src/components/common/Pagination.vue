<template>
  <div v-if="totalPages > 1" class="pagination">
    <button :disabled="page <= 1" @click="go(page - 1)">&#8592;</button>
    <span>Halaman {{ page }} dari {{ totalPages }}</span>
    <button :disabled="page >= totalPages" @click="go(page + 1)">&#8594;</button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ page: number; totalPages: number }>()
const emit = defineEmits<{ 'update:page': [number] }>()
function go(p: number) {
  if (p >= 1 && p <= props.totalPages) emit('update:page', p)
}
</script>

<style scoped>
.pagination { display: flex; align-items: center; gap: 12px; padding: 16px 0; font-size: 13px; color: #718096; }
.pagination button { padding: 6px 12px; border: 1px solid #e2e8f0; background: #fff; border-radius: 6px; cursor: pointer; }
.pagination button:disabled { opacity: .4; cursor: not-allowed; }
</style>
