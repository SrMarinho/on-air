import { Application, Container, Graphics, Sprite, type FederatedPointerEvent, type Texture } from 'pixi.js'
import { hex, tokens, world as worldTokens } from '@/design/tokens'
import type { Rect } from '@/game/engine/geometry'
import { canPlace, footprint, type Placement } from '@/game/engine/items'
import { parseLevel, type ParsedLevel } from '@/game/engine/level'
import { PHYSICS, SIMULATION_DT, type Solid } from '@/game/engine/physics'
import { serverItem } from '@/game/engine/serverItems'
import { KeyboardInput } from '@/game/input/keyboard'
import { loadAnimationSet, type AnimationSet } from '@/game/render/animationSet'
import { Camera } from '@/game/render/camera'
import { CharacterView } from '@/game/render/characterView'
import { drawHazard, LevelView } from '@/game/render/levelView'
import { Nameplate } from '@/game/render/nameplate'
import { PlacementView } from '@/game/render/placementView'
import { loadStageArt, type ItemArt, type StageArt } from '@/game/render/stageArt'
import { loadUiTextures } from '@/game/render/uiArt'
import type { GameSocket } from '@/net/gameSocket'
import type { EntityState, LevelLayoutWire, PhaseName } from '@/net/protocol'
import { LocalPredictor } from './localPredictor'
import { SnapshotBuffer } from './snapshotBuffer'

const MAX_STEPS_PER_FRAME = 5
const CHARACTER_TOP = worldTokens.character.displayH + 2

export interface OnlinePlayer {
  playerId: string
  username: string
  slot: number
}

export type LocalEvent = 'died' | 'finished' | 'placed'

interface PlayerView {
  character: CharacterView
  nameplate: Nameplate
  lastState: EntityState['state']
}

/**
 * Online match renderer + input. The server is authoritative: this class predicts only the
 * local player's movement, interpolates everyone else and sends intent (inputs, placements).
 */
export class OnlineGame {
  private readonly app = new Application()
  private readonly input = new KeyboardInput()
  private readonly world = new Container()
  private readonly staticsLayer = new Container()
  private readonly platformsLayer = new Container()
  private readonly playersLayer = new Container()
  private readonly buffer = new SnapshotBuffer()
  private readonly predictor = new LocalPredictor()
  private readonly views = new Map<string, PlayerView>()
  private readonly platforms = new Map<number, Container>()
  private readonly unsubscribe: (() => void)[] = []
  private readonly socket: GameSocket
  private readonly myId: string
  private readonly players: OnlinePlayer[]
  private readonly level: ParsedLevel
  private animations!: AnimationSet
  private stageArt!: StageArt
  private placement: PlacementView | null = null
  private camera!: Camera
  private bombArt!: ItemArt
  private pathArrows!: Texture
  private staticSolids: Solid[] = []
  private staticBlockers: Rect[] = []
  private phase: PhaseName | null = null
  private heldItem: string | null = null
  private cursor: Placement | null = null
  private accumulator = 0
  private lastAck = 0
  private onLocalEvent: (event: LocalEvent) => void = () => {}

  constructor(socket: GameSocket, myId: string, layout: LevelLayoutWire, players: OnlinePlayer[]) {
    this.socket = socket
    this.myId = myId
    this.players = players
    this.level = parseLevel({
      key: layout.key,
      width: layout.width,
      height: layout.height,
      tileSize: layout.tile_size,
      rows: layout.rows,
    })
  }

  async mount(host: HTMLElement, character = 'calouro'): Promise<void> {
    await this.app.init({ resizeTo: host, background: hex(tokens.color.theme.estudio.fundo), antialias: true })
    host.appendChild(this.app.canvas)
    const [animations, stageArt, ui] = await Promise.all([
      loadAnimationSet(character),
      loadStageArt(),
      loadUiTextures(['placement-valid', 'placement-invalid', 'blast-cross', 'path-horizontal'] as const),
    ])
    this.animations = animations
    this.stageArt = stageArt
    this.pathArrows = ui['path-horizontal']
    this.bombArt = { texture: ui['blast-cross'], url: '', tiles: { w: 3, h: 3 }, category: 'structure' }
    this.camera = new Camera(this.level.pixelWidth, this.level.pixelHeight)
    this.placement = new PlacementView(this.level.pixelWidth, this.level.pixelHeight, ui)
    this.world.addChild(
      new LevelView(this.level, stageArt).container,
      this.staticsLayer,
      this.platformsLayer,
      this.playersLayer,
      this.placement.container,
    )
    this.app.stage.addChild(this.world)
    this.bindPointer()
    this.input.attach()
    this.unsubscribe.push(
      this.socket.on('snapshot', (m) => this.onSnapshot(m.entities, m.acks)),
      this.socket.on('level_items', (m) => this.rebuildStatics(m.items)),
    )
    this.app.ticker.add((ticker) => this.frame(ticker.deltaMS / 1000))
    this.setPhase(this.phase, this.heldItem)
  }

  onEvent(handler: (event: LocalEvent) => void): void {
    this.onLocalEvent = handler
  }

  /** Safe to call before `mount` finishes: the state is applied once the scene exists. */
  setPhase(phase: PhaseName | null, heldItem: string | null): void {
    this.phase = phase
    this.heldItem = phase === 'place' ? heldItem : null
    this.placement?.show(this.heldItem !== null)
    if (!this.heldItem) this.cursor = null
    if (phase !== 'run') this.predictor.stop()
  }

  destroy(): void {
    this.unsubscribe.forEach((off) => off())
    this.input.detach()
    this.app.destroy(true, { children: true })
  }

  // --- network ----------------------------------------------------------
  private onSnapshot(entities: EntityState[], acks: Record<string, number>): void {
    this.buffer.push(entities, performance.now())
    this.lastAck = acks[this.myId] ?? this.lastAck
    const mine = entities.find((e) => e.kind === 'player' && e.player_id === this.myId)
    if (!mine || mine.state !== 'alive' || this.phase !== 'run') {
      this.predictor.stop()
      return
    }
    if (this.predictor.entityId !== mine.id) this.predictor.start(mine.id, mine.x, mine.y)
    else this.predictor.reconcile(mine, this.lastAck, this.solids(), SIMULATION_DT)
  }

  private rebuildStatics(items: EntityState[]): void {
    this.staticsLayer.removeChildren().forEach((child) => child.destroy())
    this.staticSolids = []
    this.staticBlockers = []
    const hazards = new Graphics()
    for (const item of items) {
      const rect = { x: item.x, y: item.y, w: item.w, h: item.h }
      this.staticBlockers.push(rect)
      const spec = serverItem(item.kind)
      const art = spec?.art ? this.stageArt.items[spec.art] : undefined
      if (spec?.category === 'hazard') drawHazard(hazards, rect)
      else this.staticSolids.push(rect)
      if (art) this.staticsLayer.addChild(stretched(art.texture, rect))
    }
    this.staticsLayer.addChild(hazards)
  }

  private solids(): Solid[] {
    const moving = this.buffer
      .latest()
      .filter((e) => e.kind === 'moving_platform')
      .map((e) => ({ x: e.x, y: e.y, w: e.w, h: e.h, vx: e.vx, vy: e.vy }))
    return [...this.level.solids, ...this.staticSolids, ...moving]
  }

  // --- loop -------------------------------------------------------------
  private frame(seconds: number): void {
    if (this.phase === 'run' && this.predictor.active) {
      this.accumulator += Math.min(seconds, SIMULATION_DT * MAX_STEPS_PER_FRAME)
      while (this.accumulator >= SIMULATION_DT) {
        const input = this.input.snapshot()
        const seq = this.predictor.step(input, this.solids(), SIMULATION_DT)
        this.socket.send({ type: 'input', seq, ...input })
        this.accumulator -= SIMULATION_DT
      }
    } else {
      this.accumulator = 0
    }
    this.render(seconds)
  }

  private render(dt: number): void {
    const entities = this.buffer.sample(performance.now())
    this.renderPlatforms(entities)
    const focus = this.renderPlayers(entities, dt)
    const showWholeStage = this.phase !== 'run' || focus.length === 0
    this.camera.update(this.world, this.app.screen, showWholeStage ? [] : focus, dt)
    this.renderPlacement(dt)
  }

  private renderPlayers(entities: EntityState[], dt: number): Rect[] {
    const focus: Rect[] = []
    const seen = new Set<string>()
    for (const entity of entities) {
      if (entity.kind !== 'player' || !entity.player_id) continue
      const view = this.view(entity.player_id)
      seen.add(entity.player_id)
      const predicted = entity.player_id === this.myId ? this.predictor.renderPosition(dt) : null
      const body = this.predictor.body
      const x = predicted?.x ?? entity.x
      const y = predicted?.y ?? entity.y
      const alive = entity.state !== 'dead'
      view.character.container.visible = view.nameplate.container.visible = true
      view.character.update(x, y, {
        vx: predicted && body ? body.vx : entity.vx,
        vy: predicted && body ? body.vy : entity.vy,
        onGround: predicted && body ? body.onGround : Math.abs(entity.vy) < 1,
        alive,
      })
      view.nameplate.place(x + PHYSICS.playerWidth / 2, y + PHYSICS.playerHeight - CHARACTER_TOP)
      if (entity.player_id === this.myId && entity.state !== view.lastState) {
        if (entity.state === 'dead') this.onLocalEvent('died')
        if (entity.state === 'finished') this.onLocalEvent('finished')
      }
      view.lastState = entity.state
      if (entity.state === 'alive') focus.push({ x, y, w: PHYSICS.playerWidth, h: PHYSICS.playerHeight })
    }
    for (const [playerId, view] of this.views) {
      if (seen.has(playerId)) continue
      view.character.container.visible = view.nameplate.container.visible = false
      view.lastState = null
    }
    return focus
  }

  private renderPlatforms(entities: EntityState[]): void {
    const seen = new Set<number>()
    for (const entity of entities) {
      if (entity.kind !== 'moving_platform') continue
      seen.add(entity.id)
      let view = this.platforms.get(entity.id)
      if (!view) {
        view = this.platformView(entity)
        this.platforms.set(entity.id, view)
        this.platformsLayer.addChild(view)
      }
      view.position.set(entity.x, entity.y)
    }
    for (const [id, view] of this.platforms) {
      if (seen.has(id)) continue
      view.destroy({ children: true })
      this.platforms.delete(id)
    }
  }

  /** Moving structures show arrows on the art (design system §10). */
  private platformView(entity: EntityState): Container {
    const container = new Container()
    const art = this.stageArt.items['praticavel-longo']
    if (art) container.addChild(stretched(art.texture, { x: 0, y: 0, w: entity.w, h: entity.h }))
    const arrows = new Sprite(this.pathArrows)
    const scale = (entity.w * 0.6) / arrows.texture.width
    arrows.scale.set(scale)
    arrows.position.set((entity.w - arrows.width) / 2, -arrows.height - 2)
    container.addChild(arrows)
    return container
  }

  private view(playerId: string): PlayerView {
    let view = this.views.get(playerId)
    if (!view) {
      const player = this.players.find((p) => p.playerId === playerId)
      const color = tokens.players.find((p) => p.slot === player?.slot)?.color ?? tokens.players[0]!.color
      view = {
        character: new CharacterView(this.animations),
        nameplate: new Nameplate(player?.username ?? '???', color),
        lastState: null,
      }
      this.playersLayer.addChild(view.character.container, view.nameplate.container)
      this.views.set(playerId, view)
    }
    return view
  }

  // --- placement --------------------------------------------------------
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
    const spec = this.heldItem ? serverItem(this.heldItem) : undefined
    if (!spec) return
    const local = this.world.toLocal(event.global)
    const size = worldTokens.tileSize
    this.cursor = {
      shape: spec.shape,
      tileX: Math.floor(local.x / size - (spec.shape.tiles.w - 1) / 2),
      tileY: Math.floor(local.y / size - (spec.shape.tiles.h - 1) / 2),
    }
  }

  private cursorValid(): boolean {
    if (!this.cursor || !this.heldItem) return false
    const spec = serverItem(this.heldItem)
    if (!spec) return false
    if (!spec.requiresFreeSpace) {
      const area = footprint(this.cursor)
      return area.x >= 0 && area.y >= 0 && area.x + area.w <= this.level.pixelWidth && area.y + area.h <= this.level.pixelHeight
    }
    return canPlace(this.cursor, this.level, this.staticBlockers)
  }

  private placeAtCursor(): void {
    if (!this.cursor || !this.heldItem || !this.cursorValid()) return
    this.socket.send({ type: 'place_item', tile_x: this.cursor.tileX, tile_y: this.cursor.tileY })
    this.heldItem = null
    this.cursor = null
    this.placement?.show(false)
    this.onLocalEvent('placed')
  }

  private renderPlacement(dt: number): void {
    if (!this.heldItem) return
    const spec = serverItem(this.heldItem)
    const art = spec?.key === 'bomb' ? this.bombArt : spec?.art ? this.stageArt.items[spec.art] : undefined
    this.placement?.update(this.cursor && footprint(this.cursor), art, this.cursorValid(), dt)
  }
}

function stretched(texture: Texture, rect: Rect): Sprite {
  const sprite = new Sprite(texture)
  sprite.position.set(rect.x, rect.y)
  sprite.width = rect.w
  sprite.height = rect.h
  return sprite
}
