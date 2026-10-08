<script setup lang="ts">
import gsap from 'gsap'
import { onBeforeUnmount, onMounted, useTemplateRef } from 'vue'

/** The ON AIR! studio sign (design system §2): logo, HUD and mechanic share this symbol. */
const props = defineProps<{ lit?: boolean }>()
const panel = useTemplateRef<HTMLDivElement>('panel')
let pulse: gsap.core.Tween | undefined

onMounted(() => {
  if (!props.lit || !panel.value) return
  // Lighting up: blink twice (60ms on, 80ms off), then stay on and pulse the glow (1.6s cycle).
  gsap
    .timeline()
    .set(panel.value, { '--lit': 0 })
    .to(panel.value, { '--lit': 1, duration: 0, delay: 0.3 })
    .to(panel.value, { '--lit': 0, duration: 0, delay: 0.06 })
    .to(panel.value, { '--lit': 1, duration: 0, delay: 0.08 })
    .to(panel.value, { '--lit': 0, duration: 0, delay: 0.06 })
    .to(panel.value, { '--lit': 1, duration: 0, delay: 0.08 })
    .add(() => {
      pulse = gsap.fromTo(
        panel.value,
        { '--glow': 0.6 },
        { '--glow': 0.85, duration: 0.8, yoyo: true, repeat: -1, ease: 'sine.inOut' },
      )
    })
})

onBeforeUnmount(() => pulse?.kill())
</script>

<template>
  <div
    ref="panel"
    class="sign relative w-[min(360px,100%)] rounded-[22px] bg-tinta p-3"
    :style="{ '--lit': 0, '--glow': 0.6 }"
  >
    <span v-for="c in ['top-2 left-2', 'top-2 right-2', 'bottom-2 left-2', 'bottom-2 right-2']" :key="c" :class="['absolute size-2 rounded-full bg-holofote', c]" />
    <div class="panel grid aspect-[336/116] place-items-center rounded-[14px] p-2">
      <div class="tube grid size-full place-items-center rounded-[9px]">
        <span class="font-display text-[clamp(2rem,10vw,3.25rem)] leading-none">ON AIR!</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel {
  background: color-mix(in srgb, var(--color-no-ar) calc(var(--lit) * 100%), var(--color-placa-apagada));
  box-shadow: 0 0 24px color-mix(in srgb, var(--color-no-ar-brilho) calc(var(--lit) * var(--glow) * 100%), transparent);
}
.tube {
  border: 3px solid color-mix(in srgb, var(--color-no-ar-brilho) calc(var(--lit) * 100%), transparent);
  color: color-mix(in srgb, var(--color-creme) calc(var(--lit) * 100%), var(--color-placa-texto-apagado));
}
</style>
