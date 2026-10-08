import { AnimatedSprite, Container } from 'pixi.js'
import { world } from '@/design/tokens'
import { PHYSICS } from '@/game/engine/physics'
import { AnimationController, type MotionState } from './animationController'
import type { Animation, AnimationName, AnimationSet } from './animationSet'

/** Character art is 1.25 tile tall; the hitbox is smaller so near misses feel fair (§5.1). */
const DISPLAY_HEIGHT = world.character.displayH

export class CharacterView {
  readonly container = new Container()
  private readonly sprite: AnimatedSprite
  private readonly controller = new AnimationController()
  private readonly set: AnimationSet
  private readonly baseScale: number
  private playing: Animation

  constructor(set: AnimationSet) {
    this.set = set
    this.baseScale = DISPLAY_HEIGHT / set.referenceHeight
    this.playing = this.animation('idle')
    this.sprite = new AnimatedSprite(this.playing.textures)
    this.sprite.onComplete = () => this.play(this.controller.finished(this.playing.next))
    this.container.addChild(this.sprite)
    this.play('idle')
  }

  /** `x, y` = hitbox top-left in world space. */
  update(x: number, y: number, motion: MotionState): void {
    const next = this.controller.update(motion, (name) => !this.animation(name).loop)
    if (next !== this.playing.name) this.play(next)
    this.container.position.set(x + PHYSICS.playerWidth / 2, y + PHYSICS.playerHeight)
    const scale = this.baseScale * this.playing.scale
    this.sprite.scale.set(scale * this.controller.facing, scale)
  }

  destroy(): void {
    this.container.destroy({ children: true })
  }

  /** Falls back to idle for clips whose sheet is not available yet. */
  private animation(name: AnimationName): Animation {
    const animation = this.set.animations[name] ?? this.set.animations.idle
    if (!animation) throw new Error(`${this.set.character} has no idle animation`)
    return animation
  }

  private play(name: AnimationName): void {
    const animation = this.animation(name)
    this.playing = animation
    this.sprite.textures = animation.textures
    this.sprite.animationSpeed = animation.speed
    this.sprite.loop = animation.loop
    this.sprite.anchor.set(animation.anchor.x, animation.anchor.y)
    this.sprite.gotoAndPlay(0)
  }
}
