import { Assets, Rectangle, Texture } from 'pixi.js'
import { z } from 'zod'

export const ANIMATION_NAMES = [
  'idle',
  'runStart',
  'run',
  'brake',
  'turn',
  'jumpAnticipation',
  'jumpRise',
  'jumpApex',
  'fall',
  'land',
  'hit',
  'death',
  'build',
] as const
export type AnimationName = (typeof ANIMATION_NAMES)[number]

const animationNameSchema = z.enum(ANIMATION_NAMES)

/** Authored timing + geometry filled by `scripts/assets/build_animations.py`. */
const animationSpecSchema = z.object({
  texture: z.string(),
  frames: z.number().int().positive(),
  columns: z.number().int().positive(),
  duration: z.number().positive(),
  loop: z.boolean(),
  next: animationNameSchema.optional(),
  frameWidth: z.number().positive().optional(),
  frameHeight: z.number().positive().optional(),
  scale: z.number().positive().optional(),
  anchor: z.object({ x: z.number(), y: z.number() }).optional(),
  referenceHeight: z.number().positive().optional(),
})
const animationFileSchema = z.partialRecord(animationNameSchema, animationSpecSchema)

export interface Animation {
  name: AnimationName
  textures: Texture[]
  /** Pixi `animationSpeed` at 60fps ticker. */
  speed: number
  loop: boolean
  next: AnimationName | undefined
  /** Multiplier that brings this sheet to the same character height as `idle`. */
  scale: number
  anchor: { x: number; y: number }
}

export interface AnimationSet {
  character: string
  referenceHeight: number
  animations: Partial<Record<AnimationName, Animation>>
}

/** Loads `<character>/data/animations.json`, skipping sheets whose geometry is not built yet. */
export async function loadAnimationSet(character: string): Promise<AnimationSet> {
  const base = `/characters/${character}`
  const file = animationFileSchema.parse(await (await fetch(`${base}/data/animations.json`)).json())
  const ready = Object.entries(file).filter(
    (entry): entry is [AnimationName, z.infer<typeof animationSpecSchema>] =>
      entry[1]?.frameWidth !== undefined,
  )
  const animations = await Promise.all(
    ready.map(async ([name, spec]) => {
      const sheet = await Assets.load<Texture>(`${base}/sprites/${spec.texture}`)
      const fw = spec.frameWidth ?? sheet.width / spec.columns
      const fh = spec.frameHeight ?? sheet.height
      const textures = Array.from({ length: spec.frames }, (_, i) => {
        const frame = new Rectangle((i % spec.columns) * fw, Math.floor(i / spec.columns) * fh, fw, fh)
        return new Texture({ source: sheet.source, frame })
      })
      const animation: Animation = {
        name,
        textures,
        speed: (spec.frames / spec.duration) * (1000 / 60),
        loop: spec.loop,
        next: spec.next,
        scale: spec.scale ?? 1,
        anchor: spec.anchor ?? { x: 0.5, y: 1 },
      }
      return animation
    }),
  )
  const referenceHeight = file.idle?.referenceHeight
  if (!referenceHeight) throw new Error(`${character}: idle animation has no referenceHeight`)
  return {
    character,
    referenceHeight,
    animations: Object.fromEntries(animations.map((a) => [a.name, a])),
  }
}
