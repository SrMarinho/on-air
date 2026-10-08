import type { Solid } from '@/game/engine/physics'
import { createBody, stepPlayer, type PlayerBody, type PlayerInputState } from '@/game/engine/physics'

interface PendingInput {
  seq: number
  input: PlayerInputState
}

/** Larger corrections than this snap instead of being smoothed (teleports, respawns). */
const SNAP_DISTANCE = 64
const SMOOTHING_PER_SECOND = 12

/**
 * Client-side prediction for the local player: applies inputs immediately with the shared
 * physics, then on every snapshot rewinds to the server state and replays unacknowledged inputs.
 * Corrections are hidden by a decaying visual offset.
 */
export class LocalPredictor {
  body: PlayerBody | null = null
  entityId: number | null = null
  private pending: PendingInput[] = []
  private seq = 0
  private offsetX = 0
  private offsetY = 0

  get active(): boolean {
    return this.body !== null
  }

  start(entityId: number, x: number, y: number): void {
    this.entityId = entityId
    this.body = createBody(x, y)
    this.pending = []
    this.offsetX = this.offsetY = 0
  }

  stop(): void {
    this.body = null
    this.entityId = null
    this.pending = []
  }

  /** Steps the local simulation and returns the sequence number to send with this input. */
  step(input: PlayerInputState, solids: readonly Solid[], dt: number): number {
    this.seq += 1
    if (this.body) {
      stepPlayer(this.body, input, solids, dt)
      this.pending.push({ seq: this.seq, input })
    }
    return this.seq
  }

  reconcile(
    server: { x: number; y: number; vx: number; vy: number },
    ackSeq: number,
    solids: readonly Solid[],
    dt: number,
  ): void {
    const body = this.body
    if (!body) return
    const beforeX = body.x
    const beforeY = body.y
    this.pending = this.pending.filter((p) => p.seq > ackSeq)
    body.x = server.x
    body.y = server.y
    body.vx = server.vx
    body.vy = server.vy
    for (const { input } of this.pending) stepPlayer(body, input, solids, dt)

    const errorX = beforeX - body.x + this.offsetX
    const errorY = beforeY - body.y + this.offsetY
    const far = Math.hypot(errorX, errorY) > SNAP_DISTANCE
    this.offsetX = far ? 0 : errorX
    this.offsetY = far ? 0 : errorY
  }

  /** Render position: predicted body plus the decaying correction offset. */
  renderPosition(dt: number): { x: number; y: number } | null {
    if (!this.body) return null
    const decay = Math.exp(-SMOOTHING_PER_SECOND * dt)
    this.offsetX *= decay
    this.offsetY *= decay
    return { x: this.body.x + this.offsetX, y: this.body.y + this.offsetY }
  }
}
