import { Container, Graphics, Sprite, type Texture } from 'pixi.js'
import { hex, sprite, world } from '@/design/tokens'
import type { Rect } from '@/game/engine/geometry'
import type { ParsedLevel } from '@/game/engine/level'
import type { FloorTile, ItemArt, StageArt } from './stageArt'

const OUTLINE = { color: hex(sprite.contorno), width: 1.5 }

/**
 * Stage art following the category code (design system §7): studio floor tiles, start plinths,
 * the Golden Microphone, and black/yellow 45° stripes on every lethal hazard.
 */
export class LevelView {
  readonly container = new Container()

  constructor(level: ParsedLevel, art: StageArt) {
    this.drawFloor(level, art)
    const hazards = new Graphics()
    level.spikes.forEach((s) => drawHazard(hazards, s))
    this.container.addChild(hazards)
    this.drawStarts(level, art.items['start-platform'])
    this.drawGoal(level.goal, art.items['golden-microphone'])
  }

  /** Placed structure: art stretched to its exact tile footprint so it reads as the collider. */
  addItem(art: ItemArt, area: Rect): void {
    const s = this.place(art.texture, area.x, area.y)
    s.width = area.w
    s.height = area.h
  }

  private drawFloor(level: ParsedLevel, art: StageArt): void {
    const { rows } = level.layout
    const size = world.tileSize
    const solid = (x: number, y: number): boolean => rows[y]?.[x] === '#'
    rows.forEach((row, y) =>
      [...row].forEach((_, x) => {
        if (!solid(x, y)) return
        const tile = this.place(art.floor[floorTileAt(solid, x, y, rows.length)], x * size, y * size)
        tile.width = tile.height = size
      }),
    )
  }

  /** 2-tile plinths set into the floor under each spawn pair, top flush with the walkable surface. */
  private drawStarts(level: ParsedLevel, art: ItemArt | undefined): void {
    if (!art) return
    const size = world.tileSize
    for (let i = 0; i < level.spawns.length; i += art.tiles.w) {
      const spawn = level.spawns[i]
      if (!spawn) continue
      this.fit(art, spawn.x, spawn.y + size, art.tiles.w * size)
    }
  }

  /** Golden Microphone art is 2×3 tiles, bottom-centered on the goal tile. */
  private drawGoal(goal: Rect, art: ItemArt | undefined): void {
    if (!art) return
    const size = world.tileSize
    const w = art.tiles.w * size
    const mic = this.fit(art, goal.x + goal.w / 2 - w / 2, goal.y + goal.h, w, art.tiles.h * size)
    mic.y -= mic.height
  }

  /** Scales art to fit `maxW × maxH` preserving aspect ratio, horizontally centered. */
  private fit(art: ItemArt, x: number, y: number, maxW: number, maxH = Number.POSITIVE_INFINITY): Sprite {
    const scale = Math.min(maxW / art.texture.width, maxH / art.texture.height)
    const s = this.place(art.texture, x, y)
    s.scale.set(scale)
    s.x += (maxW - s.width) / 2
    return s
  }

  private place(texture: Texture, x: number, y: number): Sprite {
    const s = new Sprite(texture)
    s.position.set(x, y)
    this.container.addChild(s)
    return s
  }
}

function floorTileAt(
  solid: (x: number, y: number) => boolean,
  x: number,
  y: number,
  height: number,
): FloorTile {
  if (solid(x, y - 1)) return y === height - 1 || !solid(x, y + 1) ? 'fill-base' : 'fill'
  const left = solid(x - 1, y)
  const right = solid(x + 1, y)
  if (!left && !right) return 'top-narrow'
  if (!left) return 'top-left'
  if (!right) return 'top-right'
  return 'top'
}

export function drawHazard(g: Graphics, r: Rect): void {
  const band = world.hazardStripe.band / 2
  g.rect(r.x, r.y, r.w, r.h).fill(hex(sprite.dourado))
  for (let x = r.x - r.h; x < r.x + r.w; x += band * 2) {
    const pts = [x, r.y + r.h, x + band, r.y + r.h, x + band + r.h, r.y, x + r.h, r.y].map((v, i) =>
      i % 2 === 0 ? Math.min(Math.max(v, r.x), r.x + r.w) : v,
    )
    g.poly(pts).fill(hex(sprite.contorno))
  }
  g.rect(r.x, r.y, r.w, r.h).stroke(OUTLINE)
}
