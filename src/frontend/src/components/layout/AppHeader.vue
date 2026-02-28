<template>
  <v-app-bar color="primary" dark app elevation="3">
    <v-toolbar-title class="d-flex align-center">
      <v-icon class="mr-2" size="large">mdi-water-pump</v-icon>
      <span class="font-weight-bold text-h6">Imperial San</span>
    </v-toolbar-title>

    <v-spacer></v-spacer>

    <div class="d-flex align-center">
      <v-btn
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        text
        class="text-white mr-2"
        :prepend-icon="item.icon"
      >
        {{ item.title }}
      </v-btn>
    </div>

    <v-divider vertical class="mx-4"></v-divider>

    <!-- Кнопка корзины (только для авторизованных) -->
    <v-btn
      v-if="isAuthenticated"
      to="/cart"
      icon
      class="text-white mr-2"
    >
      <v-badge
        :content="cartItemCount"
        :model-value="cartItemCount > 0"
        color="error"
        location="bottom right"
        offset-x="5"
        offset-y="5"
      >
        <v-icon>mdi-cart</v-icon>
      </v-badge>
      
      <v-tooltip activator="parent" location="bottom">
        Корзина ({{ cartItemCount }} товаров)
      </v-tooltip>
    </v-btn>

    <!-- Информация пользователя -->
    <div v-if="isAuthenticated" class="d-flex align-center">
      <v-chip
        color="white"
        class="mr-4 text-white font-weight-medium"
        :prepend-icon="getRoleIcon"
      >
        <template v-slot:prepend>
          <v-icon :color="getRoleColor">{{ getRoleIcon }}</v-icon>
        </template>
        <span class="font-weight-bold text-h6">{{ fullName }}</span>
        <v-tooltip activator="parent" location="bottom">
          {{ getUserRoleText }}
        </v-tooltip>
      </v-chip>

      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
            class="text-white"
          >
            <v-avatar size="40" color="white">
              <span class="text-primary font-weight-bold">{{ initials }}</span>
            </v-avatar>
          </v-btn>
        </template>

        <v-list density="compact">
          <v-list-item
            v-for="item in userMenu"
            :key="item.title"
            :to="item.to"
            @click="item.action"
          >
            <template v-slot:prepend>
              <v-icon>{{ item.icon }}</v-icon>
            </template>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>

    <!-- Кнопки входа/регистрации -->
    <div v-else class="d-flex align-center">
      <v-btn
        to="/login"
        variant="outlined"
        color="white"
        class="mr-2"
        prepend-icon="mdi-login"
      >
        Войти
      </v-btn>
      <v-btn
        to="/register"
        color="white"
        prepend-icon="mdi-account-plus"
      >
        Регистрация
      </v-btn>
    </div>
  </v-app-bar>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useCartStore } from '@/store/cart'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const cartStore = useCartStore()

const { isAuthenticated, fullName, userRole, initials } = storeToRefs(authStore)
const { itemCount: cartItemCount } = storeToRefs(cartStore)

const navItems = computed(() => {
  const items = [
    { to: '/catalog', title: 'Каталог', icon: 'mdi-view-grid' }
  ]

  if (userRole.value === 'Manager' || userRole.value === 'Admin') {
    items.push({
      to: '/dashboard',
      title: 'Панель управления',
      icon: 'mdi-view-dashboard'
    })
  }

  return items
})

const userMenu = computed(() => {
  const menu = [
    {
      title: 'Мой профиль',
      icon: 'mdi-account',
      to: '/profile'
    },
    {
      title: 'Мои заказы',
      icon: 'mdi-clipboard-list',
      to: '/orders'
    }
  ]

  if (userRole.value === 'Admin') {
    menu.push({
      title: 'Администрирование',
      icon: 'mdi-cog',
      to: '/admin'
    })
  }

  menu.push(
    {
      title: 'Выйти',
      icon: 'mdi-logout',
      action: () => authStore.logout()
    }
  )

  return menu
})

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

// Загружаем корзину при монтировании, если пользователь авторизован
onMounted(() => {
  if (isAuthenticated.value) {
    cartStore.fetchBasket()
  }
})
</script>