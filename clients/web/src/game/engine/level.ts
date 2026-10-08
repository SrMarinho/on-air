import type { Rect } from './geometry'

export interface LevelLayout {
  key: string
  width: number
  height: number
  tileSize: number
  rows: readonly string[]
}

export interface ParsedLevel {
  layout: LevelLayout
  solids: Rect[]
  spikes: Rect[]
  goal: Rect
  spawns: { x: number; y: number }[]
  pixelWidth: number
  pixelHeight: number
}

const SPIKE_INSET = 6

/** Same tile semantics as backend `LevelBuilder` (runs merged per row). */
export function parseLevel(layout: LevelLayout): ParsedLevel {
  const size = layout.tileSize
  const solids = horizontalRuns(layout.rows, '#').map(([x, y, len]) => ({
    x: x * size,
    y: y * size,
    w: len * size,
    h: size,
  }))
  const spikes = horizontalRuns(layout.rows, '^').map(([x, y, len]) => ({
    x: x * size,
    y: y * size + SPIKE_INSET,
    w: len * size,
    h: size - SPIKE_INSET,
  }))
  const [goal] = positionsOf(layout.rows, 'G')
  if (!goal) throw new Error(`Level ${layout.key} has no goal`)
  return {
    layout,
    solids,
    spikes,
    goal: { x: goal[0] * size, y: goal[1] * size, w: size, h: size },
    spawns: positionsOf(layout.rows, 'S').map(([x, y]) => ({ x: x * size, y: y * size })),
    pixelWidth: layout.width * size,
    pixelHeight: layout.height * size,
  }
}

function positionsOf(rows: readonly string[], tile: string): [number, number][] {
  const out: [number, number][] = []
  rows.forEach((row, y) => [...row].forEach((ch, x) => ch === tile && out.push([x, y])))
  return out
}

function horizontalRuns(rows: readonly string[], tile: string): [number, number, number][] {
  const runs: [number, number, number][] = []
  rows.forEach((row, y) => {
    let start = -1
    ;[...row, '.'].forEach((ch, x) => {
      if (ch === tile && start < 0) start = x
      else if (ch !== tile && start >= 0) {
        runs.push([start, y, x - start])
        start = -1
      }
    })
  })
  return runs
}
