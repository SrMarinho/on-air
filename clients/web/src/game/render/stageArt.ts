import { Assets, Rectangle, Texture } from 'pixi.js'
import { z } from 'zod'

const rectSchema = z.object({ x: z.number(), y: z.number(), w: z.number(), h: z.number() })

const tilesetSchema = z.object({
  texture: z.string(),
  tiles: z.array(z.string()),
  frames: z.record(z.string(), rectSchema),
})

const itemsSchema = z.record(
  z.string(),
  z.object({
    texture: z.string(),
    category: z.enum(['structure', 'hazard', 'effect', 'bonus', 'fixed']),
    tiles: z.object({ w: z.number().int().positive(), h: z.number().int().positive() }),
    serverItem: z.string().optional(),
    bounds: rectSchema.optional(),
  }),
)

export type FloorTile =
  | 'top'
  | 'top-left'
  | 'top-right'
  | 'top-narrow'
  | 'top-left-alt'
  | 'top-right-alt'
  | 'fill'
  | 'fill-base'

export interface ItemArt {
  texture: Texture
  /** Full image URL, for DOM previews (item cards). */
  url: string
  tiles: { w: number; h: number }
  category: z.infer<typeof itemsSchema>[string]['category']
}

export interface StageArt {
  floor: Record<FloorTile, Texture>
  items: Record<string, ItemArt>
}

const FLOOR_DIR = '/environment/tiles/studio/floor'
const ITEMS_DIR = '/gameplay'

/** Loads `items.json` and the studio floor tileset, cropping each texture to its opaque area. */
export async function loadStageArt(): Promise<StageArt> {
  const [floorSpec, itemsSpec] = await Promise.all([
    fetchJson(`${FLOOR_DIR}/studio-floor.json`, tilesetSchema),
    fetchJson(`${ITEMS_DIR}/items.json`, itemsSchema),
  ])

  const floorSheet = await Assets.load<Texture>(`${FLOOR_DIR}/${floorSpec.texture}`)
  const floor = Object.fromEntries(
    Object.entries(floorSpec.frames).map(([name, r]) => [name, crop(floorSheet, r)]),
  ) as Record<FloorTile, Texture>

  const items = Object.fromEntries(
    await Promise.all(
      Object.entries(itemsSpec).map(async ([key, spec]) => {
        const url = `${ITEMS_DIR}/${spec.texture}`
        const sheet = await Assets.load<Texture>(url)
        const art: ItemArt = {
          texture: spec.bounds ? crop(sheet, spec.bounds) : sheet,
          url,
          tiles: spec.tiles,
          category: spec.category,
        }
        return [key, art] as const
      }),
    ),
  )
  return { floor, items }
}

async function fetchJson<T>(url: string, schema: z.ZodType<T>): Promise<T> {
  return schema.parse(await (await fetch(url)).json())
}

function crop(sheet: Texture, r: z.infer<typeof rectSchema>): Texture {
  return new Texture({ source: sheet.source, frame: new Rectangle(r.x, r.y, r.w, r.h) })
}
