import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { refreshTokens } from '@/net/http'
import type { Profile, TokenResponse } from '@/net/protocol'
import { tokenStorage } from '@/net/tokenStorage'
import { authApi } from './authApi'

export const useAuthStore = defineStore('auth', () => {
  const profile = ref<Profile | null>(null)
  const restored = ref(false)
  const isLoggedIn = computed(() => profile.value !== null)

  async function accept(tokens: TokenResponse): Promise<void> {
    tokenStorage.save(tokens)
    profile.value = await authApi.me()
  }

  async function login(username: string, password: string): Promise<void> {
    await accept(await authApi.login(username, password))
  }

  async function register(username: string, email: string, password: string): Promise<void> {
    await accept(await authApi.register(username, email, password))
  }

  /** Restore a previous session from storage (once per page load). */
  async function restore(): Promise<void> {
    if (restored.value) return
    restored.value = true
    if (!tokenStorage.load()) return
    try {
      profile.value = await authApi.me()
    } catch {
      tokenStorage.clear()
    }
  }

  /** Fresh access token for the WebSocket handshake. */
  async function accessToken(): Promise<string | null> {
    await refreshTokens()
    return tokenStorage.load()?.access_token ?? null
  }

  function logout(): void {
    tokenStorage.clear()
    profile.value = null
  }

  return { profile, isLoggedIn, login, register, restore, accessToken, logout }
})
