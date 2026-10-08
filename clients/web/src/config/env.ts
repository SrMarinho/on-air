const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const env = {
  apiUrl,
  wsUrl: import.meta.env.VITE_WS_URL ?? `${apiUrl.replace(/^http/, 'ws')}/ws`,
} as const
