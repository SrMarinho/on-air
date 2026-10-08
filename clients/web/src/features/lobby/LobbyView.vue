<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import GameIcon from '@/components/GameIcon.vue'
import { useAuthStore } from '@/features/auth/authStore'
import { apiErrorMessage } from '@/net/http'
import type { RoomSummary } from '@/net/protocol'
import { roomsApi } from './roomsApi'

const auth = useAuthStore()
const router = useRouter()
const rooms = ref<RoomSummary[]>([])
const roomName = ref('')
const loading = ref(false)
const error = ref('')

async function refresh(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    rooms.value = await roomsApi.list()
  } catch (e) {
    error.value = apiErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function create(): Promise<void> {
  const name = roomName.value.trim() || `Programa do ${auth.profile?.username ?? 'calouro'}`
  try {
    const room = await roomsApi.create(name)
    await router.push(`/sala/${room.id}`)
  } catch (e) {
    error.value = apiErrorMessage(e)
  }
}

function logout(): void {
  auth.logout()
  router.push('/')
}

onMounted(refresh)
</script>

<template>
  <main class="mx-auto flex min-h-dvh w-full max-w-3xl flex-col gap-8 p-8">
    <header class="flex items-center justify-between gap-4">
      <h1 class="font-display text-4xl leading-[38px] md:text-6xl md:leading-[60px]">Salas</h1>
      <div class="flex items-center gap-2">
        <span class="chip">{{ auth.profile?.username }}</span>
        <button class="btn btn-fantasma h-10" @click="logout"><GameIcon name="exit" :size="20" />Sair</button>
      </div>
    </header>

    <section class="panel flex flex-col gap-4">
      <h2 class="font-display text-2xl">Criar sala</h2>
      <form class="flex flex-col gap-3 sm:flex-row" @submit.prevent="create">
        <label class="field flex-1">
          <span class="sr-only">Nome da sala</span>
          <input v-model="roomName" maxlength="40" placeholder="Nome do programa" />
        </label>
        <button class="btn btn-primario"><GameIcon name="play" :size="20" />Criar sala</button>
      </form>
    </section>

    <section class="panel flex flex-col gap-4">
      <div class="flex items-center justify-between">
        <h2 class="font-display text-2xl">No ar agora</h2>
        <button class="btn btn-secundario h-10" :disabled="loading" @click="refresh">
          <GameIcon name="replay" :size="20" />Atualizar
        </button>
      </div>
      <p v-if="error" class="text-sm text-no-ar-brilho" role="alert">{{ error }}</p>
      <p v-else-if="!rooms.length && !loading" class="text-texto-suave">
        Nenhum programa no ar. Crie uma sala e chame o elenco!
      </p>
      <ul class="flex flex-col gap-3">
        <li
          v-for="room in rooms"
          :key="room.id"
          class="flex items-center justify-between gap-4 rounded-md border-3 border-tinta bg-fundo-poco p-3"
        >
          <span class="font-label text-lg font-extrabold tracking-[0.04em] uppercase">{{ room.name }}</span>
          <span class="flex items-center gap-3">
            <span class="flex items-center gap-1 font-display tabular-nums">
              <GameIcon name="players" :size="24" />{{ room.players }}/{{ room.max_players }}
            </span>
            <RouterLink
              :to="`/sala/${room.id}`"
              class="btn btn-secundario h-10"
              :class="{ 'pointer-events-none opacity-40': room.players >= room.max_players }"
            >
              Entrar
            </RouterLink>
          </span>
        </li>
      </ul>
    </section>
  </main>
</template>
