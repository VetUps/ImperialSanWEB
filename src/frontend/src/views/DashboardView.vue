<template>
  <v-container fluid class="pa-4">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h3 font-weight-bold text-primary mb-6">
          <v-icon class="mr-2" size="large">mdi-view-dashboard</v-icon>
          Панель управления
        </h1>
      </v-col>
    </v-row>

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
                  to="/dashboard/products/create"
                >
                  Добавить товар
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
        <v-card>
          <v-card-title>
            <v-icon left>mdi-history</v-icon>
            Последние заказы
          </v-card-title>
          <v-card-text>
            <v-table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Дата</th>
                  <th>Пользователь</th>
                  <th>Статус</th>
                  <th>Сумма</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in recentOrders" :key="order.order_id">
                  <td>{{ order.order_id }}</td>
                  <td>{{ formatDate(order.order_date_create) }}</td>
                  <td>{{ order.user_name }} {{ order.user_surname }}</td>
                  <td>
                    <v-chip :color="getStatusColor(order.order_status)" size="small">
                      {{ order.order_status }}
                    </v-chip>
                  </td>
                  <td>{{ formatPrice(order.order_price) }} ₽</td>
                </tr>
              </tbody>
            </v-table>

            <div class="text-center mt-4">
              <v-btn
                color="primary"
                variant="text"
                to="/dashboard/orders"
              >
                Все заказы
                <v-icon right>mdi-chevron-right</v-icon>
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { isAdmin } = storeToRefs(authStore)

const stats = ref({
  totalProducts: 0,
  totalOrders: 0,
  totalUsers: 0,
  revenue: 0
})

const recentOrders = ref([])
const orderStatusStats = ref([])

onMounted(async () => {
  // Загрузка статистики (заглушка)
  stats.value = {
    totalProducts: 156,
    totalOrders: 24,
    totalUsers: 89,
    revenue: 456780
  }

  recentOrders.value = [
    {
      order_id: 1001,
      order_date_create: '2024-01-15T10:30:00',
      user_name: 'Иван',
      user_surname: 'Иванов',
      order_status: 'В обработке',
      order_price: 12500
    },
    {
      order_id: 1002,
      order_date_create: '2024-01-14T14:45:00',
      user_name: 'Петр',
      user_surname: 'Петров',
      order_status: 'Собирается',
      order_price: 7800
    },
    {
      order_id: 1003,
      order_date_create: '2024-01-13T09:15:00',
      user_name: 'Сергей',
      user_surname: 'Сергеев',
      order_status: 'Доставлен',
      order_price: 23400
    }
  ]

  orderStatusStats.value = [
    { name: 'В обработке', count: 5, percentage: 21, color: 'blue' },
    { name: 'Собирается', count: 3, percentage: 13, color: 'orange' },
    { name: 'Собран', count: 8, percentage: 33, color: 'green' },
    { name: 'Доставлен', count: 6, percentage: 25, color: 'success' },
    { name: 'Отменён', count: 2, percentage: 8, color: 'red' }
  ]
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU')
}

const getStatusColor = (status) => {
  const colors = {
    'В обработке': 'blue',
    'Собирается': 'orange',
    'Собран': 'green',
    'В пути': 'purple',
    'Доставлен': 'success',
    'Отменён': 'red'
  }
  return colors[status] || 'grey'
}
</script>