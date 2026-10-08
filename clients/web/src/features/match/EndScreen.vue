<script setup lang="ts">
import { computed } from 'vue'
import GameIcon from '@/components/GameIcon.vue'
import { useMatchStore } from './matchStore'

/** End of the show (§15.11): podium order, winner catchphrase, back to the room. */
defineEmits<{ leave: [] }>()
const match = useMatchStore()

const ranking = computed(() => [...match.players].sort((a, b) => b.score - a.score))
const winner = computed(() => match.players.find((p) => p.playerId === match.winnerId) ?? null)
</script>

<template>
  <div class="absolute inset-0 z-20 grid place-items-center bg-fundo-poco/70 p-8">
    <section class="panel flex w-full max-w-lg flex-col items-center gap-6 text-center">
      <GameIcon name="trophy" :size="48" />
      <h2 class="font-display text-4xl leading-[38px]">{{ winner ? 'É campeão!' : 'Programa sem vencedor!' }}</h2>
      <p v-if="winner" class="font-label text-2xl font-extrabold tracking-[0.04em] uppercase" :style="{ color: match.slotColor(winner.playerId) }">
        {{ winner.username }}
      </p>
      <ol class="flex w-full flex-col gap-2">
        <li
          v-for="(player, index) in ranking"
          :key="player.playerId"
          class="flex items-center justify-between rounded-md border-3 border-tinta bg-fundo-poco px-4 py-2"
        >
          <span class="flex items-center gap-3 font-label text-lg font-extrabold uppercase">
            <span class="font-display text-holofote">{{ index + 1 }}º</span>
            <span class="size-4 rounded-full border-2 border-tinta" :style="{ background: match.slotColor(player.playerId) }" />
            {{ player.username }}
          </span>
          <span class="flex items-center gap-1 font-display tabular-nums"><GameIcon name="star" :size="20" />{{ player.score }}</span>
        </li>
      </ol>
      <div class="flex w-full flex-col gap-3 sm:flex-row">
        <button class="btn btn-primario flex-1" @click="match.clear()"><GameIcon name="replay" :size="20" />Voltar à sala</button>
        <button class="btn btn-fantasma flex-1" @click="$emit('leave')"><GameIcon name="exit" :size="20" />Sair do programa</button>
      </div>
    </section>
  </div>
</template>
