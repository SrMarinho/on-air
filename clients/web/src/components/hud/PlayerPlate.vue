<script setup lang="ts">
import { computed } from 'vue'
import GameIcon from '@/components/GameIcon.vue'
import { tokens } from '@/design/tokens'

/** Bottom HUD plate (§16, §17.5): player shape + color, name, score and state. */
const props = defineProps<{
  slot: number
  name: string
  score: number
  state?: 'alive' | 'finished' | 'eliminated'
}>()

const player = computed(() => tokens.players.find((p) => p.slot === props.slot) ?? tokens.players[0]!)
const SHAPES: Record<string, string> = {
  circle: 'rounded-full',
  triangle: '[clip-path:polygon(50%_6%,96%_92%,4%_92%)]',
  square: 'rounded-[6px]',
  diamond: 'rotate-45 scale-75 rounded-[4px]',
}
</script>

<template>
  <div
    class="flex items-center gap-3 rounded-lg border-3 border-tinta bg-fundo-elevado p-2 pr-4 shadow-[0_4px_0_var(--color-sombra-pop)]"
    :class="{ 'opacity-60 grayscale': state === 'eliminated' }"
  >
    <span class="size-10 border-3 border-tinta" :class="SHAPES[player.shape]" :style="{ background: player.color }" />
    <div class="flex flex-col gap-1">
      <span
        class="rounded-sm px-2 font-label text-base leading-[18px] font-extrabold tracking-[0.06em] text-tinta uppercase"
        :style="{ background: player.color }"
      >
        {{ name }}
      </span>
      <span class="flex items-center gap-1 font-display text-xl leading-none tabular-nums">
        <GameIcon name="star" :size="20" />{{ score }}
        <GameIcon v-if="state === 'finished'" name="check" :size="20" class="ml-1" />
        <GameIcon v-if="state === 'eliminated'" name="gong" :size="20" class="ml-1" />
      </span>
    </div>
  </div>
</template>
