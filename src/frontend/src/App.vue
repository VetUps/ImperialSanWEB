<template>
  <v-app>
    <AppHeader
      @toggle-drawer="drawer = !drawer"
      v-if="showHeader"
    />

    <v-main>
      <v-container fluid class="pa-0">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </v-container>
    </v-main>

    <!-- Уведомления -->
    <v-snackbar
      v-model="showNotification"
      :color="notificationColor"
      :timeout="3000"
    >
      {{ notificationMessage }}
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'

const route = useRoute()

const drawer = ref(false)

const showHeader = computed(() => {
  return !['login', 'register'].includes(route.name)
})

const showNotification = ref(false)
const notificationMessage = ref('')
const notificationColor = ref('success')
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

html {
  scroll-behavior: smooth;
}

/* Стили для скроллбара */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #2196F3;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #1976D2;
}
</style>