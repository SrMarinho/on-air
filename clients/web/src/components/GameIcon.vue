<script setup lang="ts">
/** Icon from assets/ui/icons (design system §18). Sizes: 20 in buttons, 24 in lists, 32 in HUD. */
export type IconName =
  | 'play' | 'pause' | 'settings' | 'players' | 'microphone' | 'trophy'
  | 'crown' | 'timer' | 'sound' | 'mute' | 'gamepad' | 'key'
  | 'copy' | 'share' | 'exit' | 'check' | 'close' | 'back'
  | 'star' | 'gong' | 'chat' | 'replay' | 'lock' | 'offline'

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
