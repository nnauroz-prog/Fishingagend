<script setup lang="ts">
import { computed } from 'vue';

import type { FeedBeitrag, Folge } from '@/api/typen';

const props = defineProps<{
  feed: FeedBeitrag[];
  folgen: Folge[];
  welt?: 'kontrolle' | 'variante';
}>();

const gefiltert = computed(() =>
  props.welt ? props.feed.filter((b) => b.welt === props.welt) : props.feed,
);

const gefiltertFolgen = computed(() =>
  props.welt ? props.folgen.filter((f) => f.welt === props.welt) : props.folgen,
);

const reaktionsIcon: Record<string, string> = {
  like: '♡',
  antwort: '↩',
  repost: '↻',
};
</script>

<template>
  <div class="space-y-4">
    <div v-if="!gefiltert.length" class="text-sm text-slate-500">
      Noch keine Beiträge in dieser Welt.
    </div>

    <article
      v-for="b in gefiltert"
      :key="b.id"
      class="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800"
    >
      <header class="mb-2 flex items-center justify-between text-xs text-slate-500">
        <div class="flex items-center gap-2">
          <span class="grid h-7 w-7 place-items-center rounded-full bg-markenblau-100 text-xs font-semibold text-markenblau-700 dark:bg-slate-700 dark:text-slate-200">
            {{ b.autor.charAt(0) }}
          </span>
          <span class="font-semibold text-slate-900 dark:text-slate-100">{{ b.autor }}</span>
          <span>· Schritt {{ b.schritt_nr }}</span>
          <span
            v-if="!welt"
            class="rounded-full px-2 py-0.5"
            :class="b.welt === 'kontrolle' ? 'bg-slate-100 dark:bg-slate-700' : 'bg-markenblau-50 text-markenblau-700 dark:bg-slate-700 dark:text-markenblau-300'"
          >
            {{ b.welt }}
          </span>
        </div>
        <span class="font-mono text-[10px]">#{{ b.id }}</span>
      </header>

      <p class="whitespace-pre-wrap text-sm">{{ b.inhalt }}</p>

      <ul v-if="b.reaktionen.length" class="mt-3 space-y-1 border-t border-slate-100 pt-2 text-xs dark:border-slate-700">
        <li
          v-for="(r, i) in b.reaktionen"
          :key="i"
          class="flex items-start gap-2 text-slate-600 dark:text-slate-300"
        >
          <span class="text-base">{{ reaktionsIcon[r.typ] }}</span>
          <span>
            <strong>{{ r.autor }}</strong>
            <span v-if="r.typ === 'antwort' && r.inhalt"> antwortet: „{{ r.inhalt }}“</span>
            <span v-else-if="r.typ === 'like'"> hat das geliked</span>
            <span v-else> reposted</span>
            <span class="ml-1 text-slate-400">· #{{ r.schritt_nr }}</span>
          </span>
        </li>
      </ul>
    </article>

    <details v-if="gefiltertFolgen.length" class="rounded border border-slate-200 p-3 dark:border-slate-700">
      <summary class="cursor-pointer text-xs uppercase text-slate-500">
        Folge-Beziehungen ({{ gefiltertFolgen.length }})
      </summary>
      <ul class="mt-2 space-y-1 text-xs">
        <li v-for="(f, i) in gefiltertFolgen" :key="i">
          <strong>{{ f.folger }}</strong> folgt
          <strong>{{ f.gefolgter }}</strong>
          <span class="text-slate-400"> · Schritt {{ f.schritt_nr }}</span>
        </li>
      </ul>
    </details>
  </div>
</template>
