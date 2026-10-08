import { describe, expect, it } from 'vitest'
import { SnapshotBuffer } from './snapshotBuffer'

const entity = (x: number) => ({ id: 1, kind: 'player', x, y: 0, w: 22, h: 35, vx: 0, vy: 0 })

describe('SnapshotBuffer', () => {
  it('interpolates between the two snapshots around the render time', () => {
    const buffer = new SnapshotBuffer()
    buffer.push([entity(0)], 1000)
    buffer.push([entity(100)], 1100)

    const [sampled] = buffer.sample(1150, 100)

    expect(sampled?.x).toBeCloseTo(50)
  })

  it('holds the latest snapshot when render time is ahead of everything', () => {
    const buffer = new SnapshotBuffer()
    buffer.push([entity(10)], 1000)

    expect(buffer.sample(5000, 100)[0]?.x).toBe(10)
  })
})
