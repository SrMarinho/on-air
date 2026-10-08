import { env } from '@/config/env'
import {
  serverMessageSchema,
  type ClientMessage,
  type ServerMessage,
  type ServerMessageOf,
  type ServerMessageType,
} from './protocol'

export type SocketStatus = 'idle' | 'connecting' | 'open' | 'closed'
type Handler<T extends ServerMessageType> = (message: ServerMessageOf<T>) => void
type AnyHandler = (message: ServerMessage) => void

const PING_INTERVAL_MS = 2000

/**
 * Typed WebSocket for the game server. Authenticates with the first frame, validates every
 * inbound frame with Zod, dispatches by `type`, and measures round-trip time.
 */
export class GameSocket {
  status: SocketStatus = 'idle'
  rttMs = 0
  private socket: WebSocket | null = null
  private pingTimer: number | undefined
  private readonly handlers = new Map<ServerMessageType, Set<AnyHandler>>()
  private readonly statusListeners = new Set<(status: SocketStatus, code?: number) => void>()

  connect(token: string, url: string = env.wsUrl): Promise<ServerMessageOf<'auth_ok'>> {
    this.close()
    this.setStatus('connecting')
    const socket = new WebSocket(url)
    this.socket = socket
    return new Promise((resolve, reject) => {
      const offAuth = this.once('auth_ok', (message) => {
        this.setStatus('open')
        this.startPing()
        resolve(message)
      })
      socket.onopen = () => this.send({ type: 'auth', token })
      socket.onmessage = (event) => this.receive(event.data)
      socket.onclose = (event) => {
        offAuth()
        this.stopPing()
        if (this.socket === socket) this.socket = null
        this.setStatus('closed', event.code)
        reject(new Error(`socket closed (${event.code})`))
      }
    })
  }

  send(message: ClientMessage): void {
    if (this.socket?.readyState === WebSocket.OPEN) this.socket.send(JSON.stringify(message))
  }

  on<T extends ServerMessageType>(type: T, handler: Handler<T>): () => void {
    // Safe: handlers are only ever called with messages of their own `type`.
    const erased = handler as unknown as AnyHandler
    const set = this.handlers.get(type) ?? new Set<AnyHandler>()
    set.add(erased)
    this.handlers.set(type, set)
    return () => set.delete(erased)
  }

  once<T extends ServerMessageType>(type: T, handler: Handler<T>): () => void {
    const off = this.on(type, (message) => {
      off()
      handler(message)
    })
    return off
  }

  onStatus(listener: (status: SocketStatus, code?: number) => void): () => void {
    this.statusListeners.add(listener)
    return () => this.statusListeners.delete(listener)
  }

  close(): void {
    this.stopPing()
    this.socket?.close()
    this.socket = null
  }

  private receive(raw: unknown): void {
    if (typeof raw !== 'string') return
    const parsed = serverMessageSchema.safeParse(JSON.parse(raw))
    if (!parsed.success) {
      console.warn('Invalid server message', parsed.error.issues)
      return
    }
    const message = parsed.data
    if (message.type === 'pong') this.rttMs = performance.now() - message.client_time
    this.handlers.get(message.type)?.forEach((handler) => handler(message))
  }

  private startPing(): void {
    this.stopPing()
    this.pingTimer = window.setInterval(
      () => this.send({ type: 'ping', client_time: performance.now() }),
      PING_INTERVAL_MS,
    )
  }

  private stopPing(): void {
    window.clearInterval(this.pingTimer)
  }

  private setStatus(status: SocketStatus, code?: number): void {
    this.status = status
    this.statusListeners.forEach((listener) => listener(status, code))
  }
}
