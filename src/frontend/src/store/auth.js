import { defineStore } from 'pinia'
import { authService } from '@/services/auth'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token'),
    loading: false,
    error: null
  }),

  getters: {
    fullName: (state) => {
      if (!state.user) return ''
      const surname = state.user.user_surname || ''
      const name = state.user.user_name || ''
      return `${surname} ${name}`.trim()
    },

    userRole: (state) => state.user?.user_role || 'User',

    isAdmin: (state) => state.user?.user_role === 'Admin',

    isManager: (state) =>
      state.user?.user_role === 'Manager' || state.user?.user_role === 'Admin',

    initials: (state) => {
      if (!state.user) return ''
      const first = state.user.user_surname?.charAt(0) || ''
      const second = state.user.user_name?.charAt(0) || ''
      return (first + second).toUpperCase()
    }
  },

  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null

      try {
        const response = await authService.login(credentials)
        const { user, token } = response

        this.user = user
        this.token = token
        this.isAuthenticated = true
        this.loading = false

        localStorage.setItem('user', JSON.stringify(user))
        localStorage.setItem('token', token)
        api.defaults.headers.common['Authorization'] = `Token ${token}`
        
        return { success: true, user }
      } catch (error) {
        this.loading = false
        this.error = error.detail || 'Ошибка входа. Проверьте email и пароль.'
        return { success: false, error: this.error }
      }
    },

    async register(userData) {
      this.loading = true
      this.error = null

      try {
        const response = await authService.register(userData)
        const { user, token } = response

        this.user = user
        this.token = token
        this.isAuthenticated = true
        this.loading = false

        localStorage.setItem('user', JSON.stringify(user))
        localStorage.setItem('token', token)
        api.defaults.headers.common['Authorization'] = `Token ${token}`

        return { success: true, user }
      } catch (error) {
        this.loading = false

        if (error.email) {
          this.error = error.email[0]
        } else if (error.detail) {
          this.error = error.detail
        } else {
          this.error = 'Ошибка регистрации'
        }

        return { success: false, error: error }
      }
    },

    async logout() {
      try {
        await authService.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.clearAuth()
      }
    },

    clearAuth() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      this.error = null

      localStorage.removeItem('user')
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    },

    async updateProfile(userData) {
      this.loading = true
      this.error = null

      try {
        const updatedUser = await authService.updateProfile(userData)
        this.user = updatedUser
        localStorage.setItem('user', JSON.stringify(updatedUser))

        this.loading = false
        return { success: true, user: updatedUser }
      } catch (error) {
        this.loading = false
        this.error = error.detail || 'Ошибка обновления профиля'
        return { success: false, error: this.error }
      }
    },

    clearError() {
      this.error = null
    }
  }
})