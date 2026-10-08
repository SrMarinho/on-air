import { Container, Graphics } from 'pixi.js'
import { hex, identity, sprite, world } from '@/design/tokens'
import type { Rect } from '@/game/engine/geometry'
import type { ParsedLevel } from '@/game/engine/level'

const OUTLINE = { color: hex(sprite.contorno), width: 1.5 }

/**
 * Placeholder stage art following the category code (design system §7): stage floor planks,
 * turquoise start, golden finish and black/yellow 45° stripes on every lethal hazard.
 */
export class LevelView {
  readonly container = new Container()

  constructor(level: ParsedLevel) {
    const g = new Graphics()
    level.solids.forEach((s) => drawFloor(g, s))
    level.spikes.forEach((s) => drawHazard(g, s))
    level.spawns.forEach((s) => drawStart(g, { x: s.x, y: s.y + world.tileSize - 8, w: world.tileSize, h: 8 }))
    drawGoldenMic(g, level.goal)
    this.container.addChild(g)
  }
}

function drawFloor(g: Graphics, r: Rect): void {
  g.rect(r.x, r.y, r.w, r.h).fill(hex(sprite.pisoTabua)).stroke(OUTLINE)
  g.rect(r.x, r.y, r.w, 4).fill(hex(sprite.pisoBorda))
  for (let x = r.x + world.tileSize; x < r.x + r.w; x += world.tileSize) {
    const offset = ((x / world.tileSize) % 2) * (r.h / 2)
    g.moveTo(x, r.y + 4 + offset).lineTo(x, r.y + r.h / 2 + offset).stroke({
      color: hex(sprite.pisoJunta),
      width: 1,
    })
  }
}

function drawHazard(g: Graphics, r: Rect): void {
  const band = world.hazardStripe.band / 2
  g.rect(r.x, r.y, r.w, r.h).fill(hex(sprite.dourado))
  for (let x = r.x - r.h; x < r.x + r.w; x += band * 2) {
    const x0 = Math.max(x, r.x)
    const x1 = Math.min(x + band, r.x + r.w)
    if (x1 <= x0) continue
    g.poly([x0, r.y + r.h, x1, r.y + r.h, Math.min(x1 + r.h, r.x + r.w), r.y, Math.min(x0 + r.h, r.x + r.w), r.y])
      .fill(hex(sprite.contorno))
  }
  g.rect(r.x, r.y, r.w, r.h).stroke(OUTLINE)
}

function drawStart(g: Graphics, r: Rect): void {
  g.roundRect(r.x + 2, r.y, r.w - 4, r.h, 2).fill(hex(identity.turquesa)).stroke(OUTLINE)
}

function drawGoldenMic(g: Graphics, r: Rect): void {
  const cx = r.x + r.w / 2
  g.rect(cx - 2, r.y + 10, 4, r.h - 10).fill(hex(sprite.dourado)).stroke(OUTLINE)
  g.roundRect(cx - 7, r.y - 6, 14, 18, 7).fill(hex(sprite.dourado)).stroke(OUTLINE)
  g.circle(cx - 3, r.y - 1, 2).fill(hex(sprite.creme))
}
