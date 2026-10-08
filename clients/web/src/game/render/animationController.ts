import type { AnimationName } from './animationSet'

export interface MotionState {
  vx: number
  vy: number
  onGround: boolean
  alive: boolean
}

const MOVING_SPEED = 30
const RISING_SPEED = -120
const FALLING_SPEED = 120

const AIRBORNE: ReadonlySet<AnimationName> = new Set(['jumpAnticipation', 'jumpRise', 'jumpApex', 'fall'])
const RUNNING: ReadonlySet<AnimationName> = new Set(['runStart', 'run', 'turn'])

/**
 * Picks the animation from motion. Pure logic (no Pixi) so it is unit-testable and shared by
 * local and remote players. One-shot clips advance through their JSON `next` via `finished`.
 */
export class AnimationController {
  current: AnimationName = 'idle'
  facing: 1 | -1 = 1
  private oneShotPlaying = false
  private wasOnGround = true

  update(motion: MotionState, isOneShot: (name: AnimationName) => boolean): AnimationName {
    const next = this.choose(motion)
    this.wasOnGround = motion.onGround
    if (Math.abs(motion.vx) > MOVING_SPEED) this.facing = motion.vx > 0 ? 1 : -1
    if (next !== this.current) {
      this.current = next
      this.oneShotPlaying = isOneShot(next)
    }
    return this.current
  }

  /** Called when a non-looping clip ends; `next` comes from animations.json. */
  finished(next: AnimationName | undefined): AnimationName {
    this.oneShotPlaying = false
    if (next) this.current = next
    return this.current
  }

  private choose({ vx, vy, onGround, alive }: MotionState): AnimationName {
    if (!alive) return 'death'
    const moving = Math.abs(vx) > MOVING_SPEED
    const busy = this.oneShotPlaying

    if (!onGround) {
      if (vy < RISING_SPEED) {
        if (this.wasOnGround) return 'jumpRise'
        return AIRBORNE.has(this.current) && this.current !== 'fall' ? this.current : 'jumpRise'
      }
      if (vy > FALLING_SPEED) return 'fall'
      return busy && AIRBORNE.has(this.current) ? this.current : 'jumpApex'
    }

    if (!this.wasOnGround) return 'land'
    if (busy && this.current === 'land' && !moving) return 'land'

    if (moving) {
      const reversed = Math.sign(vx) !== this.facing
      if (reversed && RUNNING.has(this.current)) return 'turn'
      if (busy && (this.current === 'runStart' || this.current === 'turn')) return this.current
      if (this.current === 'run' || this.current === 'land') return 'run'
      return 'runStart'
    }

    if (RUNNING.has(this.current)) return 'brake'
    if (busy && this.current === 'brake') return 'brake'
    return 'idle'
  }
}
