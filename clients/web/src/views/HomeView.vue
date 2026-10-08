<script setup lang="ts">
import OnAirSign from '@/components/OnAirSign.vue'
</script>

<template>
  <main class="grid h-dvh place-items-center p-8">
    <div class="flex w-full max-w-sm flex-col items-center gap-6 text-center">
      <OnAirSign lit />
      <p class="text-texto-suave">O único programa onde o cenário quer te derrubar.</p>
      <RouterLink to="/sandbox" class="btn btn-primario w-full">Treinar</RouterLink>
      <button class="btn btn-secundario w-full" disabled title="Em breve">Jogar online</button>
    </div>
  </main>
</template>
