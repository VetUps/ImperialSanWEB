<template>
  <v-container class="py-6">
    <h1 class="text-h4 font-weight-bold mb-6 primary--text">
      <v-icon size="36" class="mr-2" color="primary">mdi-cart</v-icon>
      Корзина
    </h1>

    <!-- Пустая корзина -->
    <v-card v-if="isEmpty && !loading" class="pa-8 text-center">
      <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-cart-off</v-icon>
      <h2 class="text-h5 text-grey-darken-1 mb-4">Ваша корзина пуста</h2>
      <p class="text-body-1 text-grey mb-6">Перейдите в каталог, чтобы добавить товары</p>
      <v-btn color="primary" size="large" to="/catalog" prepend-icon="mdi-view-grid">
        Перейти в каталог
      </v-btn>
    </v-card>

    <!-- Загрузка -->
    <v-skeleton-loader v-else-if="loading" type="article, article, article"></v-skeleton-loader>

    <!-- Содержимое корзины -->
    <v-row v-else>
      <!-- Список товаров -->
      <v-col cols="12" lg="8">
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center py-4 px-6">
            <span class="text-h6">Товары в корзине ({{ totalItems }})</span>
            <v-spacer></v-spacer>
            <v-btn
              variant="text"
              color="error"
              size="small"
              prepend-icon="mdi-delete-sweep"
              @click="confirmClear"
              :disabled="isEmpty"
            >
              Очистить
            </v-btn>
          </v-card-title>

          <v-divider></v-divider>

          <v-list class="pa-0">
            <template v-for="(item, index) in positions" :key="item.basket_position_id">
              <v-list-item class="py-4 px-6">
                <template v-slot:prepend>
                  <v-avatar size="80" rounded="lg" class="mr-4">
                    <v-img :src="item.product.product_image_url || '/placeholder-product.png'" cover>
                      <template v-slot:placeholder>
                        <v-icon size="40" color="grey-lighten-1">mdi-package-variant</v-icon>
                      </template>
                    </v-img>
                  </v-avatar>
                </template>

                <v-list-item-title class="text-subtitle-1 font-weight-bold mb-1">
                  {{ item.product.product_title }}
                </v-list-item-title>

                <v-list-item-subtitle class="text-caption text-grey mb-2">
                  {{ item.product.product_brand_title || 'Без бренда' }}
                </v-list-item-subtitle>

                <div class="d-flex align-center mt-2">
                  <!-- Контрол количества -->
                  <div class="d-flex align-center quantity-control mr-4">
                    <v-btn
                      icon="mdi-minus"
                      size="x-small"
                      variant="outlined"
                      density="comfortable"
                      @click="decreaseQuantity(item)"
                      :disabled="item.product_quantity <= 1"
                    ></v-btn>
                    
                    <v-text-field
                      v-model.number="item.product_quantity"
                      type="number"
                      min="1"
                      hide-details
                      density="compact"
                      variant="outlined"
                      class="quantity-input mx-2"
                      @change="updateItemQuantity(item, $event.target.value)"
                    ></v-text-field>
                    
                    <v-btn
                      icon="mdi-plus"
                      size="x-small"
                      variant="outlined"
                      density="comfortable"
                      @click="increaseQuantity(item)"
                    ></v-btn>
                  </div>

                  <!-- Цена -->
                  <div class="text-h6 font-weight-bold primary--text">
                    {{ formatPrice(item.total_price) }} ₽
                  </div>

                  <v-spacer></v-spacer>

                  <!-- Удалить -->
                  <v-btn
                    icon="mdi-delete"
                    variant="text"
                    color="error"
                    size="small"
                    @click="removeItem(item.basket_position_id)"
                  ></v-btn>
                </div>
              </v-list-item>

              <v-divider v-if="index < positions.length - 1"></v-divider>
            </template>
          </v-list>
        </v-card>
      </v-col>

      <!-- Итого и оформление -->
      <v-col cols="12" lg="4">
        <v-card class="sticky-summary">
          <v-card-title class="text-h6 py-4 px-6">Итого</v-card-title>
          
          <v-card-text class="px-6 pb-4">
            <div class="d-flex justify-space-between mb-2">
              <span class="text-body-1">Товаров:</span>
              <span class="text-body-1 font-weight-medium">{{ totalItems }} шт.</span>
            </div>
            
            <v-divider class="my-3"></v-divider>
            
            <div class="d-flex justify-space-between align-center">
              <span class="text-h6">К оплате:</span>
              <span class="text-h5 font-weight-bold primary--text">{{ formatPrice(totalPrice) }} ₽</span>
            </div>
          </v-card-text>

          <v-card-actions class="px-6 pb-6">
            <v-btn
              color="primary"
              size="large"
              block
              prepend-icon="mdi-cash-register"
              :disabled="isEmpty"
              @click="goToCheckout"
            >
              Оформить заказ
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Диалог подтверждения очистки -->
    <v-dialog v-model="clearDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">Очистить корзину?</v-card-title>
        <v-card-text>
          Все товары будут удалены из корзины. Это действие нельзя отменить.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="clearDialog = false">Отмена</v-btn>
          <v-btn color="error" @click="clearCart">Очистить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Снекбар уведомлений -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'
import { storeToRefs } from 'pinia'

const router = useRouter()
const cartStore = useCartStore()

const { positions, totalItems, totalPrice, isEmpty, loading } = storeToRefs(cartStore)

const clearDialog = ref(false)
const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
})

const showSnackbar = (text, color = 'success') => {
  snackbar.value = { show: true, text, color }
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}

const increaseQuantity = async (item) => {
  const result = await cartStore.updateQuantity(item.basket_position_id, item.product_quantity + 1)
  if (!result.success) {
    showSnackbar(result.error, 'error')
  }
}

const decreaseQuantity = async (item) => {
  if (item.product_quantity > 1) {
    const result = await cartStore.updateQuantity(item.basket_position_id, item.product_quantity - 1)
    if (!result.success) {
      showSnackbar(result.error, 'error')
    }
  }
}

const updateItemQuantity = async (item, newValue) => {
  const quantity = parseInt(newValue) || 1
  if (quantity < 1) {
    // Если меньше 1 - удаляем
    await removeItem(item.basket_position_id)
    return
  }
  
  const result = await cartStore.updateQuantity(item.basket_position_id, quantity)
  if (!result.success) {
    showSnackbar(result.error, 'error')
    // Восстанавливаем предыдущее значение
    cartStore.fetchBasket()
  }
}

const removeItem = async (positionId) => {
  const result = await cartStore.removeFromCart(positionId)
  if (result.success) {
    showSnackbar('Товар удален из корзины')
  } else {
    showSnackbar(result.error, 'error')
  }
}

const confirmClear = () => {
  clearDialog.value = true
}

const clearCart = async () => {
  const result = await cartStore.clearCart()
  clearDialog.value = false
  if (result.success) {
    showSnackbar('Корзина очищена')
  } else {
    showSnackbar(result.error, 'error')
  }
}

const goToCheckout = () => {
  router.push('/checkout')
}

onMounted(() => {
  cartStore.fetchBasket()
})
</script>

<style scoped>
.quantity-control {
  width: 140px;
}

.quantity-input :deep(input) {
  text-align: center;
  padding: 4px 0;
}

.sticky-summary {
  position: sticky;
  top: 80px;
}
</style>