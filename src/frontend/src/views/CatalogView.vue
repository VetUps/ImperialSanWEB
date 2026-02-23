<template>
  <v-container fluid class="pa-4">
    <v-row>
      <!-- Фильтры (по категориям) -->
      <v-col cols="12" md="3" v-if="showFiltersAndSort">
        <CategoryFilter 
          :model-value="catalogFilters.category"
          @filter="handleCategoryUpdate"
        />
        
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
            
            <div v-if="activeFiltersCount > 0" class="mt-4">
              <div class="text-caption font-weight-bold mb-1">Активные фильтры:</div>
              <v-chip
                v-for="filter in activeFilters"
                :key="filter.type"
                size="small"
                closable
                class="mr-1 mb-1"
                @click:close="clearFilter(filter.type)"
              >
                {{ filter.label }}
              </v-chip>
              <v-chip
                v-if="catalogFilters.brand"
                size="small"
                closable
                class="mr-1 mb-1"
                @click:close="clearFilter('brand')"
              >
                Бренд: {{ catalogFilters.brand }}
              </v-chip>
              <v-chip
                v-if="catalogFilters.availability"
                size="small"
                closable
                class="mr-1 mb-1"
                @click:close="clearFilter('availability')"
              >
                Наличие: {{ getAvailabilityLabel(catalogFilters.availability) }}
              </v-chip>
            </div>
            
            <v-btn
              v-if="activeFiltersCount > 0"
              size="small"
              variant="text"
              color="error"
              class="mt-2"
              @click="clearAllFilters"
            >
              <v-icon size="small" start>mdi-refresh</v-icon>
              Сбросить все
            </v-btn>
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
          
          <v-col cols="12" md="4" class="text-right" v-if="showFiltersAndSort">
            <v-text-field
              v-model="searchQuery"
              placeholder="Поиск..."
              prepend-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              @click:clear="onSearchClear"
            />
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
        
        <ProductList 
          :filters="catalogFilters"
          :sort-by="sortBy"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed } from 'vue'
import { useCatalogStore } from '@/store/catalog'
import { useAuthStore } from '@/store/auth'
import { debounce } from 'lodash'
import CategoryFilter from '@/components/catalog/CategoryFilter.vue'
import ProductList from '@/components/catalog/ProductList.vue'

const catalogStore = useCatalogStore()
const authStore = useAuthStore()

const totalProducts = computed(() => catalogStore.pagination?.totalProducts || 0)
const totalPages = computed(() => catalogStore.pagination?.totalPages || 1)
const currentPage = computed(() => catalogStore.pagination?.currentPage || 1)
const catalogFilters = computed(() => catalogStore.filters)
const sortBy = computed(() => catalogStore.sortBy)

const showFiltersAndSort = computed(() => {
  return authStore.isManager || authStore.isAdmin
})

const searchQuery = computed({
  get: () => catalogStore.filters.search || '',
  set: debounce((value) => {
    catalogStore.updateFilters({ search: value || '' })
    catalogStore.fetchProducts()
  }, 300)
})

const activeFiltersCount = computed(() => {
  let count = 0
  const f = catalogFilters.value
  if (f.category) count++
  if (f.search) count++
  if (f.minPrice != null) count++
  if (f.maxPrice != null) count++
  if (f.brand) count++
  if (f.availability) count++
  return count
})

const activeFilters = computed(() => {
  const filters = []
  const f = catalogFilters.value
  
  if (f.category) {
    filters.push({ type: 'category', label: `Категория: ${getCategoryName(f.category)}` })
  }
  if (f.search) {
    filters.push({ type: 'search', label: `Поиск: "${f.search}"` })
  }
  if (f.minPrice != null) {
    filters.push({ type: 'minPrice', label: `От: ${f.minPrice} ₽` })
  }
  if (f.maxPrice != null) {
    filters.push({ type: 'maxPrice', label: `До: ${f.maxPrice} ₽` })
  }
  
  return filters
})

const handleCategoryUpdate = (categoryId) => {
  catalogStore.updateFilters({ category: categoryId || null })
  console.log(categoryId)
  catalogStore.fetchProducts()
}

const clearFilter = (type) => {
  const updates = {}
  
  switch (type) {
    case 'category': updates.category = null; break
    case 'search': updates.search = ''; break
    case 'minPrice': updates.minPrice = null; break
    case 'maxPrice': updates.maxPrice = null; break
    case 'brand': updates.brand = null; break
    case 'availability': updates.availability = null; break
  }
  
  catalogStore.updateFilters(updates)
  catalogStore.fetchProducts()
}

const clearAllFilters = () => {
  catalogStore.clearFilters()
  catalogStore.fetchProducts()
}

const getAvailabilityLabel = (value) => {
  const labels = {
    'in_stock': 'В наличии',
    'out_of_stock': 'Нет в наличии',
    'low_stock': 'Мало'
  }
  return labels[value] || value
}

const getCategoryName = (categoryId) => {
  const category = catalogStore.categories?.find(c => c.category_id === categoryId)
  return category?.category_name || categoryId
}

const onSearchClear = () => {
  catalogStore.updateFilters({ search: '' })
  catalogStore.fetchProducts()
}

if (catalogStore.products.length === 0) {
  catalogStore.fetchCategories()
  catalogStore.fetchProducts()
}
</script>