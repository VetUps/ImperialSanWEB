<!-- views/dashboard/DashboardProductEdit.vue -->
<template>
  <v-container fluid class="pa-4">
    <v-row>
      <v-col>
        <router-link to="/dashboard/products" class="text-decoration-none text-primary">
          <v-icon>mdi-arrow-left</v-icon> Назад к товарам
        </router-link>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="8" offset-md="2">
        <ProductForm
          :product-id="productId"
          @saved="onSaved"
          @cancel="onCancel"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ProductForm from '@/components/dashboard/ProductForm.vue'

const route = useRoute()
const router = useRouter()

const productId = computed(() => {
  const id = route.params.id
  return id ? parseInt(id) : null
})

const onSaved = (product) => {
  // Перенаправляем на список товаров с уведомлением об успехе
  router.push('/dashboard/products')
  // TODO: показать snackbar
}

const onCancel = () => {
  router.push('/dashboard/products')
}
</script>