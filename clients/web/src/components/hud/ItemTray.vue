<script setup lang="ts">
import type { SandboxItem } from '@/game/sandbox/sandboxGame'

/** Item cards for the build phase (§17.4): cream card, centered art, category strip below. */
defineProps<{ items: SandboxItem[]; selected: string }>()
defineEmits<{ select: [key: string] }>()

const LABELS: Record<string, string> = {
  praticavel: 'Praticável',
  'praticavel-longo': 'Praticável longo',
}
</script>

<template>
  <div class="flex gap-3">
    <button
      v-for="(item, index) in items"
      :key="item.key"
      class="group relative flex h-40 w-35 flex-col overflow-hidden rounded-md border-3 border-tinta bg-creme text-tinta shadow-[0_4px_0_var(--color-sombra-pop)] transition-transform duration-120 hover:-translate-y-2"
      :class="{ '-translate-y-2 outline-3 outline-offset-3 outline-foco': item.key === selected }"
      @click="$emit('select', item.key)"
    >
      <span class="absolute top-1 left-2 font-label text-sm font-extrabold">{{ index + 1 }}</span>
      <img :src="item.image" alt="" class="m-auto max-h-20 w-[80%] object-contain" draggable="false" />
      <span class="px-2 pb-2 font-label text-base leading-5 font-extrabold tracking-[0.04em] uppercase">
        {{ LABELS[item.key] ?? item.key }}
      </span>
      <!-- Structure category strip: wood (never stripes, §7). -->
      <span class="h-3 w-full border-t-3 border-tinta bg-sprite-madeira" />
    </button>
  </div>
</template>
