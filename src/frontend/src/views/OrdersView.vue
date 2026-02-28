<template>
  <v-container class="py-6">
    <h1 class="text-h4 font-weight-bold mb-6 primary--text">
      <v-icon size="36" class="mr-2" color="primary">mdi-clipboard-list</v-icon>
      Мои заказы
    </h1>

    <!-- Загрузка -->
    <v-skeleton-loader v-if="loading" type="article, article, article"></v-skeleton-loader>

    <!-- Пусто -->
    <v-card v-else-if="orders.length === 0" class="pa-8 text-center">
      <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-clipboard-text-outline</v-icon>
      <h2 class="text-h5 text-grey-darken-1 mb-4">У вас пока нет заказов</h2>
      <p class="text-body-1 text-grey mb-6">Сделайте свой первый заказ в каталоге</p>
      <v-btn color="primary" size="large" to="/catalog" prepend-icon="mdi-view-grid">
        Перейти в каталог
      </v-btn>
    </v-card>

    <!-- Список заказов -->
    <template v-else>
      <v-row>
        <v-col v-for="order in orders" :key="order.order_id" cols="12">
          <v-card :class="{ 'order-cancelled': order.order_status === 'Отменён' }">
            <v-card-title class="d-flex align-center py-4 px-6">
              <div>
                <span class="text-h6">Заказ #{{ order.order_id }}</span>
                <div class="text-caption text-grey">{{ formatDate(order.date_of_create) }}</div>
              </div>
              
              <v-spacer></v-spacer>
              
              <!-- Статус -->
              <v-chip
                :color="order.status_display.color"
                class="font-weight-bold"
                size="small"
              >
                {{ order.order_status }}
              </v-chip>
            </v-card-title>

            <v-divider></v-divider>

            <v-card-text class="px-6 py-4">
              <!-- Позиции (показываем первые 2) -->
              <div class="mb-4">
                <div
                  v-for="position in order.positions.slice(0, 2)"
                  :key="position.order_position_id"
                  class="d-flex align-center mb-2"
                >
                  <v-avatar size="40" rounded class="mr-3">
                    <v-img :src="position.product?.product_image_url || '/placeholder-product.png'">
                      <template v-slot:placeholder>
                        <v-icon size="20" color="grey-lighten-1">mdi-package-variant</v-icon>
                      </template>
                    </v-img>
                  </v-avatar>
                  
                  <div class="flex-grow-1">
                    <div class="text-body-2 font-weight-medium line-clamp-1">
                      {{ position.product?.product_title || 'Товар удалён' }}
                    </div>
                    <div class="text-caption text-grey">
                      {{ position.product_quantity }} шт. × {{ formatPrice(position.product_price_in_moment) }} ₽
                    </div>
                  </div>
                </div>
                
                <div v-if="order.positions.length > 2" class="text-caption text-grey ml-13">
                  и ещё {{ order.positions.length - 2 }} товаров...
                </div>
              </div>

              <!-- Инфо -->
              <v-row class="text-body-2">
                <v-col cols="12" sm="6">
                  <div class="d-flex align-center mb-2">
                    <v-icon size="small" class="mr-2" color="grey">mdi-map-marker</v-icon>
                    <span class="line-clamp-2">{{ order.delivery_address }}</span>
                  </div>
                  <div class="d-flex align-center">
                    <v-icon size="small" class="mr-2" color="grey">mdi-credit-card</v-icon>
                    <span>{{ order.payment_method }}</span>
                  </div>
                </v-col>
                
                <v-col cols="12" sm="6" class="text-sm-right">
                  <div class="text-caption text-grey mb-1">Сумма заказа</div>
                  <div class="text-h6 font-weight-bold primary--text">{{ formatPrice(order.price) }} ₽</div>
                </v-col>
              </v-row>
            </v-card-text>

            <v-divider v-if="order.can_cancel"></v-divider>

            <v-card-actions v-if="order.can_cancel" class="px-6 py-4">
              <v-spacer></v-spacer>
              <v-btn
                color="error"
                variant="outlined"
                prepend-icon="mdi-close-circle"
                @click="confirmCancel(order)"
              >
                Отменить заказ
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <!-- Пагинация -->
      <v-pagination
        v-if="pagination.num_pages > 1"
        v-model="currentPage"
        :length="pagination.num_pages"
        :total-visible="7"
        class="mt-6"
        @update:model-value="changePage"
      ></v-pagination>
    </template>

    <!-- Диалог подтверждения отмены -->
    <v-dialog v-model="cancelDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">Отменить заказ?</v-card-title>
        <v-card-text>
          Заказ #{{ orderToCancel?.order_id }} будет отменён, а товары вернутся в продажу.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="cancelDialog = false">Нет, оставить</v-btn>
          <v-btn color="error" :loading="cancelling" @click="executeCancel">
            Да, отменить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Снекбар -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useOrdersStore } from '@/store/order'
import { storeToRefs } from 'pinia'

const ordersStore = useOrdersStore()
const { orders, loading, pagination } = storeToRefs(ordersStore)

const currentPage = ref(1)
const cancelDialog = ref(false)
const orderToCancel = ref(null)
const cancelling = ref(false)

const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
})

const showSnackbar = (text, color = 'success') => {
  snackbar.value = { show: true, text, color }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}

const changePage = (page) => {
  ordersStore.fetchOrders(page)
}

const confirmCancel = (order) => {
  orderToCancel.value = order
  cancelDialog.value = true
}

const executeCancel = async () => {
  if (!orderToCancel.value) return
  
  cancelling.value = true
  
  const result = await ordersStore.cancelOrder(orderToCancel.value.order_id)
  
  cancelDialog.value = false
  cancelling.value = false
  
  if (result.success) {
    showSnackbar('Заказ успешно отменён')
  } else {
    showSnackbar(result.error, 'error')
  }
}

onMounted(() => {
  ordersStore.fetchOrders()
})
</script>

<style scoped>
.order-cancelled {
  opacity: 0.7;
  background-color: #f5f5f5;
}

.line-clamp-1 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
</style>