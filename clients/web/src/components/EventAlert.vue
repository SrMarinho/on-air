<script setup lang="ts">
import gsap from 'gsap'
import { nextTick, ref, useTemplateRef } from 'vue'

/** Big center catchphrase ("CAIU, PERDEU!") with the `pop` motion token (§16, §19.2). */
const text = ref('')
const el = useTemplateRef<HTMLParagraphElement>('el')

async function show(message: string): Promise<void> {
  text.value = message
  await nextTick()
  if (!el.value) return
  gsap.killTweensOf(el.value)
  gsap
    .timeline()
    .fromTo(el.value, { scale: 0, autoAlpha: 1 }, { scale: 1.1, duration: 0.17, ease: 'back.out(3)' })
    .to(el.value, { scale: 1, duration: 0.08 })
    .to(el.value, { autoAlpha: 0, duration: 0.22, delay: 0.9 })
}

defineExpose({ show })
</script>

<template>
  <p
    ref="el"
    class="pointer-events-none invisible absolute inset-x-0 top-1/4 text-center font-display text-4xl text-creme [-webkit-text-stroke:3px_var(--color-tinta)] [paint-order:stroke_fill]"
  >
    {{ text }}
  </p>
</template>
