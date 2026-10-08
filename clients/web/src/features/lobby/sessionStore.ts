import { defineStore } from 'pinia'
import { computed, markRaw, ref, shallowRef } from 'vue'
import { useAuthStore } from '@/features/auth/authStore'
import { useMatchStore } from '@/features/match/matchStore'
import { GameSocket, type SocketStatus } from '@/net/gameSocket'
import type { ServerMessageOf } from '@/net/protocol'

export type RoomState = Omit<ServerMessageOf<'room_state'>, 'type'>

/**
 * Online session: the single WebSocket, who I am on the server, the room I am in and the last
 * server error. Match-specific state lives in `useMatchStore`.
 */
export const useSessionStore = defineStore('session', () => {
  const socket = shallowRef(markRaw(new GameSocket()))
  const status = ref<SocketStatus>('idle')
  const playerId = ref<string | null>(null)
  const room = ref<RoomState | null>(null)
  const lastError = ref<{ code: string; message: string; at: number } | null>(null)

  const me = computed(() => room.value?.members.find((m) => m.player_id === playerId.value) ?? null)
  const isHost = computed(() => me.value?.is_host ?? false)
  const everyoneReady = computed(
    () => room.value?.members.every((m) => m.ready || m.is_host) ?? false,
  )

  socket.value.onStatus((next) => (status.value = next))
  socket.value.on('room_state', ({ type: _type, ...state }) => (room.value = state))
  socket.value.on('error', ({ code, message }) => (lastError.value = { code, message, at: Date.now() }))
  useMatchStore().bind(socket.value)

  async function connect(): Promise<void> {
    if (status.value === 'open' || status.value === 'connecting') return
    const token = await useAuthStore().accessToken()
    if (!token) throw new Error('not logged in')
    const ok = await socket.value.connect(token)
    playerId.value = ok.player_id
  }

  async function join(roomId: string): Promise<void> {
    await connect()
    socket.value.send({ type: 'join_room', room_id: roomId })
  }

  function leave(): void {
    socket.value.send({ type: 'leave_room' })
    room.value = null
    useMatchStore().clear()
  }

  function setReady(ready: boolean): void {
    socket.value.send({ type: 'set_ready', ready })
  }

  function start(): void {
    socket.value.send({ type: 'start_match' })
  }

  function disconnect(): void {
    socket.value.close()
    room.value = null
    useMatchStore().clear()
  }

  return {
    socket, status, playerId, room, lastError, me, isHost, everyoneReady,
    connect, join, leave, setReady, start, disconnect,
  }
})
