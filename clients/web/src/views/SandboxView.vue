<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, useTemplateRef } from 'vue'
import meadow from '@levels/meadow.json'
import EventAlert from '@/components/EventAlert.vue'
import { SandboxGame, type SandboxEvent } from '@/game/sandbox/sandboxGame'

const host = useTemplateRef<HTMLDivElement>('host')
const alert = useTemplateRef<InstanceType<typeof EventAlert>>('alert')
const loading = ref(true)
const deaths = ref(0)
const finishes = ref(0)
const game = new SandboxGame()

/** Official catchphrases (design system §2). */
const catchphrases: Record<SandboxEvent, string> = {
  died: 'Caiu, perdeu!',
  finished: 'É campeão!',
}

onMounted(async () => {
  if (!host.value) return
  game.on((event) => {
    alert.value?.show(catchphrases[event])
    if (event === 'died') deaths.value++
    else finishes.value++
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
  <div class="relative h-dvh w-full overflow-hidden bg-fundo">
    <div ref="host" class="absolute inset-0" />
    <p v-if="loading" class="absolute inset-0 grid place-items-center font-label text-sm tracking-[0.08em] uppercase">
      Entrando no ar…
    </p>
    <EventAlert ref="alert" />
    <header class="pointer-events-none absolute inset-x-0 top-0 flex items-start justify-between p-8">
      <span class="chip">Treino</span>
      <div class="pointer-events-auto flex gap-2">
        <span class="chip">Chegadas {{ finishes }}</span>
        <span class="chip">Quedas {{ deaths }}</span>
        <button class="chip hover:bg-linha" @click="game.toggleHitbox()">Hitbox</button>
        <RouterLink to="/" class="chip hover:bg-linha">Sair</RouterLink>
      </div>
    </header>
    <footer class="pointer-events-none absolute inset-x-0 bottom-0 p-8 text-center font-label text-sm font-extrabold tracking-[0.08em] text-texto-suave uppercase">
      [← →] / [A D] mover · [↑] / [W] / [Espaço] pular · segure para pular mais alto · pule na parede
    </footer>
  </div>
</template>
