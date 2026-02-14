<template>
  <slot v-if="hasAccess"></slot>
  <v-alert
    v-else
    type="info"
    variant="tonal"
    class="my-4"
  >
    <div class="d-flex align-center">
      <v-icon class="mr-2">mdi-lock</v-icon>
      <div>
        <div class="font-weight-bold mb-1">Доступ ограничен</div>
        <div class="text-caption">
          Для доступа к фильтрации и сортировке требуется роль менеджера или администратора.
        </div>
      </div>
    </div>
  </v-alert>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { isManager, isAdmin } = storeToRefs(authStore)

const props = defineProps({
  // Можно расширить для разных типов доступа
  type: {
    type: String,
    default: 'filters' // 'filters', 'admin', 'manager', etc.
  }
})

const hasAccess = computed(() => {
  switch (props.type) {
    case 'filters':
      return isManager.value || isAdmin.value
    case 'admin':
      return isAdmin.value
    case 'manager':
      return isManager.value || isAdmin.value
    default:
      return true
  }
})
</script>