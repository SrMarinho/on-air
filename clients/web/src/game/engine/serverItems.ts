import type { ItemShape } from './items'

export type ItemCategory = 'structure' | 'hazard' | 'effect' | 'bonus'

export interface ServerItem {
  /** Key used on the wire (backend `ItemDefinition.key`). */
  key: string
  label: string
  category: ItemCategory
  shape: ItemShape
  /** Bombs may cover anything; everything else needs free space. */
  requiresFreeSpace: boolean
  /** Entry in assets/gameplay/items.json used as world art, if any. */
  art?: string
  /** Image for item cards (relative to assets root). */
  cardImage?: string
}

const tile = (key: string, w: number, h: number, solid: boolean): ItemShape => ({
  key,
  tiles: { w, h },
  solids: solid ? [{ x: 0, y: 0, w, h }] : [],
})

/** Mirrors backend `default_item_registry()` in match/domain/items.py. */
export const SERVER_ITEMS: Record<string, ServerItem> = {
  block: {
    key: 'block',
    label: 'Praticável',
    category: 'structure',
    shape: tile('block', 1, 1, true),
    requiresFreeSpace: true,
    art: 'praticavel',
    cardImage: 'gameplay/structures/praticavel/praticavel.png',
  },
  plank: {
    key: 'plank',
    label: 'Praticável longo',
    category: 'structure',
    shape: tile('plank', 3, 1, true),
    requiresFreeSpace: true,
    art: 'praticavel-longo',
    cardImage: 'gameplay/structures/praticavel/praticavel-longo.png',
  },
  moving_platform: {
    key: 'moving_platform',
    label: 'Plataforma móvel',
    category: 'structure',
    shape: tile('moving_platform', 3, 1, true),
    requiresFreeSpace: true,
    art: 'praticavel-longo',
    cardImage: 'gameplay/structures/camera-rail/camera-rail.png',
  },
  spikes: {
    key: 'spikes',
    label: 'Espinhos',
    category: 'hazard',
    shape: tile('spikes', 1, 1, false),
    requiresFreeSpace: true,
  },
  bomb: {
    key: 'bomb',
    label: 'Dinamite',
    category: 'hazard',
    shape: tile('bomb', 3, 3, false),
    requiresFreeSpace: false,
    cardImage: 'effects/telegraphs/blast-cross.png',
  },
}

export function serverItem(key: string): ServerItem | undefined {
  return SERVER_ITEMS[key]
}
