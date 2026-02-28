import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useCartStore = defineStore('cart', () => {
  // State
  const basket = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const positions = computed(() => basket.value?.positions || [])
  const totalPrice = computed(() => basket.value?.total_price || 0)
  const totalItems = computed(() => basket.value?.total_items || 0)
  const isEmpty = computed(() => totalItems.value === 0)

  const itemCount = computed(() => {
    return positions.value.reduce((sum, pos) => sum + pos.product_quantity, 0)
  })

  // Actions
  const fetchBasket = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/basket/')
      basket.value = response.data
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Ошибка загрузки корзины'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const addToCart = async (productId, quantity = 1) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/basket/add_item/', {
        product_id: productId,
        quantity
      })
      basket.value = response.data
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Ошибка добавления в корзину'
      return { 
        success: false, 
        error: error.value,
        available: err.response?.data?.available 
      }
    } finally {
      loading.value = false
    }
  }

  const updateQuantity = async (positionId, quantity) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/basket/update_quantity/', {
        position_id: positionId,
        quantity
      })
      basket.value = response.data
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Ошибка обновления количества'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const removeFromCart = async (positionId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/basket/remove_item/', {
        position_id: positionId
      })
      basket.value = response.data
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Ошибка удаления из корзины'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const clearCart = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/basket/clear/')
      basket.value = response.data
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Ошибка очистки корзины'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    basket,
    loading,
    error,
    positions,
    totalPrice,
    totalItems,
    itemCount,
    isEmpty,
    fetchBasket,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    clearError
  }
})