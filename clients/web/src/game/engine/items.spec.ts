import { describe, expect, it } from 'vitest'
import { canPlace, ITEM_SHAPES, placedSolids } from './items'
import { parseLevel } from './level'

const level = parseLevel({
  key: 'test',
  width: 10,
  height: 6,
  tileSize: 32,
  rows: ['..........', '..........', '..........', '.S......G.', '##########', '##########'],
})
const block = ITEM_SHAPES.praticavel!
const plank = ITEM_SHAPES['praticavel-longo']!

describe('canPlace', () => {
  it('accepts free space in the middle of the stage', () => {
    expect(canPlace({ shape: block, tileX: 4, tileY: 1 }, level, [])).toBe(true)
  })

  it('rejects overlapping the floor', () => {
    expect(canPlace({ shape: block, tileX: 4, tileY: 4 }, level, [])).toBe(false)
  })

  it('rejects the keep-out zone around start and finish', () => {
    expect(canPlace({ shape: block, tileX: 2, tileY: 3 }, level, [])).toBe(false)
    expect(canPlace({ shape: block, tileX: 7, tileY: 2 }, level, [])).toBe(false)
  })

  it('rejects leaving the stage', () => {
    expect(canPlace({ shape: plank, tileX: 8, tileY: 1 }, level, [])).toBe(false)
  })

  it('rejects overlapping a blocker such as a player', () => {
    expect(canPlace({ shape: block, tileX: 4, tileY: 1 }, level, [{ x: 140, y: 40, w: 22, h: 35 }])).toBe(false)
  })
})

describe('placedSolids', () => {
  it('converts tile shapes into world pixels', () => {
    expect(placedSolids({ shape: plank, tileX: 2, tileY: 1 })).toEqual([{ x: 64, y: 32, w: 96, h: 32 }])
  })
})
