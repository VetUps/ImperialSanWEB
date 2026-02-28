import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useOrdersStore = defineStore('orders', () => {
  // State
  const orders = ref([])
  const currentOrder = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    count: 0,
    num_pages: 1,
    current_page: 1,
    has_next: false,
    has_previous: false
  })

  // Getters
  const activeOrders = computed(() => 
    orders.value.filter(o => o.order_status !== 'Отменён' && o.order_status !== 'Доставлен')
  )

  const orderHistory = computed(() => 
    orders.value.filter(o => o.order_status === 'Отменён' || o.order_status === 'Доставлен')
  )

  // Actions
  const fetchOrders = async (page = 1, perPage = 10) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/orders/', {
        params: { page, per_page: perPage }
      })
      
      orders.value = response.data.results
      pagination.value = {
        count: response.data.count,
        num_pages: response.data.num_pages,
        current_page: response.data.current_page,
        has_next: response.data.has_next,
        has_previous: response.data.has_previous
      }
      
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || 'Ошибка загрузки заказов'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const fetchOrderDetail = async (orderId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get(`/orders/${orderId}/`)
      currentOrder.value = response.data
      return { success: true, order: response.data }
    } catch (err) {
      error.value = err.response?.data?.error || 'Ошибка загрузки заказа'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const createOrder = async (orderData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/orders/', orderData)
      currentOrder.value = response.data
      
      // Обновляем список заказов
      await fetchOrders()
      
      return { success: true, order: response.data }
    } catch (err) {
      error.value = err.response?.data?.error || 'Ошибка оформления заказа'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const cancelOrder = async (orderId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post(`/orders/${orderId}/cancel/`)
      
      // Обновляем в списке
      const index = orders.value.findIndex(o => o.order_id === orderId)
      if (index !== -1) {
        orders.value[index] = response.data
      }
      
      if (currentOrder.value?.order_id === orderId) {
        currentOrder.value = response.data
      }
      
      return { success: true, order: response.data }
    } catch (err) {
      error.value = err.response?.data?.error || 'Ошибка отмены заказа'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    orders,
    currentOrder,
    loading,
    error,
    pagination,
    activeOrders,
    orderHistory,
    fetchOrders,
    fetchOrderDetail,
    createOrder,
    cancelOrder,
    clearError
  }
})