import { Application, Container, Graphics, type FederatedPointerEvent } from 'pixi.js'
import { hex, tokens, world as worldTokens } from '@/design/tokens'
import { overlaps, type Rect } from '@/game/engine/geometry'
import { canPlace, footprint, ITEM_SHAPES, placedSolids, type Placement } from '@/game/engine/items'
import { parseLevel, type LevelLayout, type ParsedLevel } from '@/game/engine/level'
import { createBody, PHYSICS, SIMULATION_DT, stepPlayer, type PlayerBody } from '@/game/engine/physics'
import { KeyboardInput } from '@/game/input/keyboard'
import { loadAnimationSet } from '@/game/render/animationSet'
import { Camera } from '@/game/render/camera'
import { CharacterView } from '@/game/render/characterView'
import { LevelView } from '@/game/render/levelView'
import { PlacementView } from '@/game/render/placementView'
import { loadStageArt, type StageArt } from '@/game/render/stageArt'
import { loadUiTextures } from '@/game/render/uiArt'

const RESPAWN_DELAY = 1.2
const MAX_STEPS_PER_FRAME = 5

export type SandboxEvent = 'died' | 'finished' | 'placed' | 'blocked'
export type SandboxMode = 'run' | 'build' | 'paused'

export interface SandboxItem {
  key: string
  image: string
  tiles: { w: number; h: number }
}

export interface SandboxState {
  mode: SandboxMode
  selectedItem: string
  items: SandboxItem[]
}

export interface SandboxListener {
  event(event: SandboxEvent): void
  state(state: SandboxState): void
  clock(elapsedSeconds: number): void
}

const SILENT: SandboxListener = { event: () => {}, state: () => {}, clock: () => {} }

/**
 * Offline playground: local simulation with the same physics as the server, plus a build mode
 * to try the placement flow (design system §15.7). The online client reuses engine/render pieces.
 */
export class SandboxGame {
  private readonly app = new Application()
  private readonly input = new KeyboardInput()
  private readonly world = new Container()
  private readonly hitbox = new Graphics()
  private level!: ParsedLevel
  private stageArt!: StageArt
  private levelView!: LevelView
  private placement!: PlacementView
  private character!: CharacterView
  private camera!: Camera
  private body!: PlayerBody
  private alive = true
  private respawnIn = 0
  private accumulator = 0
  private elapsed = 0
  private lastClock = -1
  private mode: SandboxMode = 'run'
  private modeBeforePause: SandboxMode = 'run'
  private selectedItem = Object.keys(ITEM_SHAPES)[0] ?? ''
  private cursor: Placement | null = null
  private listener: SandboxListener = SILENT
  private readonly onKey = (event: KeyboardEvent): void => this.handleKey(event)

  async mount(host: HTMLElement, layout: LevelLayout, character = 'calouro'): Promise<void> {
    await this.app.init({ resizeTo: host, background: hex(tokens.color.theme.estudio.fundo), antialias: true })
    host.appendChild(this.app.canvas)
    this.level = parseLevel(layout)
    this.camera = new Camera(this.level.pixelWidth, this.level.pixelHeight)
    const [animations, stageArt, cursors] = await Promise.all([
      loadAnimationSet(character),
      loadStageArt(),
      loadUiTextures(['placement-valid', 'placement-invalid'] as const),
    ])
    this.stageArt = stageArt
    this.levelView = new LevelView(this.level, stageArt)
    this.placement = new PlacementView(this.level.pixelWidth, this.level.pixelHeight, cursors)
    this.character = new CharacterView(animations)
    this.world.addChild(this.levelView.container, this.character.container, this.hitbox, this.placement.container)
    this.app.stage.addChild(this.world)
    this.hitbox.visible = false
    this.bindPointer()
    this.input.attach()
    window.addEventListener('keydown', this.onKey)
    this.respawn()
    this.emitState()
    this.app.ticker.add((ticker) => this.frame(ticker.deltaMS / 1000))
  }

  listen(listener: Partial<SandboxListener>): void {
    this.listener = { ...SILENT, ...listener }
  }

  toggleHitbox(): void {
    this.hitbox.visible = !this.hitbox.visible
  }

  setMode(mode: SandboxMode): void {
    if (mode === this.mode) return
    if (mode === 'paused') this.modeBeforePause = this.mode
    this.mode = mode
    this.placement.show(mode === 'build')
    this.cursor = null
    this.emitState()
  }

  togglePause(): void {
    this.setMode(this.mode === 'paused' ? this.modeBeforePause : 'paused')
  }

  toggleBuild(): void {
    this.setMode(this.mode === 'build' ? 'run' : 'build')
  }

  selectItem(key: string): void {
    if (!ITEM_SHAPES[key]) return
    this.selectedItem = key
    this.emitState()
  }

  destroy(): void {
    window.removeEventListener('keydown', this.onKey)
    this.input.detach()
    this.app.destroy(true, { children: true })
  }

  // --- loop -------------------------------------------------------------
  private frame(seconds: number): void {
    if (this.mode === 'run') {
      this.accumulator += Math.min(seconds, SIMULATION_DT * MAX_STEPS_PER_FRAME)
      while (this.accumulator >= SIMULATION_DT) {
        this.step(SIMULATION_DT)
        this.accumulator -= SIMULATION_DT
      }
      this.tickClock(seconds)
    }
    this.render(seconds)
  }

  private tickClock(seconds: number): void {
    this.elapsed += seconds
    const whole = Math.floor(this.elapsed)
    if (whole !== this.lastClock) {
      this.lastClock = whole
      this.listener.clock(whole)
    }
  }

  private step(dt: number): void {
    if (!this.alive) {
      this.respawnIn -= dt
      if (this.respawnIn <= 0) this.respawn()
      return
    }
    stepPlayer(this.body, this.input.snapshot(), this.level.solids, dt)
    const box = this.playerRect()
    if (this.level.spikes.some((s) => overlaps(box, s)) || box.y > this.level.pixelHeight + 64) {
      this.end('died')
    } else if (overlaps(box, this.level.goal)) {
      this.end('finished')
    }
  }

  private end(event: 'died' | 'finished'): void {
    this.alive = event !== 'died'
    this.respawnIn = RESPAWN_DELAY
    this.listener.event(event)
    if (event === 'finished') this.respawn()
  }

  private respawn(): void {
    const spawn = this.level.spawns[0] ?? { x: 0, y: 0 }
    const size = this.level.layout.tileSize
    this.body = createBody(spawn.x + (size - PHYSICS.playerWidth) / 2, spawn.y + size - PHYSICS.playerHeight)
    this.alive = true
  }

  private render(dt: number): void {
    const { body } = this
    this.character.update(body.x, body.y, {
      vx: this.mode === 'run' ? body.vx : 0,
      vy: this.mode === 'run' ? body.vy : 0,
      onGround: body.onGround || this.mode !== 'run',
      alive: this.alive,
    })
    this.hitbox.clear().rect(body.x, body.y, PHYSICS.playerWidth, PHYSICS.playerHeight).stroke({
      color: hex(tokens.color.state.valido),
      width: 1,
    })
    const focus = this.mode === 'build' ? [] : [this.playerRect()]
    this.camera.update(this.world, this.app.screen, focus, dt)
    const art = this.cursor ? this.stageArt.items[this.cursor.shape.key] : undefined
    this.placement.update(this.cursor && footprint(this.cursor), art, this.cursorValid(), dt)
  }

  // --- build mode -------------------------------------------------------
  private bindPointer(): void {
    this.app.stage.eventMode = 'static'
    this.app.stage.hitArea = this.app.screen
    this.app.stage.on('pointermove', (e: FederatedPointerEvent) => this.moveCursor(e))
    this.app.stage.on('pointerdown', (e: FederatedPointerEvent) => {
      this.moveCursor(e)
      this.placeAtCursor()
    })
  }

  private moveCursor(event: FederatedPointerEvent): void {
    const shape = ITEM_SHAPES[this.selectedItem]
    if (this.mode !== 'build' || !shape) return
    const local = this.world.toLocal(event.global)
    const size = worldTokens.tileSize
    this.cursor = {
      shape,
      tileX: Math.floor(local.x / size - (shape.tiles.w - 1) / 2),
      tileY: Math.floor(local.y / size - (shape.tiles.h - 1) / 2),
    }
  }

  private cursorValid(): boolean {
    return !!this.cursor && canPlace(this.cursor, this.level, [this.playerRect()])
  }

  private placeAtCursor(): void {
    if (this.mode !== 'build' || !this.cursor) return
    if (!this.cursorValid()) {
      this.listener.event('blocked')
      return
    }
    this.level.solids.push(...placedSolids(this.cursor))
    const art = this.stageArt.items[this.cursor.shape.key]
    if (art) this.levelView.addItem(art, footprint(this.cursor))
    this.listener.event('placed')
  }

  private handleKey(event: KeyboardEvent): void {
    if (event.repeat) return
    if (event.code === 'Escape') this.togglePause()
    else if (event.code === 'KeyB' && this.mode !== 'paused') this.toggleBuild()
    else if (this.mode === 'build' && /^Digit[1-9]$/.test(event.code)) {
      const key = Object.keys(ITEM_SHAPES)[Number(event.code.slice(5)) - 1]
      if (key) this.selectItem(key)
    }
  }

  private emitState(): void {
    this.listener.state({
      mode: this.mode,
      selectedItem: this.selectedItem,
      items: Object.values(ITEM_SHAPES)
        .filter((shape) => this.stageArt?.items[shape.key])
        .map((shape) => ({
          key: shape.key,
          image: this.stageArt.items[shape.key]?.url ?? '',
          tiles: shape.tiles,
        })),
    })
  }

  private playerRect(): Rect {
    return { x: this.body.x, y: this.body.y, w: PHYSICS.playerWidth, h: PHYSICS.playerHeight }
  }
}
