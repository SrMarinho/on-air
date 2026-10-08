import { Application, Container, Graphics } from 'pixi.js'
import { hex, tokens } from '@/design/tokens'
import { overlaps, type Rect } from '@/game/engine/geometry'
import { parseLevel, type LevelLayout, type ParsedLevel } from '@/game/engine/level'
import { createBody, PHYSICS, SIMULATION_DT, stepPlayer, type PlayerBody } from '@/game/engine/physics'
import { KeyboardInput } from '@/game/input/keyboard'
import { loadAnimationSet } from '@/game/render/animationSet'
import { Camera } from '@/game/render/camera'
import { CharacterView } from '@/game/render/characterView'
import { LevelView } from '@/game/render/levelView'

const RESPAWN_DELAY = 1.2
const MAX_STEPS_PER_FRAME = 5

export type SandboxEvent = 'died' | 'finished'

/**
 * Offline playground: local simulation with the same physics as the server, no network.
 * Used to tune feel and art; the online client reuses engine/render pieces.
 */
export class SandboxGame {
  private readonly app = new Application()
  private readonly input = new KeyboardInput()
  private readonly world = new Container()
  private readonly hitbox = new Graphics()
  private level!: ParsedLevel
  private character!: CharacterView
  private camera!: Camera
  private body!: PlayerBody
  private alive = true
  private respawnIn = 0
  private accumulator = 0
  private onEvent: (event: SandboxEvent) => void = () => {}

  async mount(host: HTMLElement, layout: LevelLayout, character = 'calouro'): Promise<void> {
    await this.app.init({ resizeTo: host, background: hex(tokens.color.theme.estudio.fundo), antialias: true })
    host.appendChild(this.app.canvas)
    this.level = parseLevel(layout)
    this.camera = new Camera(this.level.pixelWidth, this.level.pixelHeight)
    this.character = new CharacterView(await loadAnimationSet(character))
    this.world.addChild(new LevelView(this.level).container, this.character.container, this.hitbox)
    this.app.stage.addChild(this.world)
    this.hitbox.visible = false
    this.input.attach()
    this.respawn()
    this.app.ticker.add((ticker) => this.frame(ticker.deltaMS / 1000))
  }

  on(handler: (event: SandboxEvent) => void): void {
    this.onEvent = handler
  }

  toggleHitbox(): void {
    this.hitbox.visible = !this.hitbox.visible
  }

  destroy(): void {
    this.input.detach()
    this.app.destroy(true, { children: true })
  }

  private frame(seconds: number): void {
    this.accumulator += Math.min(seconds, SIMULATION_DT * MAX_STEPS_PER_FRAME)
    while (this.accumulator >= SIMULATION_DT) {
      this.step(SIMULATION_DT)
      this.accumulator -= SIMULATION_DT
    }
    this.render(seconds)
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

  private end(event: SandboxEvent): void {
    this.alive = event !== 'died'
    this.respawnIn = RESPAWN_DELAY
    this.onEvent(event)
    if (event === 'finished') this.respawn()
  }

  private respawn(): void {
    const spawn = this.level.spawns[0] ?? { x: 0, y: 0 }
    const size = this.level.layout.tileSize
    this.body = createBody(
      spawn.x + (size - PHYSICS.playerWidth) / 2,
      spawn.y + size - PHYSICS.playerHeight,
    )
    this.alive = true
  }

  private render(dt: number): void {
    const { body } = this
    this.character.update(body.x, body.y, {
      vx: body.vx,
      vy: body.vy,
      onGround: body.onGround,
      alive: this.alive,
    })
    this.hitbox.clear().rect(body.x, body.y, PHYSICS.playerWidth, PHYSICS.playerHeight).stroke({
      color: hex(tokens.color.state.valido),
      width: 1,
    })
    this.camera.update(this.world, this.app.screen, [this.playerRect()], dt)
  }

  private playerRect(): Rect {
    return { x: this.body.x, y: this.body.y, w: PHYSICS.playerWidth, h: PHYSICS.playerHeight }
  }
}
