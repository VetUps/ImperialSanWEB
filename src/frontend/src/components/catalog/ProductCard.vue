<template>
  <v-card
    class="product-card"
    hover
    :loading="loading"
    @click="goToProduct"
  >
    <v-img
      :src="imageUrl"
      height="200"
      cover
      class="product-image"
    >
      <template v-slot:placeholder>
        <v-row class="fill-height ma-0" align="center" justify="center">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </v-row>
      </template>

      <!-- Бейдж наличия -->
      <v-chip
        v-if="product.product_quantity_in_stock === 0"
        color="error"
        size="small"
        class="ma-2"
      >
        Нет в наличии
      </v-chip>
      <v-chip
        v-else-if="product.product_quantity_in_stock < 10"
        color="warning"
        size="small"
        class="ma-2"
      >
        Мало
      </v-chip>

      <!-- Бейдж категории -->
      <v-chip
        v-if="product.category_title"
        color="primary"
        size="small"
        class="ma-2"
        style="position: absolute; bottom: 8px; left: 8px;"
      >
        {{ product.category_title }}
      </v-chip>
    </v-img>

    <v-card-title class="text-subtitle-1 font-weight-bold product-title">
      {{ product.product_title }}
    </v-card-title>

    <v-card-subtitle class="pb-2">
      <div class="d-flex align-center">
        <v-icon size="small" class="mr-1" color="grey">mdi-factory</v-icon>
        <span class="text-caption">{{ product.product_brand_title || 'Без бренда' }}</span>
      </div>
    </v-card-subtitle>

    <v-card-text class="pt-0">
      <div class="d-flex justify-space-between align-center mb-2">
        <div class="text-h6 text-primary font-weight-bold">
          {{ formatPrice(product.product_price) }} ₽
        </div>

        <div class="text-caption text-disabled">
          <v-icon size="small" class="mr-1">mdi-package</v-icon>
          {{ product.product_quantity_in_stock }} шт.
        </div>
      </div>

      <div class="text-caption text-disabled mb-3 line-clamp-2">
        {{ product.product_description?.substring(0, 100) }}
        {{ product.product_description?.length > 100 ? '...' : '' }}
      </div>
    </v-card-text>

    <v-divider></v-divider>

    <v-card-actions class="pa-3">
      <v-btn
        color="primary"
        variant="tonal"
        size="small"
        @click.stop="handleAddToCart"
        :disabled="product.product_quantity_in_stock === 0 || !authStore.$state.isAuthenticated"
        :loading="addingToCart"
      >
        <v-icon left>mdi-cart-plus</v-icon>
        В корзину
      </v-btn>

      <v-spacer></v-spacer>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed, defineProps, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useCartStore } from '@/store/cart'

const authStore = useAuthStore()
const cartStore = useCartStore()
const router = useRouter()

const props = defineProps({
  product: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const addingToCart = ref(false)
const showSnackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

const imageUrl = computed(() => {
  return props.product.product_image_url ||
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSRo7whXykxuYBoms2CyYPY-Wf_eZD976fP5w&s'
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}

const goToProduct = () => {
  router.push(`/product/${props.product.product_id}`)
}

const handleAddToCart = async (event) => {
  event.stopPropagation()
  
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  addingToCart.value = true
  
  const result = await cartStore.addToCart(props.product.product_id, 1)
  
  addingToCart.value = false
  
  if (result.success) {
    snackbarText.value = 'Товар добавлен в корзину'
    snackbarColor.value = 'success'
  } else {
    snackbarText.value = result.error
    snackbarColor.value = 'error'
  }
  
  showSnackbar.value = true
}
</script>

<style scoped>
.product-card {
  cursor: pointer;
  transition: transform 0.2s;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(33, 150, 243, 0.15) !important;
}

.product-image {
  background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
}

.product-title {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 48px;
}

.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
</style>