<script setup lang="ts">
import { computed } from 'vue'
import GameIcon from '@/components/GameIcon.vue'

/** HUD timer pill (§16): `placar` digits, tabular; red + pulse in the last 10s of a countdown. */
const props = defineProps<{ seconds: number; countdown?: boolean }>()

const label = computed(() => {
  const s = Math.max(0, Math.floor(props.seconds))
  return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`
})
const urgent = computed(() => props.countdown && props.seconds <= 10)
</script>

<template>
  <div
    class="flex items-center gap-2 rounded-pill border-3 border-tinta bg-fundo-elevado py-1 pr-4 pl-2 shadow-[0_4px_0_var(--color-sombra-pop)]"
    :class="{ 'animate-pulse': urgent }"
  >
    <GameIcon name="timer" :size="32" />
    <span class="font-display text-[28px] leading-none tabular-nums" :class="urgent ? 'text-no-ar-brilho' : 'text-texto'">
      {{ label }}
    </span>
  </div>
</template>
