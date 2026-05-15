<script setup lang="ts">
defineProps<{ modelValue: string; platzhalter?: string }>();
defineEmits<{ 'update:modelValue': [string] }>();
</script>

<template>
  <div class="relative">
    <input
      :value="modelValue"
      type="search"
      class="eingabe pl-9"
      :placeholder="platzhalter"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">⌕</span>
  </div>
</template>
