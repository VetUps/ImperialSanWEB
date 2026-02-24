import { defineStore } from 'pinia'
import api from '@/services/api'

export const useCatalogStore = defineStore('catalog', {
  state: () => ({
    products: [],
    categories: [],
    currentProduct: null,
    pagination: {
      currentPage: 1,
      totalPages: 1,
      totalProducts: 0,
      pageSize: 20
    },
    loading: false,
    error: null,

    filters: {
      search: '',
      category: null,
      minPrice: null,
      maxPrice: null,
      brand: null,
      availability: null,
      is_all: false
    },
    sortBy: 'default'
  }),

  getters: {
    activeFiltersCount: (state) => {
      let count = 0
      const f = state.filters
      if (f.search) count++
      if (f.category) count++
      if (f.minPrice != null) count++
      if (f.maxPrice != null) count++
      if (f.brand) count++
      if (f.availability) count++
      return count
    },

    apiParams: (state) => {
      const params = {
        page: state.pagination.currentPage,
        search: state.filters.search || undefined,
        category: state.filters.category || undefined,
        min_price: state.filters.minPrice || undefined,
        max_price: state.filters.maxPrice || undefined,
        brand: state.filters.brand || undefined,
        availability: state.filters.availability || undefined,
        sort: state.sortBy !== 'default' ? state.sortBy : undefined,
        is_all: state.is_all
      }
      
      // Удаляем пустые значения
      Object.keys(params).forEach(key => {
        if (params[key] === undefined || params[key] === null || params[key] === '') {
          delete params[key]
        }
      })
      
      return params
    },

    categoryTree: (state) => {
      const buildTree = (parentId = null) => {
        const children = state.categories
          .filter(cat => cat.parent_category_id === parentId)
          .map(cat => {
            const subChildren = buildTree(cat.category_id)
            const node = {
              ...cat,
              children: subChildren
            }
            if (subChildren.length === 0) {
              delete node.children
            }
            return node
          })
        return children
      }
      return buildTree()
    }
  },

  actions: {
    async fetchProducts(overrideParams = {}) {
      this.loading = true
      this.error = null

      try {
        // Объединяем параметры из store с возможными переопределениями
        const params = { ...this.apiParams, ...overrideParams }
        
        const response = await api.get('/products/', { params })
        
        this.products = response.data.results || response.data
        this.pagination = {
          currentPage: response.data.current_page || 1,
          totalPages: response.data.total_pages || 1,
          totalProducts: response.data.total_objects || 0,
          pageSize: response.data.page_size || 20
        }
      } catch (error) {
        this.error = 'Ошибка загрузки товаров'
        console.error('Fetch products error:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchProductsWithDebounce() { 
      return this.fetchProducts()
    },

    async fetchCategories() {
      try {
        const response = await api.get('/categories/')
        this.categories = response.data
      } catch (error) {
        console.error('Fetch categories error:', error)
      }
    },

    async fetchProductById(id) {
      this.loading = true
      this.error = null

      try {
        const response = await api.get(`/products/${id}/`)
        this.currentProduct = response.data
        return this.currentProduct
      } catch (error) {
        this.error = 'Ошибка загрузки товара'
        console.error('Fetch product error:', error)
        return null
      } finally {
        this.loading = false
      }
    },

    async createProduct(productData) {
      this.loading = true
      this.error = null

      try {
        const response = await api.post('/products/', productData)
        this.products.unshift(response.data)
        return { success: true, product: response.data }
      } catch (error) {
        this.error = error.response?.data || 'Ошибка создания товара'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async updateProduct(id, productData) {
      this.loading = true
      this.error = null

      try {
        const response = await api.patch(`/products/${id}/`, productData)

        const index = this.products.findIndex(p => p.product_id === id)
        if (index !== -1) {
          this.products[index] = response.data
        }

        return { success: true, product: response.data }
      } catch (error) {
        this.error = error.response?.data || 'Ошибка обновления товара'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async deleteProduct(id) {
      this.loading = true
      this.error = null

      try {
        await api.delete(`/products/${id}/`)
        this.fetchProducts({ is_all: true })
        return { success: true }
      } catch (error) {
        this.error = 'Ошибка удаления товара'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    clearError() {
      this.error = null
    },

    updateFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
      this.pagination.currentPage = 1
    },

    updateSort(sortValue) {
      this.sortBy = sortValue
      this.pagination.currentPage = 1
    },

    clearFilters() {
      this.filters = {
        search: '',
        category: null,
        minPrice: null,
        maxPrice: null,
        brand: null,
        availability: null
      }
      this.sortBy = 'default'
      this.pagination.currentPage = 1
    },

    setPage(page) {
      this.pagination.currentPage = page
    },
  }
})