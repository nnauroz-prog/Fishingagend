<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{ name: string; groesse?: 'klein' | 'mittel' | 'gross' }>(),
  { groesse: 'mittel' },
);

// Konsistenter, leichter Farb-Hash auf Basis des Namens.
function nameHash(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

const initialen = computed(() => {
  const teile = props.name.split(/\s+/).filter(Boolean);
  if (!teile.length) return '?';
  if (teile.length === 1) return teile[0].slice(0, 2).toUpperCase();
  return (teile[0][0] + teile[teile.length - 1][0]).toUpperCase();
});

// Eine kleine Palette aus Tailwind-Tönen, damit es sauber zur App passt.
const palette = [
  ['#fee2e2', '#991b1b'],
  ['#fef3c7', '#92400e'],
  ['#dcfce7', '#166534'],
  ['#cffafe', '#155e75'],
  ['#dbeafe', '#1e40af'],
  ['#ede9fe', '#5b21b6'],
  ['#fce7f3', '#9d174d'],
  ['#f1f5f9', '#334155'],
];

const farben = computed(() => palette[nameHash(props.name) % palette.length]);

const dimension = computed(() => {
  switch (props.groesse) {
    case 'klein':
      return { box: 'h-7 w-7', text: 'text-[10px]' };
    case 'gross':
      return { box: 'h-12 w-12', text: 'text-lg' };
    default:
      return { box: 'h-9 w-9', text: 'text-xs' };
  }
});
</script>

<template>
  <span
    class="inline-grid shrink-0 place-items-center rounded-full font-semibold leading-none"
    :class="[dimension.box, dimension.text]"
    :style="{ backgroundColor: farben[0], color: farben[1] }"
    :title="name"
    :aria-label="name"
  >
    {{ initialen }}
  </span>
</template>
