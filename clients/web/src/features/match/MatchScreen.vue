<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, useTemplateRef, watch } from 'vue'
import EventAlert from '@/components/EventAlert.vue'
import GameIcon from '@/components/GameIcon.vue'
import OnAirSign from '@/components/OnAirSign.vue'
import HudTimer from '@/components/hud/HudTimer.vue'
import PlayerPlate from '@/components/hud/PlayerPlate.vue'
import { useNow } from '@/composables/useNow'
import { useSessionStore } from '@/features/lobby/sessionStore'
import { serverItem } from '@/game/engine/serverItems'
import { OnlineGame } from '@/game/online/onlineGame'
import AudienceMeter from './AudienceMeter.vue'
import EndScreen from './EndScreen.vue'
import ItemOfferCard from './ItemOfferCard.vue'
import { useMatchStore } from './matchStore'

defineEmits<{ leave: [] }>()

const session = useSessionStore()
const match = useMatchStore()
const host = useTemplateRef<HTMLDivElement>('host')
const alert = useTemplateRef<InstanceType<typeof EventAlert>>('alert')
const now = useNow()
const placed = ref(false)
let game: OnlineGame | null = null

const PHASE_LABEL = { pick: 'Roleta', place: 'Montagem', run: 'No ar', score: 'Resultado', end: 'Fim' } as const

const myId = computed(() => session.playerId ?? '')
const myItem = computed(() => match.heldItems[myId.value] ?? null)
const iPicked = computed(() => myItem.value !== null)
const secondsLeft = computed(() => Math.max(0, (match.phaseEndsAt - now.value) / 1000))

onMounted(async () => {
  if (!host.value || !match.level) return
  game = new OnlineGame(session.socket, myId.value, match.level, match.players)
  game.onEvent((event) => {
    if (event === 'died') alert.value?.show('Caiu, perdeu!')
    else if (event === 'finished') alert.value?.show('Chegou!')
    else placed.value = true
  })
  await game.mount(host.value)
  syncGame()
})

function syncGame(): void {
  game?.setPhase(match.phase, placed.value ? null : myItem.value)
}

watch(() => match.phase, (phase) => {
  placed.value = false
  if (phase === 'run') alert.value?.show('Tá no ar!')
  syncGame()
})
watch(myItem, syncGame)
// A rejected placement comes back as an error: let the player try again.
watch(() => session.lastError, () => {
  if (match.phase === 'place' && placed.value) {
    placed.value = false
    syncGame()
  }
})

function pick(offerId: number): void {
  session.socket.send({ type: 'pick_item', offer_id: offerId })
}

onBeforeUnmount(() => game?.destroy())
</script>

<template>
  <div class="relative h-dvh w-full overflow-hidden bg-fundo select-none">
    <div ref="host" class="absolute inset-0" :class="{ 'cursor-crosshair': match.phase === 'place' && iPicked && !placed }" />
    <EventAlert ref="alert" />

    <!-- Top HUD (§16) -->
    <header class="pointer-events-none absolute inset-x-0 top-0 grid grid-cols-[1fr_auto_1fr] items-start gap-4 p-8">
      <span class="chip w-fit">Rodada {{ match.round }}</span>
      <div class="flex flex-col items-center gap-2">
        <OnAirSign size="sm" :lit="match.phase === 'run'" />
        <span v-if="match.phase" class="chip">{{ PHASE_LABEL[match.phase] }}</span>
      </div>
      <div class="flex justify-end">
        <HudTimer v-if="match.phase && match.phase !== 'end'" :seconds="secondsLeft" countdown />
      </div>
    </header>

    <!-- Prize wheel showcase (§15.6) -->
    <div v-if="match.phase === 'pick'" class="absolute inset-0 grid place-items-center bg-fundo-poco/50 p-8">
      <div class="flex flex-col items-center gap-6">
        <h2 class="font-display text-4xl leading-[38px]">{{ iPicked ? 'Esperando o resto do elenco…' : 'Escolha seu item' }}</h2>
        <div class="flex flex-wrap justify-center gap-4">
          <ItemOfferCard
            v-for="offer in match.offers"
            :key="offer.offer_id"
            :item="offer.item"
            :taken-by-color="offer.taken_by ? match.slotColor(offer.taken_by) : undefined"
            :selectable="!iPicked && !offer.taken_by"
            @click="pick(offer.offer_id)"
          />
        </div>
      </div>
    </div>

    <!-- Build phase hint (§15.7) -->
    <div v-if="match.phase === 'place'" class="pointer-events-none absolute inset-x-0 bottom-28 flex justify-center">
      <p v-if="myItem && !placed" class="chip flex items-center gap-2 text-base">
        <GameIcon name="key" :size="20" />
        {{ serverItem(myItem)?.label ?? myItem }} · [clique] colocar
      </p>
      <p v-else class="chip text-base text-texto-suave">Esperando o resto do elenco…</p>
    </div>

    <AudienceMeter v-if="match.phase === 'score'" />
    <EndScreen v-if="match.ended" @leave="$emit('leave')" />

    <!-- Player plates -->
    <footer class="pointer-events-none absolute inset-x-0 bottom-0 flex flex-wrap justify-center gap-3 p-6">
      <PlayerPlate
        v-for="player in match.players"
        :key="player.playerId"
        :slot="player.slot"
        :name="player.username"
        :score="player.score"
      />
    </footer>
  </div>
</template>
