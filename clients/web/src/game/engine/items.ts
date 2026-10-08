import { world } from '@/design/tokens'
import { overlaps, type Rect } from './geometry'
import type { ParsedLevel } from './level'

/** Collision layout of a placeable item, in tile units relative to its top-left tile. */
export interface ItemShape {
  key: string
  tiles: { w: number; h: number }
  solids: Rect[]
}

/** Mirrors the structure items of backend `match/domain/items.py` (block, plank). */
export const ITEM_SHAPES: Record<string, ItemShape> = {
  praticavel: { key: 'praticavel', tiles: { w: 1, h: 1 }, solids: [{ x: 0, y: 0, w: 1, h: 1 }] },
  'praticavel-longo': {
    key: 'praticavel-longo',
    tiles: { w: 3, h: 1 },
    solids: [{ x: 0, y: 0, w: 3, h: 1 }],
  },
}

export interface Placement {
  shape: ItemShape
  tileX: number
  tileY: number
}

const KEEP_OUT_TILES = 1

export function footprint({ shape, tileX, tileY }: Placement): Rect {
  const size = world.tileSize
  return { x: tileX * size, y: tileY * size, w: shape.tiles.w * size, h: shape.tiles.h * size }
}

export function placedSolids({ shape, tileX, tileY }: Placement): Rect[] {
  const size = world.tileSize
  return shape.solids.map((s) => ({
    x: (tileX + s.x) * size,
    y: (tileY + s.y) * size,
    w: s.w * size,
    h: s.h * size,
  }))
}

/**
 * Same rules as backend `PlacePhase.place`: inside the stage, off the start/finish keep-out
 * zones and not overlapping solids, hazards or a player.
 */
export function canPlace(placement: Placement, level: ParsedLevel, blockers: readonly Rect[]): boolean {
  const area = footprint(placement)
  const inside =
    area.x >= 0 && area.y >= 0 && area.x + area.w <= level.pixelWidth && area.y + area.h <= level.pixelHeight
  if (!inside) return false
  const margin = KEEP_OUT_TILES * world.tileSize
  const size = world.tileSize
  const keepOut = [...level.spawns, { x: level.goal.x, y: level.goal.y }].map((p) => ({
    x: p.x - margin,
    y: p.y - margin,
    w: size + margin * 2,
    h: size + margin * 2,
  }))
  return ![...keepOut, ...level.solids, ...level.spikes, level.goal, ...blockers].some((r) =>
    overlaps(area, r),
  )
}
