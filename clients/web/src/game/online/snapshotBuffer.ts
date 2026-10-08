import type { EntityState } from '@/net/protocol'

/** Remote entities are drawn this far in the past so there are always two snapshots to blend. */
export const INTERPOLATION_DELAY_MS = 100
const MAX_SNAPSHOTS = 32

interface TimedSnapshot {
  receivedAt: number
  entities: Map<number, EntityState>
}

/**
 * Keeps recent snapshots and samples entity positions at an arbitrary render time by linear
 * interpolation between the two snapshots around it (entity interpolation).
 */
export class SnapshotBuffer {
  private readonly snapshots: TimedSnapshot[] = []

  push(entities: EntityState[], receivedAt: number): void {
    this.snapshots.push({ receivedAt, entities: new Map(entities.map((e) => [e.id, e])) })
    if (this.snapshots.length > MAX_SNAPSHOTS) this.snapshots.shift()
  }

  clear(): void {
    this.snapshots.length = 0
  }

  latest(): EntityState[] {
    return [...(this.snapshots.at(-1)?.entities.values() ?? [])]
  }

  sample(now: number, delayMs: number = INTERPOLATION_DELAY_MS): EntityState[] {
    const renderAt = now - delayMs
    const newer = this.snapshots.findIndex((s) => s.receivedAt >= renderAt)
    if (newer <= 0) return newer === 0 ? [...this.snapshots[0]!.entities.values()] : this.latest()
    const from = this.snapshots[newer - 1]!
    const to = this.snapshots[newer]!
    const t = (renderAt - from.receivedAt) / Math.max(1, to.receivedAt - from.receivedAt)
    return [...to.entities.values()].map((target) => {
      const source = from.entities.get(target.id)
      if (!source) return target
      return { ...target, x: lerp(source.x, target.x, t), y: lerp(source.y, target.y, t) }
    })
  }
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t
}
