<script setup lang="ts">
import { useToastStore } from '@/store/toasts';

const toasts = useToastStore();
</script>

<template>
  <Teleport to="body">
    <div class="fixed right-4 top-4 z-50 flex w-80 flex-col gap-2">
      <TransitionGroup
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="translate-x-full opacity-0"
        enter-to-class="translate-x-0 opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-for="toast in toasts.liste"
          :key="toast.id"
          class="flex items-start gap-2 rounded-lg border p-3 shadow-lg"
          :class="{
            'border-green-300 bg-green-50 text-green-900 dark:border-green-700 dark:bg-green-900/40 dark:text-green-100':
              toast.typ === 'erfolg',
            'border-red-300 bg-red-50 text-red-900 dark:border-red-700 dark:bg-red-900/40 dark:text-red-100':
              toast.typ === 'fehler',
            'border-slate-300 bg-white text-slate-900 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100':
              toast.typ === 'info',
          }"
          role="status"
        >
          <span class="text-sm">{{ toast.text }}</span>
          <button
            class="ml-auto text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
            aria-label="Schließen"
            @click="toasts.entferne(toast.id)"
          >
            ✕
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
