import { z } from 'zod'
import { http } from '@/net/http'
import { roomSummarySchema, type RoomSummary } from '@/net/protocol'

export const roomsApi = {
  async list(): Promise<RoomSummary[]> {
    const { data } = await http.get('/rooms')
    return z.array(roomSummarySchema).parse(data)
  },
  async create(name: string): Promise<RoomSummary> {
    const { data } = await http.post('/rooms', { name })
    return roomSummarySchema.parse(data)
  },
}
