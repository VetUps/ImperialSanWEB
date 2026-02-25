<template>
  <v-container fluid class="pa-4">
    <v-row>
      <v-col>
        <router-link to="/dashboard" class="text-decoration-none text-primary">
          <v-icon>mdi-arrow-left</v-icon> Назад к панели управления
        </router-link>
      </v-col>
    </v-row>
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-2">mdi-package-variant</v-icon>
          Управление товарами
        </h1>
      </v-col>
      <v-col class="text-right">
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="goToCreate"
        >
          Добавить товар
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-card-text>
        <v-text-field
          v-model="searchQuery"
          @update:model-value="handleSearch"
          prepend-icon="mdi-magnify"
          label="Поиск товаров"
          variant="outlined"
          density="comfortable"
          clearable
          class="mb-4"
        ></v-text-field>

        <v-data-table
          :headers="headers"
          :items="products"
          :loading="loading"
          :items-per-page="20"
          class="elevation-1"
        >
          <!-- Изображение -->
          <template v-slot:[`item.product_image_url`]="{ value }">
            <v-img
              :src="value || 'https://via.placeholder.com/50'"
              width="50"
              height="50"
              cover
              class="rounded"
            ></v-img>
          </template>

          <!-- Цена -->
          <template v-slot:[`item.product_price`]="{ value }">
            {{ formatPrice(value) }} ₽
          </template>

          <!-- Статус -->
          <template v-slot:[`item.product_is_active`]="{ value }">
            <v-chip :color="value ? 'success' : 'error'" size="small">
              {{ value ? 'Активен' : 'Неактивен' }}
            </v-chip>
          </template>

          <!-- Действия -->
          <template v-slot:[`item.actions`]="{ item }">
            <v-btn
              icon
              size="small"
              color="primary"
              variant="text"
              @click="editProduct(item.product_id)"
            >
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn
              v-if="item.product_is_active"
              icon
              size="small"
              color="error"
              variant="text"
              @click="confirmDelete(item)"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>

            <v-btn
              v-else
              icon
              size="small"
              color="green"
              variant="text"
              @click="activateProduct(item)"
            >
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Диалог подтверждения удаления -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">Подтверждение деактивации</v-card-title>
        <v-card-text>
          Вы уверены, что хотите деактивировать товар "{{ productToDelete?.product_title }}"?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showDeleteDialog = false">Отмена</v-btn>
          <v-btn color="error" @click="deleteProduct" :loading="loading">Деактивировать</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCatalogStore } from '@/store/catalog'
import { useRouter } from 'vue-router'
import { debounce } from 'lodash'

const router = useRouter()
const catalogStore = useCatalogStore()

const products = computed(() => catalogStore.products)
const loading = computed(() => catalogStore.loading)

const searchQuery = computed({
  get: () => catalogStore.filters.search,
  set: (value) => catalogStore.updateFilters({ search: value })
})

const showDeleteDialog = ref(false)
const productToDelete = ref(null)

const headers = [
  { title: 'Изображение', key: 'product_image_url', sortable: false },
  { title: 'Название', key: 'product_title' },
  { title: 'Цена', key: 'product_price' },
  { title: 'В наличии', key: 'product_quantity_in_stock' },
  { title: 'Категория', key: 'category_title' },
  { title: 'Бренд', key: 'product_brand_title' },
  { title: 'Статус', key: 'product_is_active' },
  { title: 'Действия', key: 'actions', sortable: false }
]

/*
const filteredProducts = computed(() => {
  if (!search.value) return products.value
  const query = search.value.toLowerCase()
  return products.value.filter(p =>
    p.product_title.toLowerCase().includes(query) ||
    p.product_brand_title?.toLowerCase().includes(query)
  )
})
  */

const handleSearch = debounce(() => {
  catalogStore.fetchProducts({ is_all: true })
  console.log(products)
}, 500)

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}

onMounted(async () => {
  await catalogStore.clearFilters()
  await catalogStore.fetchProducts({ is_all: true, sortById: true })
})

const goToCreate = () => {
  router.push('/dashboard/products/create')
}

const editProduct = (id) => {
  router.push(`/dashboard/products/edit/${id}`)
}

const confirmDelete = (product) => {
  productToDelete.value = product
  showDeleteDialog.value = true
}

const activateProduct = async (product) => {
  const result = await catalogStore.updateProduct(product.product_id, { product_is_active: true })
}

const deleteProduct = async () => {
  if (!productToDelete.value) return
  const result = await catalogStore.deleteProduct(productToDelete.value.product_id)
  await catalogStore.fetchProducts({ is_all: true, sortById: true })
  if (result.success) {
    showDeleteDialog.value = false
  }
}
</script>