<script setup lang="ts">
import { computed } from 'vue'
import GameIcon from '@/components/GameIcon.vue'
import { useMatchStore } from './matchStore'

/** Round results (§15.9): one bar per player in their color, gained points as labeled segments. */
const match = useMatchStore()

const REASONS: Record<string, string> = {
  goal: 'Chegou',
  first: 'Primeiro a chegar',
  solo: 'Exclusiva!',
  viral: 'Momento viral!',
}

const rows = computed(() =>
  match.players.map((player) => {
    const line = match.roundScores.find((s) => s.player_id === player.playerId)
    return {
      ...player,
      gained: line?.gained ?? 0,
      reasons: line?.reasons ?? [],
      color: match.slotColor(player.playerId),
      width: Math.min(100, (player.score / Math.max(1, match.targetScore)) * 100),
    }
  }),
)
const nobodyScored = computed(() => rows.value.every((r) => r.gained === 0))
</script>

<template>
  <div class="absolute inset-0 z-10 grid place-items-center bg-fundo-poco/60 p-8">
    <section class="panel w-full max-w-2xl">
      <h2 class="mb-6 text-center font-display text-4xl leading-[38px]">Audiência</h2>
      <p v-if="nobodyScored" class="mb-6 text-center text-texto-suave">A audiência despencou! Ninguém pontua.</p>
      <ul class="flex flex-col gap-4">
        <li v-for="row in rows" :key="row.playerId" class="flex flex-col gap-1">
          <div class="flex items-center justify-between font-label text-base font-extrabold tracking-[0.06em] uppercase">
            <span>{{ row.username }}</span>
            <span class="flex items-center gap-1 font-display text-xl tabular-nums">
              <GameIcon name="star" :size="20" />{{ row.score }}
              <span v-if="row.gained" class="text-holofote">+{{ row.gained }}</span>
            </span>
          </div>
          <div class="relative h-6 overflow-hidden rounded-pill border-3 border-tinta bg-fundo-poco">
            <div class="h-full transition-[width] duration-500" :style="{ width: `${row.width}%`, background: row.color }" />
            <!-- Finish line with trophy marks the target score -->
            <GameIcon name="trophy" :size="20" class="absolute top-1/2 right-1 -translate-y-1/2" />
          </div>
          <div class="flex flex-wrap gap-1">
            <span v-for="reason in row.reasons" :key="reason" class="chip bg-holofote text-tinta">
              {{ REASONS[reason] ?? reason }}
            </span>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>
