<script setup lang="ts">
import { computed } from 'vue'
import { serverItem } from '@/game/engine/serverItems'

/** Item card (§17.4 / §15.6): cream card, art, name, category strip (stripes = lethal). */
const props = defineProps<{ item: string; takenByColor?: string; selectable?: boolean }>()

const spec = computed(() => serverItem(props.item))
</script>

<template>
  <button
    type="button"
    class="relative flex h-40 w-35 flex-col overflow-hidden rounded-md border-3 border-tinta bg-creme text-tinta shadow-[0_4px_0_var(--color-sombra-pop)] transition-transform duration-120"
    :class="selectable ? 'hover:-translate-y-2' : 'cursor-default'"
    :disabled="!selectable"
  >
    <span class="grid flex-1 place-items-center p-3">
      <img v-if="spec?.cardImage" :src="`/${spec.cardImage}`" alt="" class="max-h-20 w-[85%] object-contain" draggable="false" />
      <span v-else class="hazard-stripes size-14 rounded-sm border-3 border-tinta" />
    </span>
    <span class="px-2 pb-2 font-label text-base leading-5 font-extrabold tracking-[0.04em] uppercase">
      {{ spec?.label ?? item }}
    </span>
    <span
      class="h-3 w-full border-t-3 border-tinta"
      :class="spec?.category === 'hazard' ? 'hazard-stripes' : 'bg-sprite-madeira'"
    />
    <span
      v-if="takenByColor"
      class="absolute inset-0 grid place-items-center bg-tinta/40"
      aria-label="Já escolhido"
    >
      <span class="size-10 rounded-full border-3 border-tinta" :style="{ background: takenByColor }" />
    </span>
  </button>
</template>

<style scoped>
/* Lethal category stripes (§7): 45°, dark and gold bands of equal width. */
.hazard-stripes {
  background: repeating-linear-gradient(
    45deg,
    var(--color-tinta) 0 6px,
    var(--color-holofote) 6px 12px
  );
}
</style>
