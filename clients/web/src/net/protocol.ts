import { z } from 'zod'

/**
 * Wire protocol, mirrored from `backend/src/onair/protocol` (JSON Schema in `shared/protocol`).
 * Every inbound frame is validated here before it reaches the game.
 */

const uuid = z.string().uuid()

// --- server → client --------------------------------------------------------
export const roomMemberSchema = z.object({
  player_id: uuid,
  username: z.string(),
  ready: z.boolean(),
  is_host: z.boolean(),
})

export const levelLayoutSchema = z.object({
  key: z.string(),
  width: z.number().int(),
  height: z.number().int(),
  tile_size: z.number().int(),
  rows: z.array(z.string()),
})

export const entityStateSchema = z.object({
  id: z.number().int(),
  kind: z.string(),
  x: z.number(),
  y: z.number(),
  w: z.number(),
  h: z.number(),
  vx: z.number().default(0),
  vy: z.number().default(0),
  player_id: uuid.nullable().optional(),
  state: z.enum(['alive', 'dead', 'finished']).nullable().optional(),
})

export const itemOfferSchema = z.object({
  offer_id: z.number().int(),
  item: z.string(),
  taken_by: uuid.nullable().optional(),
})

export const scoreLineSchema = z.object({
  player_id: uuid,
  total: z.number().int(),
  gained: z.number().int(),
  reasons: z.array(z.string()),
})

export const phaseNameSchema = z.enum(['pick', 'place', 'run', 'score', 'end'])

export const serverMessageSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('auth_ok'), player_id: uuid, username: z.string() }),
  z.object({ type: z.literal('error'), code: z.string(), message: z.string() }),
  z.object({
    type: z.literal('room_state'),
    room_id: uuid,
    name: z.string(),
    status: z.enum(['lobby', 'playing', 'finished']),
    max_players: z.number().int(),
    members: z.array(roomMemberSchema),
  }),
  z.object({
    type: z.literal('match_started'),
    level: levelLayoutSchema,
    players: z.array(z.object({ player_id: uuid, username: z.string(), color: z.number().int() })),
    target_score: z.number().int(),
    simulation_hz: z.number().int(),
  }),
  z.object({
    type: z.literal('phase_changed'),
    phase: phaseNameSchema,
    round: z.number().int(),
    duration: z.number(),
    offers: z.array(itemOfferSchema).nullable().optional(),
    scores: z.array(scoreLineSchema).nullable().optional(),
  }),
  z.object({ type: z.literal('item_picked'), player_id: uuid, offer_id: z.number().int(), item: z.string() }),
  z.object({
    type: z.literal('snapshot'),
    tick: z.number().int(),
    phase_time_left: z.number(),
    acks: z.record(z.string(), z.number().int()),
    entities: z.array(entityStateSchema),
  }),
  z.object({ type: z.literal('level_items'), items: z.array(entityStateSchema) }),
  z.object({ type: z.literal('match_ended'), winner_id: uuid.nullable(), scores: z.array(scoreLineSchema) }),
  z.object({ type: z.literal('pong'), client_time: z.number(), server_time: z.number() }),
])

export type ServerMessage = z.infer<typeof serverMessageSchema>
export type ServerMessageType = ServerMessage['type']
export type ServerMessageOf<T extends ServerMessageType> = Extract<ServerMessage, { type: T }>
export type EntityState = z.infer<typeof entityStateSchema>
export type RoomMember = z.infer<typeof roomMemberSchema>
export type LevelLayoutWire = z.infer<typeof levelLayoutSchema>
export type ItemOffer = z.infer<typeof itemOfferSchema>
export type ScoreLine = z.infer<typeof scoreLineSchema>
export type PhaseName = z.infer<typeof phaseNameSchema>

// --- client → server --------------------------------------------------------
export type ClientMessage =
  | { type: 'auth'; token: string }
  | { type: 'join_room'; room_id: string }
  | { type: 'leave_room' }
  | { type: 'set_ready'; ready: boolean }
  | { type: 'start_match' }
  | { type: 'input'; seq: number; left: boolean; right: boolean; jump: boolean }
  | { type: 'pick_item'; offer_id: number }
  | { type: 'place_item'; tile_x: number; tile_y: number }
  | { type: 'ping'; client_time: number }

// --- REST -------------------------------------------------------------------
export const tokenResponseSchema = z.object({
  player_id: uuid,
  access_token: z.string(),
  refresh_token: z.string(),
})
export const profileSchema = z.object({
  id: uuid,
  username: z.string(),
  matches_played: z.number().int(),
  matches_won: z.number().int(),
})
export const roomSummarySchema = z.object({
  id: uuid,
  name: z.string(),
  players: z.number().int(),
  max_players: z.number().int(),
})
export type TokenResponse = z.infer<typeof tokenResponseSchema>
export type Profile = z.infer<typeof profileSchema>
export type RoomSummary = z.infer<typeof roomSummarySchema>
