/* eslint-disable */
import api from './api'

export const authService = {
  // Логин
  async login(credentials) {
    try {
      const response = await api.post('users/login/', credentials)
      return response.data
    } catch (error) {
      throw error.response?.data || error
    }
  },

  // Регистрация
  async register(userData) {
    try {
      const response = await api.post('users/register/', userData)
      return response.data
    } catch (error) {
      throw error.response?.data || error
    }
  },

  // Выход
  async logout() {
    try {
      await api.post('/logout/')
    } catch (error) {
      console.error('Logout error:', error)
    }
  },

  // Получение профиля
  async getProfile() {
    try {
      const response = await api.get('/users/me/')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Обновление профиля
  async updateProfile(userData) {
    try {
      const response = await api.patch(`/users/${userData.user_id}/`, userData)
      return response.data
    } catch (error) {
      throw error.response?.data || error
    }
  }
}