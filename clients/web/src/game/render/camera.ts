import type { Container } from 'pixi.js'
import { world } from '@/design/tokens'
import type { Rect } from '@/game/engine/geometry'

const MARGIN = 3 * world.tileSize
const MIN_VISIBLE_HEIGHT = 12 * world.tileSize
const SMOOTHING = 6

/**
 * Frames every live player with a 3-tile margin and zooms smoothly (design system §15.8),
 * never showing outside the stage.
 */
export class Camera {
  private x = 0
  private y = 0
  private zoom = 1
  private initialized = false
  private readonly stage: { w: number; h: number }

  constructor(stageWidth: number, stageHeight: number) {
    this.stage = { w: stageWidth, h: stageHeight }
  }

  update(target: Container, screen: { width: number; height: number }, focus: Rect[], dt: number): void {
    const fit = Math.min(screen.width / this.stage.w, screen.height / this.stage.h)
    const box = this.focusBox(focus)
    const wanted = Math.max(
      fit,
      Math.min(
        screen.width / Math.max(box.w, (MIN_VISIBLE_HEIGHT * screen.width) / screen.height),
        screen.height / Math.max(box.h, MIN_VISIBLE_HEIGHT),
      ),
    )
    const cx = box.x + box.w / 2
    const cy = box.y + box.h / 2
    const t = this.initialized ? 1 - Math.exp(-SMOOTHING * dt) : 1
    this.initialized = true
    this.zoom += (wanted - this.zoom) * t
    this.x += (cx - this.x) * t
    this.y += (cy - this.y) * t

    const viewW = screen.width / this.zoom
    const viewH = screen.height / this.zoom
    const left = clamp(this.x - viewW / 2, Math.min(0, this.stage.w - viewW), Math.max(0, this.stage.w - viewW))
    const top = clamp(this.y - viewH / 2, Math.min(0, this.stage.h - viewH), Math.max(0, this.stage.h - viewH))
    const offsetX = viewW > this.stage.w ? (viewW - this.stage.w) / 2 : -left
    const offsetY = viewH > this.stage.h ? (viewH - this.stage.h) / 2 : -top
    target.scale.set(this.zoom)
    target.position.set(offsetX * this.zoom, offsetY * this.zoom)
  }

  private focusBox(focus: Rect[]): Rect {
    if (focus.length === 0) return { x: 0, y: 0, w: this.stage.w, h: this.stage.h }
    const x0 = Math.min(...focus.map((r) => r.x)) - MARGIN
    const y0 = Math.min(...focus.map((r) => r.y)) - MARGIN
    const x1 = Math.max(...focus.map((r) => r.x + r.w)) + MARGIN
    const y1 = Math.max(...focus.map((r) => r.y + r.h)) + MARGIN
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 }
  }
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max)
}
