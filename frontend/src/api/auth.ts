import client from './client'

export const authApi = {
  login: (email: string, password: string) =>
    client.post('/auth/login', { email, password }),

  logout: (refreshToken: string) =>
    client.post('/auth/logout', { refresh_token: refreshToken }),

  refresh: (refreshToken: string) =>
    client.post('/auth/refresh', { refresh_token: refreshToken }),
}
