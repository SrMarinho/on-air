<script setup lang="ts">
import GameIcon from '@/components/GameIcon.vue'
import OnAirSign from '@/components/OnAirSign.vue'
</script>

<template>
  <main class="grid h-dvh place-items-center p-8">
    <div class="flex w-full max-w-sm flex-col items-center gap-6 text-center">
      <OnAirSign lit />
      <p class="text-texto-suave">O único programa onde o cenário quer te derrubar.</p>
      <RouterLink to="/salas" class="btn btn-primario w-full"><GameIcon name="players" :size="20" />Jogar online</RouterLink>
      <RouterLink to="/sandbox" class="btn btn-secundario w-full"><GameIcon name="play" :size="20" />Treinar</RouterLink>
    </div>
  </main>
</template>
