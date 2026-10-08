<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import GameIcon from '@/components/GameIcon.vue'
import ToastBar from '@/components/ToastBar.vue'
import { tokens } from '@/design/tokens'
import MatchScreen from '@/features/match/MatchScreen.vue'
import { useMatchStore } from '@/features/match/matchStore'
import { useSessionStore } from './sessionStore'

const props = defineProps<{ id: string }>()
const session = useSessionStore()
const match = useMatchStore()
const router = useRouter()
const connectionError = ref('')
const toast = ref<InstanceType<typeof ToastBar>>()

const seats = computed(() => {
  const members = session.room?.members ?? []
  const max = session.room?.max_players ?? 4
  return Array.from({ length: max }, (_, i) => ({ slot: i + 1, member: members[i] ?? null }))
})
const playerColor = (slot: number) => tokens.players.find((p) => p.slot === slot)?.color

onMounted(async () => {
  try {
    await session.join(props.id)
  } catch {
    connectionError.value = 'Saímos do ar! Não deu para conectar ao servidor.'
  }
})

watch(
  () => session.lastError,
  (error) => error && toast.value?.show(error.message, 'close'),
)
watch(
  () => session.status,
  (status) => {
    if (status === 'closed' && !connectionError.value) connectionError.value = 'Saímos do ar! A conexão caiu.'
  },
)

function leave(): void {
  session.leave()
  router.push('/salas')
}

async function copyLink(): Promise<void> {
  try {
    await navigator.clipboard.writeText(window.location.href)
    toast.value?.show('Link da sala copiado', 'check')
  } catch {
    toast.value?.show('Não deu para copiar o link', 'close')
  }
}

onBeforeUnmount(() => session.disconnect())
</script>

<template>
  <div class="relative min-h-dvh">
    <ToastBar ref="toast" />

    <MatchScreen v-if="match.active" @leave="leave" />

    <main v-else class="mx-auto flex min-h-dvh w-full max-w-4xl flex-col gap-8 p-8">
      <header class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p class="font-label text-sm font-extrabold tracking-[0.08em] text-texto-suave uppercase">Sala</p>
          <h1 class="font-display text-4xl leading-[38px]">{{ session.room?.name ?? 'Entrando no ar…' }}</h1>
        </div>
        <div class="flex gap-2">
          <button class="btn btn-secundario h-10" @click="copyLink"><GameIcon name="copy" :size="20" />Copiar link</button>
          <button class="btn btn-fantasma h-10" @click="leave"><GameIcon name="exit" :size="20" />Sair</button>
        </div>
      </header>

      <div v-if="connectionError" class="panel flex flex-col items-center gap-4 text-center">
        <GameIcon name="offline" :size="48" />
        <p>{{ connectionError }}</p>
        <RouterLink to="/salas" class="btn btn-secundario"><GameIcon name="back" :size="20" />Voltar às salas</RouterLink>
      </div>

      <template v-else-if="session.room">
        <!-- Dressing-room chairs (§15.4) -->
        <ul class="grid grid-cols-2 gap-4 md:grid-cols-4">
          <li
            v-for="seat in seats"
            :key="seat.slot"
            class="flex flex-col items-center gap-3 rounded-lg border-3 border-tinta bg-fundo-elevado p-4 shadow-[0_4px_0_var(--color-sombra-pop)]"
          >
            <div class="relative grid size-24 place-items-center rounded-full bg-fundo-poco">
              <!-- First idle frame of the 8×2 atlas -->
              <span
                v-if="seat.member"
                class="h-20 w-[52px] bg-[url(/atlases/characters/calouro/calouro-idle.png)] bg-[length:800%_200%] bg-no-repeat"
                aria-hidden="true"
              />
              <span v-else class="font-display text-4xl text-texto-suave">?</span>
              <GameIcon v-if="seat.member?.is_host" name="crown" :size="32" class="absolute -top-3 -right-2" />
            </div>
            <span
              class="max-w-full truncate rounded-sm px-2 font-label text-base font-extrabold tracking-[0.06em] text-tinta uppercase"
              :style="{ background: seat.member ? playerColor(seat.slot) : 'var(--color-linha)' }"
            >
              {{ seat.member?.username ?? 'Cadeira vazia' }}
            </span>
            <span
              v-if="seat.member"
              class="chip"
              :class="seat.member.ready || seat.member.is_host ? 'bg-turquesa text-tinta' : 'text-texto-suave'"
            >
              {{ seat.member.is_host ? 'Dono da sala' : seat.member.ready ? 'Pronto' : 'Aguardando…' }}
            </span>
          </li>
        </ul>

        <footer class="flex flex-wrap justify-end gap-3">
          <button v-if="!session.isHost" class="btn btn-secundario" @click="session.setReady(!session.me?.ready)">
            <GameIcon :name="session.me?.ready ? 'close' : 'check'" :size="20" />
            {{ session.me?.ready ? 'Cancelar' : 'Pronto' }}
          </button>
          <button
            v-else
            class="btn btn-primario"
            :disabled="!session.everyoneReady"
            :title="session.everyoneReady ? '' : 'Esperando o resto do elenco…'"
            @click="session.start()"
          >
            <GameIcon name="play" :size="20" />Começar o programa
          </button>
        </footer>
      </template>
    </main>
  </div>
</template>
