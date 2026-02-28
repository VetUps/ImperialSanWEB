<template>
  <div>
    <!-- Быстрые действия -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card>
          <v-card-title>Быстрые действия</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6" md="3">
                <v-btn
                  color="primary"
                  variant="tonal"
                  block
                  size="large"
                  prepend-icon="mdi-plus"
                  to="/dashboard/products"
                >
                  Управление товарами
                </v-btn>
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <v-btn
                  color="primary"
                  variant="tonal"
                  block
                  size="large"
                  prepend-icon="mdi-clipboard-list"
                  to="/dashboard/orders"
                >
                  Управление заказами
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Последние заказы -->
    <v-row>
      <v-col cols="12">
        <v-card :loading="loading">
          <v-card-title class="d-flex align-center">
            <v-icon left class="mr-2">mdi-history</v-icon>
            Последние заказы
            <v-spacer></v-spacer>
            <v-btn
              icon="mdi-refresh"
              variant="text"
              size="small"
              @click="refreshOrders"
              :loading="loading"
            ></v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-alert
              v-if="error"
              type="error"
              variant="tonal"
              class="mb-4"
            >
              {{ error }}
            </v-alert>

            <v-table v-if="recentOrders.length > 0" hover>
              <thead>
                <tr>
                  <th class="font-weight-bold">ID</th>
                  <th class="font-weight-bold">Дата</th>
                  <th class="font-weight-bold">Пользователь</th>
                  <th class="font-weight-bold">Статус</th>
                  <th class="font-weight-bold text-right">Сумма</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="order in recentOrders"
                  :key="order.order_id"
                  @click="openOrderDetail(order.order_id)"
                  style="cursor: pointer;"
                >
                  <td class="font-weight-medium">#{{ order.order_id }}</td>
                  <td>{{ formatDate(order.date_of_create) }}</td>
                  <td>
                    <div class="d-flex align-center">
                      <v-icon size="small" class="mr-2" color="grey">mdi-account</v-icon>
                      <div>
                        <div class="font-weight-medium">{{ order.user_info?.full_name || 'Неизвестный' }}</div>
                        <div class="text-caption text-grey">{{ order.user_info?.email }}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <v-chip
                      :color="order.status_display.color"
                      size="small"
                      class="font-weight-medium"
                    >
                      {{ order.order_status }}
                    </v-chip>
                  </td>
                  <td class="text-right font-weight-bold text-primary">
                    {{ formatPrice(order.price) }} ₽
                  </td>
                </tr>
              </tbody>
            </v-table>

            <v-alert
              v-else-if="!loading"
              type="info"
              variant="tonal"
              class="text-center"
            >
              Нет заказов для отображения
            </v-alert>

            <div class="text-center mt-4">

            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Диалог деталей заказа -->
    <v-dialog v-model="detailDialog" max-width="700">
      <v-card v-if="selectedOrder">
        <v-card-title class="d-flex align-center py-4">
          <span>Заказ #{{ selectedOrder.order_id }}</span>
          <v-spacer></v-spacer>
          <v-chip
            :color="selectedOrder.status_display.color"
            class="font-weight-bold"
          >
            {{ selectedOrder.order_status }}
          </v-chip>
        </v-card-title>

        <v-divider></v-divider>

        <v-card-text class="py-4">
          <!-- Инфо о пользователе -->
          <v-row class="mb-4">
            <v-col cols="12" sm="6">
              <div class="text-caption text-grey mb-1">Покупатель</div>
              <div class="font-weight-medium">{{ selectedOrder.user_info?.full_name }}</div>
              <div class="text-body-2">{{ selectedOrder.user_info?.email }}</div>
              <div class="text-body-2">{{ selectedOrder.user_info?.phone }}</div>
            </v-col>
            <v-col cols="12" sm="6">
              <div class="text-caption text-grey mb-1">Дата оформления</div>
              <div class="font-weight-medium">{{ formatDateTime(selectedOrder.date_of_create) }}</div>
              <div class="text-caption text-grey mt-2 mb-1">Способ оплаты</div>
              <div>{{ selectedOrder.payment_method }}</div>
            </v-col>
          </v-row>

          <!-- Адрес -->
          <div class="mb-4">
            <div class="text-caption text-grey mb-1">Адрес доставки</div>
            <div class="font-weight-medium">{{ selectedOrder.delivery_address }}</div>
          </div>

          <!-- Комментарий -->
          <div v-if="selectedOrder.user_comment" class="mb-4">
            <div class="text-caption text-grey mb-1">Комментарий</div>
            <div class="text-body-2">{{ selectedOrder.user_comment }}</div>
          </div>

          <v-divider class="my-4"></v-divider>

          <!-- Позиции -->
          <div class="text-subtitle-1 font-weight-bold mb-3">Состав заказа</div>
          <v-list class="pa-0">
            <v-list-item
              v-for="position in selectedOrder.positions"
              :key="position.order_position_id"
              class="px-0"
            >
              <template v-slot:prepend>
                <v-avatar size="50" rounded class="mr-3">
                  <v-img :src="position.product?.product_image_url || '/placeholder-product.png'">
                    <template v-slot:placeholder>
                      <v-icon color="grey-lighten-1">mdi-package-variant</v-icon>
                    </template>
                  </v-img>
                </v-avatar>
              </template>

              <v-list-item-title class="font-weight-medium">
                {{ position.product?.product_title || 'Товар удалён' }}
              </v-list-item-title>

              <v-list-item-subtitle>
                {{ position.product_quantity }} шт. × {{ formatPrice(position.product_price_in_moment) }} ₽
              </v-list-item-subtitle>

              <template v-slot:append>
                <span class="font-weight-bold text-primary">
                  {{ formatPrice(position.product_quantity * position.product_price_in_moment) }} ₽
                </span>
              </template>
            </v-list-item>
          </v-list>

          <v-divider class="my-4"></v-divider>

          <div class="d-flex justify-space-between align-center">
            <span class="text-h6">Итого:</span>
            <span class="text-h5 font-weight-bold text-primary">{{ formatPrice(selectedOrder.price) }} ₽</span>
          </div>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions class="pa-4">
          <v-select
            v-model="newStatus"
            :items="availableStatuses"
            item-title="title"
            item-value="value"
            label="Изменить статус"
            variant="outlined"
            density="comfortable"
            class="mr-4"
            style="max-width: 200px;"
            hide-details
          ></v-select>
          
          <v-btn
            color="primary"
            :disabled="newStatus === selectedOrder.order_status || !newStatus"
            :loading="updatingStatus"
            @click="updateStatus"
          >
            Обновить
          </v-btn>

          <v-spacer></v-spacer>

          <v-btn variant="text" @click="detailDialog = false">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminOrdersStore } from '@/store/adminOrders'
import { storeToRefs } from 'pinia'

const adminStore = useAdminOrdersStore()
const { recentOrders, loading, error, statistics: stats } = storeToRefs(adminStore)

const detailDialog = ref(false)
const selectedOrder = ref(null)
const newStatus = ref('')
const updatingStatus = ref(false)

const availableStatuses = [
  { title: 'В обработке', value: 'В обработке' },
  { title: 'Собирается', value: 'Собирается' },
  { title: 'Собран', value: 'Собран' },
  { title: 'В пути', value: 'В пути' },
  { title: 'Доставлен', value: 'Доставлен' },
  { title: 'Отменён', value: 'Отменён' }
]

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const refreshOrders = async () => {
  await adminStore.fetchAllOrders({ per_page: 5 })
  await adminStore.fetchStatistics()
}

const openOrderDetail = async (orderId) => {
  const result = await adminStore.fetchOrderDetail(orderId)
  if (result.success) {
    selectedOrder.value = result.order
    newStatus.value = result.order.order_status
    detailDialog.value = true
  }
}

const updateStatus = async () => {
  if (!selectedOrder.value || !newStatus.value) return
  
  updatingStatus.value = true
  
  const result = await adminStore.updateOrderStatus(
    selectedOrder.value.order_id,
    newStatus.value
  )
  
  updatingStatus.value = false
  
  if (result.success) {
    selectedOrder.value = result.order
    // Обновляем список
    await adminStore.fetchAllOrders({ per_page: 5 })
  }
}

onMounted(() => {
  refreshOrders()
})
</script>

<style scoped>
tr:hover {
  background-color: rgba(33, 150, 243, 0.05);
}
</style>