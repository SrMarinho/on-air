import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { tokens } from '@/design/tokens'
import type { GameSocket } from '@/net/gameSocket'
import type { ItemOffer, LevelLayoutWire, PhaseName, ScoreLine } from '@/net/protocol'

export interface MatchPlayer {
  playerId: string
  username: string
  /** 1-based slot → color + shape from the design tokens (§3.4). */
  slot: number
  score: number
}

/**
 * Match state that Vue renders (phases, offers, scores). High-frequency data (snapshots) goes
 * straight from the socket to the game engine and never through this store.
 */
export const useMatchStore = defineStore('match', () => {
  const active = ref(false)
  const level = ref<LevelLayoutWire | null>(null)
  const players = ref<MatchPlayer[]>([])
  const targetScore = ref(0)
  const phase = ref<PhaseName | null>(null)
  const round = ref(0)
  const phaseDuration = ref(0)
  const phaseEndsAt = ref(0)
  const offers = ref<ItemOffer[]>([])
  const heldItems = ref<Record<string, string>>({})
  const roundScores = ref<ScoreLine[]>([])
  const winnerId = ref<string | null>(null)
  const ended = ref(false)

  const leader = computed(() => [...players.value].sort((a, b) => b.score - a.score)[0] ?? null)

  function slotColor(playerId: string): string {
    const slot = players.value.find((p) => p.playerId === playerId)?.slot ?? 1
    return tokens.players.find((p) => p.slot === slot)?.color ?? tokens.players[0]!.color
  }

  function applyScores(lines: ScoreLine[]): void {
    for (const line of lines) {
      const player = players.value.find((p) => p.playerId === line.player_id)
      if (player) player.score = line.total
    }
  }

  function bind(socket: GameSocket): void {
    socket.on('match_started', (m) => {
      active.value = true
      ended.value = false
      winnerId.value = null
      level.value = m.level
      targetScore.value = m.target_score
      players.value = m.players.map((p, i) => ({ playerId: p.player_id, username: p.username, slot: i + 1, score: 0 }))
    })
    socket.on('phase_changed', (m) => {
      phase.value = m.phase
      round.value = m.round
      phaseDuration.value = m.duration
      phaseEndsAt.value = performance.now() + m.duration * 1000
      if (m.phase === 'pick') {
        offers.value = m.offers ?? []
        heldItems.value = {}
        roundScores.value = []
      }
      if (m.scores) {
        roundScores.value = m.scores
        applyScores(m.scores)
      }
    })
    socket.on('item_picked', (m) => {
      heldItems.value = { ...heldItems.value, [m.player_id]: m.item }
      offers.value = offers.value.map((o) => (o.offer_id === m.offer_id ? { ...o, taken_by: m.player_id } : o))
    })
    socket.on('snapshot', (m) => {
      phaseEndsAt.value = performance.now() + m.phase_time_left * 1000
    })
    socket.on('match_ended', (m) => {
      ended.value = true
      winnerId.value = m.winner_id
      applyScores(m.scores)
    })
  }

  function clear(): void {
    active.value = false
    level.value = null
    players.value = []
    phase.value = null
    offers.value = []
    heldItems.value = {}
    roundScores.value = []
    winnerId.value = null
    ended.value = false
  }

  return {
    active, level, players, targetScore, phase, round, phaseDuration, phaseEndsAt, offers,
    heldItems, roundScores, winnerId, ended, leader, slotColor, bind, clear,
  }
})
