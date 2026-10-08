<script setup lang="ts">
import GameIcon from '@/components/GameIcon.vue'

/** Pause menu (§15.12): darkened 70%, "VOLTAMOS JÁ" break card with color bars on top. */
defineEmits<{ resume: []; exit: [] }>()

const bars = ['creme', 'holofote', 'turquesa', 'estado-pronto', 'confete', 'no-ar', 'estado-valido']
</script>

<template>
  <div class="absolute inset-0 z-20 grid place-items-center bg-fundo-poco/70 p-8">
    <div class="w-full max-w-md overflow-hidden rounded-lg border-3 border-tinta bg-fundo-elevado shadow-[0_6px_0_var(--color-sombra-pop)]">
      <div class="flex h-6">
        <span v-for="bar in bars" :key="bar" class="flex-1" :style="{ background: `var(--color-${bar})` }" />
      </div>
      <div class="flex flex-col items-center gap-6 p-6">
        <h2 class="font-display text-4xl leading-[38px]">Voltamos já</h2>
        <button class="btn btn-primario w-full" autofocus @click="$emit('resume')">
          <GameIcon name="play" :size="20" />Continuar
        </button>
        <button class="btn btn-fantasma w-full" @click="$emit('exit')">
          <GameIcon name="exit" :size="20" />Sair do programa
        </button>
      </div>
    </div>
  </div>
</template>
