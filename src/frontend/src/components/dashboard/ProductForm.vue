<template>
  <v-card>
    <v-card-title class="bg-primary text-white">
      {{ isEdit ? 'Редактирование товара' : 'Создание нового товара' }}
    </v-card-title>

    <v-card-text>
      <v-form ref="formRef" v-model="valid" lazy-validation @submit.prevent="submitForm">
        <v-row>
          <v-col cols="12" class="mt-4">
            <v-text-field
              v-model="form.product_title"
              label="Название товара *"
              :rules="[rules.required, rules.minLength(3)]"
              variant="outlined"
              required
            ></v-text-field>
          </v-col>

          <v-col cols="12">
            <v-textarea
              v-model="form.product_description"
              label="Описание товара"
              variant="outlined"
              rows="3"
            ></v-textarea>
          </v-col>

          <v-col cols="12" sm="6">
            <v-text-field
              v-model.number="form.product_price"
              label="Цена (₽) *"
              type="number"
              :rules="[rules.required, rules.positiveNumber]"
              variant="outlined"
              prefix="₽"
              required
            ></v-text-field>
          </v-col>

          <v-col cols="12" sm="6">
            <v-text-field
              v-model.number="form.product_quantity_in_stock"
              label="Количество на складе *"
              type="number"
              :rules="[rules.required, rules.nonNegativeNumber]"
              variant="outlined"
              required
            ></v-text-field>
          </v-col>

          <v-col cols="12">
            <v-text-field
              v-model="form.product_image_url"
              label="URL изображения"
              variant="outlined"
              :rules="[rules.url]"
            ></v-text-field>
          </v-col>

          <v-col cols="12" sm="6">
            <v-select
              v-model="form.category"
              :items="categories"
              item-title="category_title"
              item-value="category_id"
              label="Категория *"
              :rules="[rules.required]"
              variant="outlined"
              clearable
              required
            ></v-select>
          </v-col>

          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.product_brand_title"
              label="Бренд"
              variant="outlined"
            ></v-text-field>
          </v-col>

          <v-col cols="12">
            <v-switch
              v-model="form.product_is_active"
              label="Активен (отображается в каталоге)"
              color="primary"
            ></v-switch>
          </v-col>
        </v-row>

        <v-alert v-if="error" type="error" variant="tonal" class="mt-4">
          {{ error }}
        </v-alert>
      </v-form>
    </v-card-text>

    <v-card-actions class="pa-4">
      <v-spacer></v-spacer>
      <v-btn variant="text" @click="cancel">Отмена</v-btn>
      <v-btn
        color="primary"
        :loading="loading"
        :disabled="!valid || loading"
        @click="submitForm"
      >
        {{ isEdit ? 'Сохранить изменения' : 'Создать товар' }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { ref, reactive, computed, onMounted, defineEmits, defineProps } from 'vue'
import { useCatalogStore } from '@/store/catalog'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

const props = defineProps({
  productId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['saved', 'cancel'])

const catalogStore = useCatalogStore()
const { categories, loading, error } = storeToRefs(catalogStore)
const router = useRouter()

const isEdit = computed(() => !!props.productId)

const valid = ref(false)
const formRef = ref(null)

// Правила валидации
const rules = {
  required: v => !!v || 'Обязательное поле',
  minLength: len => v => (v && v.length >= len) || `Минимум ${len} символов`,
  positiveNumber: v => v > 0 || 'Цена должна быть больше 0',
  nonNegativeNumber: v => v >= 0 || 'Количество не может быть отрицательным',
  url: v => !v || /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/.test(v) || 'Некорректный URL'
}

// Форма
const form = reactive({
  product_title: '',
  product_description: '',
  product_price: null,
  product_quantity_in_stock: null,
  product_image_url: '',
  category: null,
  product_brand_title: '',
  product_is_active: true
})

onMounted(async () => {
  if (categories.value.length === 0) {
    await catalogStore.fetchCategories()
  }
  
  if (isEdit.value && props.productId) {
    const product = await catalogStore.fetchProductById(props.productId)

    if (product) {
      Object.assign(form, {
        product_title: product.product_title,
        product_description: product.product_description || '',
        product_price: product.product_price,
        product_quantity_in_stock: product.product_quantity_in_stock,
        product_image_url: product.product_image_url || '',
        category: product.category,
        product_brand_title: product.product_brand_title || '',
        product_is_active: product.product_is_active
      })
    } else {
      router.push('/dashboard/products')
    }
  }
})

const submitForm = async () => {
  const { valid: isValid } = await formRef.value.validate()
  if (!isValid) return

  let result
  if (isEdit.value) {
    result = await catalogStore.updateProduct(props.productId, form)
  } else {
    result = await catalogStore.createProduct(form)
  }

  if (result.success) {
    emit('saved', result.product)
  }
}

const cancel = () => {
  emit('cancel')
}
</script>