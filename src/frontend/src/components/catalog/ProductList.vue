<template>
  <div>
    <!-- Заголовок и фильтры -->
    <v-row class="mb-6" align="center">
      <v-col cols="12" md="6">
        <v-text-field
          v-if="showFiltersAndSort && !isMobile"
          v-model="searchQuery"
          placeholder="Поиск товаров..."
          prepend-icon="mdi-magnify"
          variant="outlined"
          density="comfortable"
          clearable
          @update:model-value="handleSearch"
          @click:clear="clearSearch"
        ></v-text-field>
      </v-col>
      
      <v-col cols="12" md="6" class="text-right">
        <!-- Кнопка фильтров -->
        <v-btn
          color="primary"
          variant="tonal"
          class="mr-2"
          @click="showFilters = !showFilters"
          v-if="showFiltersAndSort"
        >
          <v-icon left>mdi-filter</v-icon>
          Фильтры
          <v-badge
            v-if="activeFiltersCount > 0"
            color="error"
            :content="activeFiltersCount"
            inline
            class="ml-2"
          ></v-badge>
        </v-btn>
        
        <!-- Кнопка сортировки -->
        <v-btn
          color="primary"
          variant="tonal"
          class="mr-2"
          @click="showSortMenu = !showSortMenu"
          v-if="showFiltersAndSort"
        >
          <v-icon left>mdi-sort</v-icon>
          Сортировка
        </v-btn>
        
        <!-- Меню сортировки -->
        <v-menu
          v-model="showSortMenu"
          :close-on-content-click="false"
          v-if="showFiltersAndSort"
        >
          <template>
            <div style="display: none;"></div>
          </template>
          <v-card width="300">
            <v-card-text>
              <div class="text-subtitle-1 font-weight-bold mb-2">Сортировка</div>
              <v-radio-group v-model="sortBy">
                <v-radio
                  v-for="option in sortOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                  @click="applySort"
                ></v-radio>
              </v-radio-group>
            </v-card-text>
          </v-card>
        </v-menu>
        
        <!-- Кнопка добавления товара -->
        <v-btn
          color="primary"
          @click="goToProductCreate"
          v-if="isAdmin"
        >
          <v-icon left>mdi-plus</v-icon>
          Добавить товар
        </v-btn>
      </v-col>
    </v-row>
    
    <!-- Панель фильтров -->
    <v-expand-transition>
      <v-card v-if="showFilters && showFiltersAndSort" class="mb-6">
        <v-card-text>
          <v-row>
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="filters.category"
                :items="categories"
                item-title="category_title"
                item-value="category_id"
                label="Категория"
                clearable
                variant="outlined"
                density="comfortable"
                @update:model-value="applyFilters"
              ></v-select>
            </v-col>
            
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model.number="filters.minPrice"
                label="Цена от"
                type="number"
                prefix="₽"
                variant="outlined"
                density="comfortable"
                @blur="applyFilters"
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model.number="filters.maxPrice"
                label="Цена до"
                type="number"
                prefix="₽"
                variant="outlined"
                density="comfortable"
                @blur="applyFilters"
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="filters.brand"
                :items="brands"
                label="Бренд"
                clearable
                variant="outlined"
                density="comfortable"
                @update:model-value="applyFilters"
              ></v-select>
            </v-col>
            
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="filters.availability"
                :items="availabilityOptions"
                label="Наличие"
                clearable
                variant="outlined"
                density="comfortable"
                @update:model-value="applyFilters"
              ></v-select>
            </v-col>
            
            <v-col cols="12" sm="6" md="3" class="d-flex align-end">
              <v-btn
                color="error"
                variant="text"
                @click="clearAllFilters"
                :disabled="activeFiltersCount === 0"
              >
                <v-icon left>mdi-close</v-icon>
                Сбросить
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-expand-transition>
    
    <!-- Состояние загрузки -->
    <v-row v-if="loading">
      <v-col 
        v-for="n in 6" 
        :key="n" 
        cols="12" 
        sm="6" 
        md="4" 
        lg="3"
      >
        <v-skeleton-loader type="card"></v-skeleton-loader>
      </v-col>
    </v-row>
    
    <!-- Товары -->
    <v-row v-else-if="products.length > 0">
      <v-col 
        v-for="product in products" 
        :key="product.product_id" 
        cols="12" 
        sm="6" 
        md="4" 
        lg="3"
      >
        <ProductCard
          :product="product"
          @add-to-cart="handleAddToCart"
          @toggle-favorite="handleToggleFavorite"
        />
      </v-col>
    </v-row>
    
    <!-- Пустой результат -->
    <v-card v-else class="text-center pa-8">
      <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-package-variant-remove</v-icon>
      <h3 class="text-h6 mb-2">Товары не найдены</h3>
      <p class="text-body-1 text-disabled mb-4">
        Попробуйте изменить параметры поиска или фильтры
      </p>
      <v-btn color="primary" @click="clearAllFilters" v-if="showFiltersAndSort">
        Сбросить фильтры
      </v-btn>
    </v-card>
    
    <!-- Пагинация -->
    <div class="text-center mt-8" v-if="totalPages > 1">
      <v-pagination
        v-model="currentPage"
        :length="totalPages"
        :total-visible="7"
        @update:model-value="handlePageChange"
      ></v-pagination>
      
      <div class="text-caption text-disabled mt-2">
        Показано {{ products.length }} из {{ totalProducts }} товаров
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useCatalogStore } from '@/store/catalog'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'
import ProductCard from './ProductCard.vue'
import { debounce } from 'lodash'

const catalogStore = useCatalogStore()
const authStore = useAuthStore()
const router = useRouter()

// Используем стор напрямую без storeToRefs
const showFiltersAndSort = computed(() => {
  return authStore.isManager || authStore.isAdmin
})

const isAdmin = computed(() => authStore.isAdmin)

// Локальное состояние компонента
const showFilters = ref(false)
const showSortMenu = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const sortBy = ref('default')

// Фильтры (передаются на сервер)
const filters = reactive({
  category: null,
  minPrice: null,
  maxPrice: null,
  brand: null,
  availability: null
})

const sortOptions = [
  { label: 'По умолчанию', value: 'default' },
  { label: 'По цене (возрастание)', value: 'price_asc' },
  { label: 'По цене (убывание)', value: 'price_desc' },
  { label: 'По названию (А-Я)', value: 'title_asc' },
  { label: 'По названию (Я-А)', value: 'title_desc' },
  { label: 'По новизне', value: 'newest' }
]

const availabilityOptions = [
  { title: 'В наличии', value: 'in_stock' },
  { title: 'Нет в наличии', value: 'out_of_stock' },
  { title: 'Мало', value: 'low_stock' }
]

// Вычисляемые свойства из стора
const products = computed(() => catalogStore.products)
const categories = computed(() => catalogStore.categories)
const loading = computed(() => catalogStore.loading)
const pagination = computed(() => catalogStore.pagination)

const activeFiltersCount = computed(() => {
  let count = 0
  if (filters.category) count++
  if (filters.minPrice) count++
  if (filters.maxPrice) count++
  if (filters.brand) count++
  if (filters.availability) count++
  if (searchQuery.value) count++
  return count
})

const totalProducts = computed(() => pagination.value?.totalProducts || 0)
const totalPages = computed(() => pagination.value?.totalPages || 1)

const brands = computed(() => {
  const brandSet = new Set()
  products.value.forEach(product => {
    if (product.product_brand_title) {
      brandSet.add(product.product_brand_title)
    }
  })
  return Array.from(brandSet).sort()
})

// Загрузка данных при монтировании
onMounted(async () => {
  await catalogStore.fetchCategories()
  await fetchProducts()
})

// Функция для загрузки продуктов с фильтрами
const fetchProducts = async () => {
  const params = {
    page: currentPage.value,
    search: searchQuery.value,
    category: filters.category,
    min_price: filters.minPrice,
    max_price: filters.maxPrice,
    brand: filters.brand,
    availability: filters.availability,
    sort: sortBy.value !== 'default' ? sortBy.value : undefined
  }
  
  // Убираем пустые значения
  Object.keys(params).forEach(key => {
    if (params[key] === undefined || params[key] === null || params[key] === '') {
      delete params[key]
    }
  })
  
  console.log("Запрос на сервер с параметрами:", params)
  await catalogStore.fetchProducts(params)
}

// Обработчики событий
const handleSearch = debounce(() => {
  currentPage.value = 1
  fetchProducts()
}, 500)

const clearSearch = () => {
  searchQuery.value = ''
  currentPage.value = 1
  fetchProducts()
}

const applyFilters = () => {
  currentPage.value = 1
  fetchProducts()
}

const applySort = () => {
  showSortMenu.value = false
  fetchProducts()
}

const clearAllFilters = () => {
  searchQuery.value = ''
  filters.category = null
  filters.minPrice = null
  filters.maxPrice = null
  filters.brand = null
  filters.availability = null
  sortBy.value = 'default'
  
  currentPage.value = 1
  fetchProducts()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchProducts()
}

const handleAddToCart = (product) => {
  console.log('Add to cart:', product)
}

const handleToggleFavorite = ({ product, isFavorite }) => {
  console.log('Toggle favorite:', product, isFavorite)
}

const goToProductCreate = () => {
  router.push('/dashboard/products/create')
}
</script>