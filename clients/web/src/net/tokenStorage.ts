import type { TokenResponse } from './protocol'

const KEY = 'onair.tokens'

/** Persists the JWT pair. Wrapped in try/catch: storage may be unavailable (private mode). */
export const tokenStorage = {
  load(): TokenResponse | null {
    try {
      const raw = localStorage.getItem(KEY)
      return raw ? (JSON.parse(raw) as TokenResponse) : null
    } catch {
      return null
    }
  },
  save(tokens: TokenResponse): void {
    try {
      localStorage.setItem(KEY, JSON.stringify(tokens))
    } catch {
      /* session-only login */
    }
  },
  clear(): void {
    try {
      localStorage.removeItem(KEY)
    } catch {
      /* nothing stored */
    }
  },
}
