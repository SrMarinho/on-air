import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { env } from '@/config/env'
import { tokenResponseSchema } from './protocol'
import { tokenStorage } from './tokenStorage'

/** REST client: bearer token on every call, one transparent refresh on 401. */
export const http = axios.create({ baseURL: env.apiUrl, timeout: 10_000 })

http.interceptors.request.use((config) => {
  const tokens = tokenStorage.load()
  if (tokens) config.headers.Authorization = `Bearer ${tokens.access_token}`
  return config
})

let refreshing: Promise<boolean> | null = null

async function refreshTokens(): Promise<boolean> {
  const tokens = tokenStorage.load()
  if (!tokens) return false
  try {
    const { data } = await axios.post(`${env.apiUrl}/auth/refresh`, { refresh_token: tokens.refresh_token })
    tokenStorage.save(tokenResponseSchema.parse(data))
    return true
  } catch {
    tokenStorage.clear()
    return false
  }
}

http.interceptors.response.use(undefined, async (error: AxiosError) => {
  const original = error.config as (InternalAxiosRequestConfig & { _retried?: boolean }) | undefined
  const isAuthCall = original?.url?.startsWith('/auth/')
  if (error.response?.status !== 401 || !original || original._retried || isAuthCall) throw error
  original._retried = true
  refreshing ??= refreshTokens().finally(() => (refreshing = null))
  if (!(await refreshing)) throw error
  return http(original)
})

/** Message from a `{code, message}` API error (or a fallback). */
export function apiErrorMessage(error: unknown, fallback = 'Algo deu errado. Tente de novo.'): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as { message?: string; detail?: unknown } | undefined
    if (data?.message) return data.message
    if (error.code === 'ERR_NETWORK') return 'Saímos do ar! O servidor não respondeu.'
  }
  return fallback
}

export { refreshTokens }
