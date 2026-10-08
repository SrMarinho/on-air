import raw from '@design/tokens.json'

/** Design tokens (docs/design-system.md). The only place colors/sizes come from. */
export const tokens = raw

/** `#RRGGBB` → `0xRRGGBB` for Pixi. */
export function hex(color: string): number {
  return Number.parseInt(color.replace('#', ''), 16)
}

export const sprite = tokens.color.sprite
export const identity = tokens.color.identity
export const world = tokens.world
