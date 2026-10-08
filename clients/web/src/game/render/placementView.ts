import { Container, Graphics, Sprite, type Texture } from 'pixi.js'
import { hex, sprite, world } from '@/design/tokens'
import type { Rect } from '@/game/engine/geometry'
import type { ItemArt } from './stageArt'

export type PlacementCursorTextures = Record<'placement-valid' | 'placement-invalid', Texture>

const GHOST_ALPHA = 0.7
const GRID_ALPHA = 0.15
const FRAME_MARGIN = 6
const SHAKE_PX = 4

/**
 * Build-phase overlay (design system §15.7): dotted grid, ghost item at 70% snapped to the grid
 * and a valid (sky ✓) / invalid (red ✕, shaking) frame around it.
 */
export class PlacementView {
  readonly container = new Container()
  private readonly grid = new Graphics()
  private readonly ghost = new Sprite()
  private readonly frame = new Sprite()
  private readonly cursors: PlacementCursorTextures
  private shakeTime = 0

  constructor(stageWidth: number, stageHeight: number, cursors: PlacementCursorTextures) {
    this.cursors = cursors
    this.drawGrid(stageWidth, stageHeight)
    this.ghost.alpha = GHOST_ALPHA
    this.container.addChild(this.grid, this.ghost, this.frame)
    this.container.visible = false
  }

  show(visible: boolean): void {
    this.container.visible = visible
  }

  update(area: Rect | null, art: ItemArt | undefined, valid: boolean, dt: number): void {
    this.ghost.visible = this.frame.visible = area !== null
    if (!area) return
    if (art) {
      this.ghost.texture = art.texture
      this.ghost.position.set(area.x, area.y)
      this.ghost.width = area.w
      this.ghost.height = area.h
    }
    this.shakeTime = valid ? 0 : this.shakeTime + dt
    const shake = valid ? 0 : Math.sin(this.shakeTime * 60) * (SHAKE_PX / 2)
    this.frame.texture = valid ? this.cursors['placement-valid'] : this.cursors['placement-invalid']
    this.frame.position.set(area.x - FRAME_MARGIN + shake, area.y - FRAME_MARGIN * 2)
    this.frame.width = area.w + FRAME_MARGIN * 3
    this.frame.height = area.h + FRAME_MARGIN * 3
  }

  private drawGrid(width: number, height: number): void {
    const size = world.tileSize
    const color = hex(sprite.creme)
    for (let x = 0; x <= width; x += size) {
      for (let y = 0; y < height; y += 8) this.grid.rect(x, y, 1, 4)
    }
    for (let y = 0; y <= height; y += size) {
      for (let x = 0; x < width; x += 8) this.grid.rect(x, y, 4, 1)
    }
    this.grid.fill({ color, alpha: GRID_ALPHA })
  }
}
