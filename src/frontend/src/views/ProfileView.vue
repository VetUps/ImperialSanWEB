<template>
  <v-container class="pa-4">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h3 font-weight-bold text-primary mb-6">
          <v-icon class="mr-2" size="large">mdi-account</v-icon>
          Мой профиль
        </h1>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-text class="text-center pa-6">
            <v-avatar size="120" color="primary" class="mb-4">
              <span class="text-h3 text-white font-weight-bold">{{ initials }}</span>
            </v-avatar>
            
            <h2 class="text-h5 font-weight-bold mb-2">{{ fullName }}</h2>
            
            <v-chip :color="getRoleColor" class="mb-4">
              <v-icon left>{{ getRoleIcon }}</v-icon>
              {{ getUserRoleText }}
            </v-chip>
            
            <div class="text-body-1 mb-2">
              <v-icon left>mdi-email</v-icon>
              {{ user.user_mail }}
            </div>
            
            <div class="text-body-1 mb-2">
              <v-icon left>mdi-phone</v-icon>
              {{ formatPhone(user.user_phone) }}
            </div>
            
            <div class="text-body-1 mb-4">
              <v-icon left>mdi-calendar</v-icon>
              Зарегистрирован: {{ formatDate(user.date_joined) }}
            </div>
            
            <v-divider class="my-4"></v-divider>
            
            <v-btn
              color="primary"
              variant="tonal"
              block
              @click="showEditDialog = true"
            >
              <v-icon left>mdi-pencil</v-icon>
              Редактировать профиль
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="8">
        <!-- Статистика пользователя -->
        <v-row class="mb-6">
          <v-col cols="12" sm="6" md="3">
            <v-card>
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold text-primary">12</div>
                <div class="text-subtitle-1">Заказов</div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <v-card>
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold text-primary">₽45,600</div>
                <div class="text-subtitle-1">Потрачено</div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <v-card>
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold text-primary">3</div>
                <div class="text-subtitle-1">В корзине</div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <v-card>
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold text-primary">8</div>
                <div class="text-subtitle-1">Избранное</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        
        <!-- Последние заказы -->
        <v-card class="mb-6">
          <v-card-title>
            <v-icon left>mdi-history</v-icon>
            Последние заказы
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="order in userOrders"
                :key="order.id"
              >
                <template v-slot:prepend>
                  <v-avatar :color="getStatusColor(order.status)" size="40">
                    <v-icon color="white">mdi-package</v-icon>
                  </v-avatar>
                </template>
                
                <v-list-item-title>Заказ #{{ order.id }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ order.date }} • {{ order.items }} товаров
                </v-list-item-subtitle>
                
                <template v-slot:append>
                  <div class="text-right">
                    <div class="text-h6 font-weight-bold">{{ order.total }} ₽</div>
                    <v-chip :color="getStatusColor(order.status)" size="small">
                      {{ order.status }}
                    </v-chip>
                  </div>
                </template>
              </v-list-item>
            </v-list>
            
            <div class="text-center mt-4">
              <v-btn
                color="primary"
                variant="text"
                to="/orders"
              >
                Все заказы
                <v-icon right>mdi-chevron-right</v-icon>
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Диалог редактирования -->
    <v-dialog v-model="showEditDialog" max-width="600">
      <v-card>
        <v-card-title>Редактирование профиля</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="updateProfile">
            <v-text-field
              v-model="editForm.user_surname"
              label="Фамилия"
              variant="outlined"
              class="mb-3"
            ></v-text-field>
            
            <v-text-field
              v-model="editForm.user_name"
              label="Имя"
              variant="outlined"
              class="mb-3"
            ></v-text-field>
            
            <v-text-field
              v-model="editForm.user_patronymic"
              label="Отчество"
              variant="outlined"
              class="mb-3"
            ></v-text-field>
            
            <v-text-field
              v-model="editForm.user_phone"
              label="Телефон"
              variant="outlined"
              class="mb-3"
            ></v-text-field>
            
            <v-textarea
              v-model="editForm.user_dilivery_address"
              label="Адрес доставки"
              variant="outlined"
              rows="3"
              class="mb-3"
            ></v-textarea>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showEditDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="updateProfile">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { user, fullName, initials, userRole } = storeToRefs(authStore)

const showEditDialog = ref(false)
const editForm = reactive({
  user_surname: '',
  user_name: '',
  user_patronymic: '',
  user_phone: '',
  user_dilivery_address: ''
})

const userOrders = ref([
  { id: 1001, date: '15.01.2024', items: 3, total: 12500, status: 'В обработке' },
  { id: 998, date: '10.01.2024', items: 5, total: 23400, status: 'Доставлен' },
  { id: 995, date: '05.01.2024', items: 2, total: 7800, status: 'Доставлен' }
])

const getRoleIcon = computed(() => {
  switch (userRole.value) {
    case 'Admin': return 'mdi-shield-crown'
    case 'Manager': return 'mdi-shield-account'
    default: return 'mdi-account'
  }
})

const getRoleColor = computed(() => {
  switch (userRole.value) {
    case 'Admin': return 'amber'
    case 'Manager': return 'green'
    default: return 'blue'
  }
})

const getUserRoleText = computed(() => {
  switch (userRole.value) {
    case 'Admin': return 'Администратор'
    case 'Manager': return 'Менеджер'
    default: return 'Пользователь'
  }
})

const formatPhone = (phone) => {
  if (!phone) return ''
  return phone.replace(/(\d{1})(\d{3})(\d{3})(\d{2})(\d{2})/, '+$1 ($2) $3-$4-$5')
}

const formatDate = (dateString) => {
  if (!dateString) return ''
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

const updateProfile = async () => {
  const result = await authStore.updateProfile(editForm)
  if (result.success) {
    showEditDialog.value = false
  }
}

// Инициализация формы при открытии
watch(showEditDialog, (newVal) => {
  if (newVal && user.value) {
    editForm.user_surname = user.value.user_surname || ''
    editForm.user_name = user.value.user_name || ''
    editForm.user_patronymic = user.value.user_patronymic || ''
    editForm.user_phone = user.value.user_phone || ''
    editForm.user_dilivery_address = user.value.user_dilivery_address || ''
  }
})
</script>