import { http } from '@/net/http'
import { profileSchema, tokenResponseSchema, type Profile, type TokenResponse } from '@/net/protocol'

export const authApi = {
  async login(username: string, password: string): Promise<TokenResponse> {
    const { data } = await http.post('/auth/login', { username, password })
    return tokenResponseSchema.parse(data)
  },
  async register(username: string, email: string, password: string): Promise<TokenResponse> {
    const { data } = await http.post('/auth/register', { username, email, password })
    return tokenResponseSchema.parse(data)
  },
  async me(): Promise<Profile> {
    const { data } = await http.get('/players/me')
    return profileSchema.parse(data)
  },
}
