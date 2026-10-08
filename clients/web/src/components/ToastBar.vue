<script setup lang="ts">
import gsap from 'gsap'
import { nextTick, ref, useTemplateRef } from 'vue'
import GameIcon from './GameIcon.vue'
import type { IconName } from './icons'

/** Toast (§17.6): top strip, icon + text, stays 3s then slides up. */
const message = ref('')
const icon = ref<IconName>('check')
const el = useTemplateRef<HTMLDivElement>('el')

async function show(text: string, iconName: IconName = 'check'): Promise<void> {
  message.value = text
  icon.value = iconName
  await nextTick()
  if (!el.value) return
  gsap.killTweensOf(el.value)
  gsap
    .timeline()
    .fromTo(el.value, { yPercent: -150, autoAlpha: 1 }, { yPercent: 0, duration: 0.22, ease: 'power2.out' })
    .to(el.value, { yPercent: -150, duration: 0.22, ease: 'power2.in', delay: 3 })
}

defineExpose({ show })
</script>

<template>
  <div class="pointer-events-none fixed inset-x-0 top-0 z-50 flex justify-center p-4">
    <div
      ref="el"
      class="invisible flex items-center gap-3 rounded-md border-3 border-tinta bg-fundo-elevado px-4 py-3 shadow-[0_4px_0_var(--color-sombra-pop)]"
      role="status"
    >
      <GameIcon :name="icon" :size="24" />
      <span>{{ message }}</span>
    </div>
  </div>
</template>
