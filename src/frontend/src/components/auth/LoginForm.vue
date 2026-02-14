<template>
  <v-card class="mx-auto" max-width="500">
    <v-card-title class="text-h5 text-center bg-primary text-white py-4">
      <v-icon class="mr-2">mdi-login</v-icon>
      Вход в систему
    </v-card-title>

    <v-card-text class="pa-6">
      <v-form @submit.prevent="handleSubmit" ref="formRef">
        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          class="mb-4"
          closable
          @click:close="clearError"
        >
          {{ error }}
        </v-alert>

        <v-text-field
          v-model="form.user_mail"
          label="Email"
          type="email"
          prepend-icon="mdi-email"
          :rules="[rules.required, rules.email]"
          variant="outlined"
          density="comfortable"
          class="mb-3"
        ></v-text-field>

        <v-text-field
          v-model="form.password"
          label="Пароль"
          :type="showPassword ? 'text' : 'password'"
          prepend-icon="mdi-lock"
          :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
          @click:append-inner="showPassword = !showPassword"
          :rules="[rules.required]"
          variant="outlined"
          density="comfortable"
          class="mb-3"
        ></v-text-field>

        <div class="d-flex justify-space-between align-center mb-6">
          <v-checkbox
            v-model="form.remember"
            label="Запомнить меня"
            density="compact"
            hide-details
          ></v-checkbox>

          <router-link
            to="/forgot-password"
            class="text-primary text-decoration-none"
          >
            Забыли пароль?
          </router-link>
        </div>

        <v-btn
          type="submit"
          color="primary"
          size="large"
          block
          :loading="loading"
          :disabled="loading"
        >
          <v-icon left>mdi-login</v-icon>
          Войти
        </v-btn>
      </v-form>

      <v-divider class="my-6"></v-divider>

      <div class="text-center">
        <span class="text-body-2 text-disabled mr-2">Нет аккаунта?</span>
        <router-link
          to="/register"
          class="text-primary text-decoration-none font-weight-medium"
        >
          Зарегистрироваться
        </router-link>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const { loading, error } = storeToRefs(authStore)
const router = useRouter()

const form = reactive({
  user_mail: '',
  password: '',
  remember: false
})

const showPassword = ref(false)
const formRef = ref(null)

const rules = {
  required: value => !!value || 'Обязательное поле',
  email: value => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(value) || 'Некорректный email'
  }
}

const handleSubmit = async () => {
  const { valid } = await formRef.value.validate()

  if (valid) {
    const result = await authStore.login({
      user_mail: form.user_mail,
      password: form.password
    })

    if (result.success) {
      nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      console.log('Login result:', result)
      console.log('Is authenticated:', authStore.isAuthenticated)
      console.log('Token:', authStore.token)
      console.log('User:', authStore.user)

      router.push('/catalog')
    }
  }
}

const clearError = () => {
  authStore.clearError()
}
</script>