import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAdminOrdersStore = defineStore('adminOrders', () => {
  // State
  const orders = ref([])
  const currentOrder = ref(null)
  const statistics = ref(null)
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
  const recentOrders = computed(() => orders.value.slice(0, 5))
  
  const statusCounts = computed(() => {
    const counts = {
      'В обработке': 0,
      'Собирается': 0,
      'Собран': 0,
      'В пути': 0,
      'Доставлен': 0,
      'Отменён': 0
    }
    orders.value.forEach(o => {
      if (counts[o.order_status] !== undefined) {
        counts[o.order_status]++
      }
    })
    return counts
  })

  // Actions
  const fetchAllOrders = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/admin/orders/', { params })
      
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
      if (err.response?.status === 403) {
        error.value = 'Недостаточно прав для просмотра заказов'
      } else {
        error.value = err.response?.data?.error || 'Ошибка загрузки заказов'
      }
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const fetchOrderDetail = async (orderId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get(`/admin/orders/${orderId}/`)
      currentOrder.value = response.data
      return { success: true, order: response.data }
    } catch (err) {
      error.value = err.response?.data?.error || 'Ошибка загрузки заказа'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const updateOrderStatus = async (orderId, newStatus) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post(`/admin/orders/${orderId}/update_status/`, {
        status: newStatus
      })
      
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
      error.value = err.response?.data?.error || 'Ошибка обновления статуса'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const fetchStatistics = async () => {
    try {
      const response = await api.get('/admin/orders/statistics/')
      statistics.value = response.data
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.error }
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    orders,
    currentOrder,
    statistics,
    loading,
    error,
    pagination,
    recentOrders,
    statusCounts,
    fetchAllOrders,
    fetchOrderDetail,
    updateOrderStatus,
    fetchStatistics,
    clearError
  }
})