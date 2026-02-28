<template>
  <v-container class="py-6" max-width="800">
    <h1 class="text-h4 font-weight-bold mb-6 primary--text">
      <v-icon size="36" class="mr-2" color="primary">mdi-cash-register</v-icon>
      Оформление заказа
    </h1>

    <!-- Проверка корзины -->
    <v-alert
      v-if="isEmpty"
      type="warning"
      class="mb-6"
      prominent
      border="start"
    >
      <v-alert-title>Корзина пуста</v-alert-title>
      Добавьте товары в корзину перед оформлением заказа
      <template v-slot:append>
        <v-btn color="warning" variant="outlined" to="/catalog">
          В каталог
        </v-btn>
      </template>
    </v-alert>

    <template v-else>
      <!-- Форма оформления -->
      <v-card class="mb-6">
        <v-card-title class="text-h6 py-4 px-6">Данные заказа</v-card-title>
        
        <v-card-text class="px-6">
          <v-form ref="form" v-model="formValid" @submit.prevent="submitOrder">
            <!-- Адрес доставки -->
            <v-textarea
              v-model="formData.delivery_address"
              label="Адрес доставки *"
              placeholder="Город, улица, дом, квартира"
              variant="outlined"
              rows="3"
              :rules="[v => !!v || 'Адрес обязателен']"
              class="mb-4"
            ></v-textarea>

            <!-- Способ оплаты -->
            <v-select
              v-model="formData.payment_method"
              label="Способ оплаты *"
              :items="paymentMethods"
              item-title="title"
              item-value="value"
              variant="outlined"
              :rules="[v => !!v || 'Выберите способ оплаты']"
              class="mb-4"
            ></v-select>

            <!-- Комментарий -->
            <v-textarea
              v-model="formData.user_comment"
              label="Комментарий к заказу"
              placeholder="Дополнительная информация для курьера"
              variant="outlined"
              rows="2"
              hint="Необязательно"
              persistent-hint
            ></v-textarea>
          </v-form>
        </v-card-text>
      </v-card>

      <!-- Состав заказа -->
      <v-card class="mb-6">
        <v-card-title class="text-h6 py-4 px-6 d-flex align-center">
          Состав заказа
          <v-spacer></v-spacer>
          <v-btn variant="text" size="small" to="/cart">
            Изменить
          </v-btn>
        </v-card-title>

        <v-list class="pa-0">
          <template v-for="(item, index) in positions" :key="item.basket_position_id">
            <v-list-item class="py-3 px-6">
              <template v-slot:prepend>
                <v-avatar size="60" rounded="lg" class="mr-4">
                  <v-img :src="item.product.product_image_url || '/placeholder-product.png'" cover>
                    <template v-slot:placeholder>
                      <v-icon size="32" color="grey-lighten-1">mdi-package-variant</v-icon>
                    </template>
                  </v-img>
                </v-avatar>
              </template>

              <v-list-item-title class="font-weight-medium">
                {{ item.product.product_title }}
              </v-list-item-title>

              <v-list-item-subtitle>
                {{ item.product_quantity }} шт. × {{ formatPrice(item.product.product_price) }} ₽
              </v-list-item-subtitle>

              <template v-slot:append>
                <span class="text-h6 font-weight-bold primary--text">
                  {{ formatPrice(item.total_price) }} ₽
                </span>
              </template>
            </v-list-item>

            <v-divider v-if="index < positions.length - 1"></v-divider>
          </template>
        </v-list>

        <v-divider></v-divider>

        <v-card-text class="px-6 py-4">
          <div class="d-flex justify-space-between align-center">
            <span class="text-h6">Итого к оплате:</span>
            <span class="text-h4 font-weight-bold primary--text">{{ formatPrice(totalPrice) }} ₽</span>
          </div>
        </v-card-text>
      </v-card>

      <!-- Кнопки действий -->
      <div class="d-flex gap-4">
        <v-btn
          variant="outlined"
          size="large"
          to="/cart"
          prepend-icon="mdi-arrow-left"
        >
          Вернуться в корзину
        </v-btn>

        <v-spacer></v-spacer>

        <v-btn
          color="primary"
          size="large"
          prepend-icon="mdi-check-circle"
          :loading="submitting"
          :disabled="!formValid || isEmpty"
          @click="submitOrder"
        >
          Подтвердить заказ
        </v-btn>
      </div>
    </template>

    <!-- Диалог успешного оформления -->
    <v-dialog v-model="successDialog" persistent max-width="500">
      <v-card>
        <v-card-title class="text-h5 text-center pt-6">
          <v-icon size="64" color="success" class="mb-4">mdi-check-circle</v-icon>
          <div>Заказ успешно оформлен!</div>
        </v-card-title>
        
        <v-card-text class="text-center pb-4">
          <p class="text-body-1 mb-2">Номер вашего заказа: <strong class="text-primary">#{{ createdOrderId }}</strong></p>
          <p class="text-body-2 text-grey">Вы можете отслеживать статус заказа в разделе "Мои заказы"</p>
        </v-card-text>
        
        <v-card-actions class="pa-6 pt-0">
          <v-btn color="primary" block size="large" to="/orders">
            Перейти к моим заказам
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Снекбар ошибок -->
    <v-snackbar v-model="errorSnackbar.show" color="error" timeout="5000">
      {{ errorSnackbar.text }}
      <template v-slot:actions>
        <v-btn variant="text" @click="errorSnackbar.show = false">Закрыть</v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'
import { useOrdersStore } from '@/store/order'
import { storeToRefs } from 'pinia'

const router = useRouter()
const cartStore = useCartStore()
const ordersStore = useOrdersStore()

const { positions, totalPrice, isEmpty } = storeToRefs(cartStore)

const form = ref(null)
const formValid = ref(false)
const submitting = ref(false)
const successDialog = ref(false)
const createdOrderId = ref(null)

const formData = ref({
  delivery_address: '',
  payment_method: 'Онлайн',
  user_comment: ''
})

const paymentMethods = [
  { title: 'Онлайн оплата', value: 'Онлайн' },
  { title: 'Наличными при получении', value: 'Наличными' }
]

const errorSnackbar = ref({
  show: false,
  text: ''
})

const showError = (text) => {
  errorSnackbar.value = { show: true, text }
}

const formatPrice = (price) => {
    console.log(price)
  return new Intl.NumberFormat('ru-RU').format(price)
}

const submitOrder = async () => {
  const { valid } = await form.value.validate()
  if (!valid) return

  submitting.value = true

  const result = await ordersStore.createOrder(formData.value)

  if (result.success) {
    createdOrderId.value = result.order.order_id
    successDialog.value = true
  } else {
    showError(result.error)
  }

  submitting.value = false
}

onMounted(() => {
  cartStore.fetchBasket()
  console.log(positions)
})
</script>

<style scoped>
.gap-4 {
  gap: 16px;
}
</style>