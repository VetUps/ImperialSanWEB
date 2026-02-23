<template>
  <v-container fluid class="pa-4">
    <v-row>
      <!-- Фильтры (по категориям) -->
      <v-col cols="12" md="3" v-if="showFiltersAndSort">
        <CategoryFilter @filter="handleCategoryFilter" />
        
        <v-card class="mt-4">
          <v-card-title class="text-subtitle-1 font-weight-bold">
            <v-icon left>mdi-information</v-icon>
            Информация
          </v-card-title>
          <v-card-text>
            <div class="text-caption text-disabled mb-2">
              Найдено товаров: {{ totalProducts }}
            </div>
            <div class="text-caption text-disabled">
              Страница: {{ currentPage }} из {{ totalPages }}
            </div>
            
            <!-- Текущие фильтры -->
            <div v-if="activeFiltersCount > 0" class="mt-4">
              <div class="text-caption font-weight-bold mb-1">Активные фильтры:</div>
              <v-chip
                v-for="filter in activeFilters"
                :key="filter.label"
                size="small"
                closable
                class="mr-1 mb-1"
                @click:close="clearFilter(filter.type)"
              >
                {{ filter.label }}
              </v-chip>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Основной контент -->
      <v-col cols="12" :md="showFiltersAndSort ? 9 : 12">
        <v-row class="mb-4" align="center">
          <v-col cols="12" md="8">
            <h1 class="text-h4 font-weight-bold text-primary">Каталог товаров</h1>
            <p class="text-body-1 text-disabled mt-2">
              Сантехника и инженерное оборудование
            </p>
          </v-col>
        </v-row>
        
        <v-alert
          v-if="!showFiltersAndSort"
          type="info"
          variant="tonal"
          class="mb-4"
        >
          <div class="d-flex align-center">
            <span>
              Фильтрация и сортировка доступны только менеджерам и администраторам.
            </span>
          </div>
        </v-alert>
        
        <ProductList />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed } from 'vue'
import { useCatalogStore } from '@/store/catalog'
import { useAuthStore } from '@/store/auth'
import CategoryFilter from '@/components/catalog/CategoryFilter.vue'
import ProductList from '@/components/catalog/ProductList.vue'

const catalogStore = useCatalogStore()
const authStore = useAuthStore()

const totalProducts = computed(() => catalogStore.pagination?.totalProducts || 0)
const totalPages = computed(() => catalogStore.pagination?.totalPages || 1)
const currentPage = computed(() => catalogStore.pagination?.currentPage || 1)
const catalogFilters = computed(() => catalogStore.filters || {})

const showFiltersAndSort = computed(() => {
  return authStore.isManager || authStore.isAdmin
})

const activeFiltersCount = computed(() => {
  let count = 0
  const filterObj = catalogFilters.value
  if (filterObj.category) count++
  if (filterObj.search) count++
  if (filterObj.minPrice) count++
  if (filterObj.maxPrice) count++
  return count
})

const activeFilters = computed(() => {
  const filters = []
  const filterObj = catalogFilters.value
  
  if (filterObj.category) {
    filters.push({ 
      type: 'category', 
      label: `Категория: ${filterObj.category}` 
    })
  }
  
  if (filterObj.search) {
    filters.push({ 
      type: 'search', 
      label: `Поиск: "${filterObj.search}"` 
    })
  }
  
  if (filterObj.minPrice) {
    filters.push({ 
      type: 'minPrice', 
      label: `Цена от: ${filterObj.minPrice} ₽` 
    })
  }
  
  if (filterObj.maxPrice) {
    filters.push({ 
      type: 'maxPrice', 
      label: `Цена до: ${filterObj.maxPrice} ₽` 
    })
  }
  
  return filters
})

const handleCategoryFilter = (categoryId) => {
  console.log(`Выбранная категория: ${categoryId}`)
  const params = {
  }

  catalogStore.setFilters({ category: categoryId })
  catalogStore.fetchProducts(params)
}

const clearFilter = () => {
  catalogStore.fetchProducts()
}
</script>