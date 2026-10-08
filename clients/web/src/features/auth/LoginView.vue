<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { z } from 'zod'
import GameIcon from '@/components/GameIcon.vue'
import OnAirSign from '@/components/OnAirSign.vue'
import { apiErrorMessage } from '@/net/http'
import { useAuthStore } from './authStore'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const mode = ref<'login' | 'register'>('login')
const form = reactive({ username: '', email: '', password: '' })
const error = ref('')
const loading = ref(false)

const registerSchema = z.object({
  username: z.string().min(3, 'Nome com 3 a 32 letras').max(32).regex(/^\w+$/, 'Só letras, números e _'),
  email: z.string().email('E-mail inválido'),
  password: z.string().min(8, 'Senha com pelo menos 8 caracteres'),
})
const loginSchema = registerSchema.pick({ username: true }).extend({ password: z.string().min(1, 'Digite a senha') })

const title = computed(() => (mode.value === 'login' ? 'Entrar' : 'Criar conta'))

async function submit(): Promise<void> {
  error.value = ''
  const schema = mode.value === 'login' ? loginSchema : registerSchema
  const parsed = schema.safeParse(form)
  if (!parsed.success) {
    error.value = parsed.error.issues[0]?.message ?? 'Confira os campos'
    return
  }
  loading.value = true
  try {
    if (mode.value === 'login') await auth.login(form.username, form.password)
    else await auth.register(form.username, form.email, form.password)
    await router.push(typeof route.query.next === 'string' ? route.query.next : '/salas')
  } catch (e) {
    error.value = apiErrorMessage(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="grid min-h-dvh place-items-center p-8">
    <form class="flex w-full max-w-sm flex-col gap-4" novalidate @submit.prevent="submit">
      <div class="mb-2 flex justify-center"><OnAirSign size="sm" lit /></div>
      <div class="flex rounded-md border-3 border-tinta bg-fundo-poco p-1">
        <button
          v-for="m in ['login', 'register'] as const"
          :key="m"
          type="button"
          class="flex-1 rounded-sm py-2 font-label text-lg font-extrabold tracking-[0.04em] uppercase"
          :class="mode === m ? 'bg-fundo-elevado text-texto shadow-[inset_0_-4px_0_var(--color-no-ar)]' : 'text-texto-suave'"
          @click="mode = m"
        >
          {{ m === 'login' ? 'Entrar' : 'Criar conta' }}
        </button>
      </div>
      <label class="field">
        <span>Nome no programa</span>
        <input v-model.trim="form.username" autocomplete="username" maxlength="32" />
      </label>
      <label v-if="mode === 'register'" class="field">
        <span>E-mail</span>
        <input v-model.trim="form.email" type="email" autocomplete="email" />
      </label>
      <label class="field">
        <span>Senha</span>
        <input
          v-model="form.password"
          type="password"
          :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
        />
      </label>
      <p v-if="error" class="flex items-center gap-2 text-sm text-no-ar-brilho" role="alert">
        <GameIcon name="close" :size="20" />{{ error }}
      </p>
      <button class="btn btn-primario" :disabled="loading">
        <GameIcon name="play" :size="20" />{{ loading ? 'Entrando no ar…' : title }}
      </button>
      <RouterLink to="/" class="btn btn-fantasma"><GameIcon name="back" :size="20" />Voltar</RouterLink>
    </form>
  </main>
</template>
