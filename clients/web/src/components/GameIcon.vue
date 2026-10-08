<script setup lang="ts">
import type { IconName } from './icons'

/** Icon from assets/ui/icons (design system §18). Sizes: 20 in buttons, 24 in lists, 32 in HUD. */
withDefaults(defineProps<{ name: IconName; size?: 20 | 24 | 32 | 48 }>(), { size: 24 })
</script>

<template>
  <img
    :src="`/ui/icons/${name}.png`"
    alt=""
    aria-hidden="true"
    draggable="false"
    class="inline-block shrink-0 object-contain select-none"
    :style="{ width: `${size}px`, height: `${size}px` }"
  />
</template>
