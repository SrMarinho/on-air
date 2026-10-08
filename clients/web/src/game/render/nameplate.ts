import { Container, Graphics, Text } from 'pixi.js'
import { hex, tokens } from '@/design/tokens'

const HEIGHT = 12
const PADDING_X = 5

/** World nameplate above a character (§16): pill in the player color, name in `nome-jogador`. */
export class Nameplate {
  readonly container = new Container()

  constructor(name: string, color: string) {
    const label = new Text({
      text: name.toUpperCase(),
      style: {
        fontFamily: tokens.font.label,
        fontWeight: '800',
        fontSize: 9,
        letterSpacing: 0.5,
        fill: hex(tokens.color.identity.tinta),
      },
      resolution: 4,
    })
    label.anchor.set(0.5)
    const width = label.width + PADDING_X * 2
    const pill = new Graphics()
      .roundRect(-width / 2, -HEIGHT / 2, width, HEIGHT, HEIGHT / 2)
      .fill(hex(color))
      .stroke({ color: hex(tokens.color.identity.tinta), width: 1.5 })
    this.container.addChild(pill, label)
  }

  /** `x` = character center, `top` = top of the character art. */
  place(x: number, top: number): void {
    this.container.position.set(x, top - HEIGHT)
  }
}
