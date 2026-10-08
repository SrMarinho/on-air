import type { PlayerInputState } from '@/game/engine/physics'

const BINDINGS: Record<string, keyof PlayerInputState> = {
  ArrowLeft: 'left',
  KeyA: 'left',
  ArrowRight: 'right',
  KeyD: 'right',
  ArrowUp: 'jump',
  KeyW: 'jump',
  Space: 'jump',
}

export class KeyboardInput {
  private readonly state: PlayerInputState = { left: false, right: false, jump: false }
  private readonly onKey = (event: KeyboardEvent): void => {
    const action = BINDINGS[event.code]
    if (!action) return
    event.preventDefault()
    this.state[action] = event.type === 'keydown'
  }

  attach(target: Window = window): void {
    target.addEventListener('keydown', this.onKey)
    target.addEventListener('keyup', this.onKey)
  }

  detach(target: Window = window): void {
    target.removeEventListener('keydown', this.onKey)
    target.removeEventListener('keyup', this.onKey)
  }

  snapshot(): PlayerInputState {
    return { ...this.state }
  }
}
