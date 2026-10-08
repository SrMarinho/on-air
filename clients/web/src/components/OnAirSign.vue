<script setup lang="ts">
import gsap from 'gsap'
import { onBeforeUnmount, onMounted, useTemplateRef, watch } from 'vue'

/**
 * The ON AIR! studio sign (design system §2): logo, HUD and mechanic share this symbol.
 * Off → lighting up blinks twice (60ms on / 80ms off) → on, with the glow pulsing on a 1.6s cycle.
 */
const props = withDefaults(defineProps<{ lit?: boolean; size?: 'lg' | 'sm' }>(), {
  lit: false,
  size: 'lg',
})
const panel = useTemplateRef<HTMLDivElement>('panel')
let timeline: gsap.core.Timeline | undefined
let pulse: gsap.core.Tween | undefined

function stop(): void {
  timeline?.kill()
  pulse?.kill()
}

function apply(lit: boolean): void {
  const el = panel.value
  if (!el) return
  stop()
  if (!lit) {
    gsap.set(el, { '--lit': 0 })
    return
  }
  timeline = gsap
    .timeline()
    .set(el, { '--lit': 1 }, 0.1)
    .set(el, { '--lit': 0 }, 0.16)
    .set(el, { '--lit': 1 }, 0.24)
    .set(el, { '--lit': 0 }, 0.3)
    .set(el, { '--lit': 1 }, 0.38)
    .add(() => {
      pulse = gsap.fromTo(el, { '--glow': 0.6 }, { '--glow': 0.85, duration: 0.8, yoyo: true, repeat: -1, ease: 'sine.inOut' })
    })
}

onMounted(() => apply(props.lit))
watch(() => props.lit, apply)
onBeforeUnmount(stop)
</script>

<template>
  <div
    ref="panel"
    class="relative bg-tinta"
    :class="size === 'lg' ? 'w-[min(360px,100%)] rounded-[22px] p-3' : 'w-[120px] rounded-[10px] p-1.5'"
    :style="{ '--lit': 0, '--glow': 0.6 }"
    role="img"
    :aria-label="lit ? 'No ar' : 'Fora do ar'"
  >
    <template v-if="size === 'lg'">
      <span
        v-for="c in ['top-2 left-2', 'top-2 right-2', 'bottom-2 left-2', 'bottom-2 right-2']"
        :key="c"
        :class="['absolute size-2 rounded-full bg-holofote', c]"
      />
    </template>
    <div class="panel grid aspect-[336/116] place-items-center p-[4%]" :class="size === 'lg' ? 'rounded-[14px]' : 'rounded-[6px]'">
      <div class="tube grid size-full place-items-center" :class="size === 'lg' ? 'rounded-[9px] border-3' : 'rounded-[4px] border-2'">
        <span class="font-display leading-none" :class="size === 'lg' ? 'text-[clamp(2rem,10vw,3.25rem)]' : 'text-[17px]'">
          ON AIR!
        </span>
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
  border-color: color-mix(in srgb, var(--color-no-ar-brilho) calc(var(--lit) * 100%), transparent);
  color: color-mix(in srgb, var(--color-creme) calc(var(--lit) * 100%), var(--color-placa-texto-apagado));
}
</style>
