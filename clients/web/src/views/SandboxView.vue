<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, useTemplateRef } from 'vue'
import { useRouter } from 'vue-router'
import meadow from '@levels/meadow.json'
import EventAlert from '@/components/EventAlert.vue'
import GameIcon from '@/components/GameIcon.vue'
import OnAirSign from '@/components/OnAirSign.vue'
import HudTimer from '@/components/hud/HudTimer.vue'
import ItemTray from '@/components/hud/ItemTray.vue'
import PauseOverlay from '@/components/hud/PauseOverlay.vue'
import PlayerPlate from '@/components/hud/PlayerPlate.vue'
import { SandboxGame, type SandboxEvent, type SandboxState } from '@/game/sandbox/sandboxGame'

const router = useRouter()
const host = useTemplateRef<HTMLDivElement>('host')
const alert = useTemplateRef<InstanceType<typeof EventAlert>>('alert')
const loading = ref(true)
const finishes = ref(0)
const falls = ref(0)
const seconds = ref(0)
const lastResult = ref<'alive' | 'finished' | 'eliminated'>('alive')
const state = ref<SandboxState>({ mode: 'run', selectedItem: '', items: [] })
const game = new SandboxGame()

/** Official catchphrases (design system §2). */
const catchphrases: Partial<Record<SandboxEvent, string>> = {
  died: 'Caiu, perdeu!',
  finished: 'É campeão!',
}

onMounted(async () => {
  if (!host.value) return
  game.listen({
    event(event) {
      const text = catchphrases[event]
      if (text) alert.value?.show(text)
      if (event === 'died') {
        falls.value++
        lastResult.value = 'eliminated'
      } else if (event === 'finished') {
        finishes.value++
        lastResult.value = 'finished'
      }
    },
    state: (next) => (state.value = next),
    clock: (s) => (seconds.value = s),
  })
  await game.mount(host.value, {
    key: 'meadow',
    width: meadow.rows[0]?.length ?? 0,
    height: meadow.rows.length,
    tileSize: meadow.tile_size,
    rows: meadow.rows,
  })
  loading.value = false
  alert.value?.show('Tá no ar!')
})

onBeforeUnmount(() => game.destroy())
</script>

<template>
  <div class="relative h-dvh w-full overflow-hidden bg-fundo select-none">
    <div ref="host" class="absolute inset-0" :class="{ 'cursor-crosshair': state.mode === 'build' }" />
    <p v-if="loading" class="absolute inset-0 grid place-items-center font-label text-sm tracking-[0.08em] uppercase">
      Entrando no ar…
    </p>
    <EventAlert ref="alert" />

    <!-- Top HUD (§16) -->
    <header class="pointer-events-none absolute inset-x-0 top-0 grid grid-cols-[1fr_auto_1fr] items-start gap-4 p-8">
      <div class="flex items-center gap-2">
        <span class="chip">{{ state.mode === 'build' ? 'Montagem' : 'Treino' }}</span>
      </div>
      <div class="flex flex-col items-center gap-2">
        <OnAirSign size="sm" :lit="state.mode === 'run'" />
      </div>
      <div class="pointer-events-auto flex items-center justify-end gap-2">
        <HudTimer :seconds="seconds" />
        <button class="btn btn-secundario size-13 !px-0" title="Pausar [Esc]" @click="game.togglePause()">
          <GameIcon name="pause" :size="24" />
        </button>
      </div>
    </header>

    <!-- Bottom HUD -->
    <footer class="pointer-events-none absolute inset-x-0 bottom-0 flex items-end justify-between gap-4 p-8">
      <div class="flex flex-col gap-2">
        <PlayerPlate :slot="1" name="Calouro" :score="finishes" :state="lastResult" />
        <span class="chip w-fit text-texto-suave">Quedas {{ falls }}</span>
      </div>

      <div v-if="state.mode === 'build'" class="pointer-events-auto flex flex-col items-center gap-3">
        <ItemTray :items="state.items" :selected="state.selectedItem" @select="game.selectItem($event)" />
        <p class="flex items-center gap-2 font-label text-sm font-extrabold tracking-[0.08em] text-texto-suave uppercase">
          [1-{{ state.items.length }}] escolher · [clique] colocar · [B] voltar a correr
        </p>
      </div>
      <p v-else class="hidden pb-2 text-center font-label text-sm font-extrabold tracking-[0.08em] text-texto-suave uppercase md:block">
        [← →] mover · [↑ / espaço] pular · [B] montar cenário · [Esc] pausar
      </p>

      <div class="pointer-events-auto flex gap-2">
        <button class="btn btn-secundario" title="Montar cenário [B]" @click="game.toggleBuild()">
          <GameIcon :name="state.mode === 'build' ? 'play' : 'key'" :size="20" />
          {{ state.mode === 'build' ? 'Correr' : 'Montar' }}
        </button>
        <button class="btn btn-fantasma" title="Mostrar caixa de colisão" @click="game.toggleHitbox()">Hitbox</button>
      </div>
    </footer>

    <PauseOverlay v-if="state.mode === 'paused'" @resume="game.togglePause()" @exit="router.push('/')" />
  </div>
</template>
