<template>
  <v-card class="mx-auto" max-width="600">
    <v-card-title class="text-h5 text-center bg-primary text-white py-4">
      <v-icon class="mr-2">mdi-account-plus</v-icon>
      Регистрация
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

        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.user_surname"
              label="Фамилия"
              prepend-icon="mdi-account"
              :rules="[rules.required]"
              variant="outlined"
              density="comfortable"
            ></v-text-field>
          </v-col>

          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.user_name"
              label="Имя"
              :rules="[rules.required]"
              variant="outlined"
              density="comfortable"
            ></v-text-field>
          </v-col>
        </v-row>

        <v-text-field
          v-model="form.user_patronymic"
          label="Отчество"
          prepend-icon="mdi-account-details"
          variant="outlined"
          density="comfortable"
          class="mb-3"
        ></v-text-field>

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

        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.password"
              label="Пароль"
              :type="showPassword ? 'text' : 'password'"
              prepend-icon="mdi-lock"
              :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append-inner="showPassword = !showPassword"
              :rules="[rules.required, rules.minLength]"
              variant="outlined"
              density="comfortable"
            ></v-text-field>
          </v-col>

          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.passwordConfirm"
              label="Подтверждение пароля"
              :type="showPasswordConfirm ? 'text' : 'password'"
              prepend-icon="mdi-lock-check"
              :append-inner-icon="showPasswordConfirm ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append-inner="showPasswordConfirm = !showPasswordConfirm"
              :rules="[rules.required, rules.passwordMatch]"
              variant="outlined"
              density="comfortable"
            ></v-text-field>
          </v-col>
        </v-row>

        <v-btn
          type="submit"
          color="primary"
          size="large"
          block
          :loading="loading"
          :disabled="loading"
        >
          <v-icon left>mdi-account-plus</v-icon>
          Зарегистрироваться
        </v-btn>
      </v-form>

      <v-divider class="my-6"></v-divider>

      <div class="text-center">
        <span class="text-body-2 text-disabled mr-2">Уже есть аккаунт?</span>
        <router-link
          to="/login"
          class="text-primary text-decoration-none font-weight-medium"
        >
          Войти
        </router-link>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const { loading, error } = storeToRefs(authStore)
const router = useRouter()

const form = reactive({
  user_surname: '',
  user_name: '',
  user_patronymic: '',
  user_mail: '',
  password: '',
})

const showPassword = ref(false)
const showPasswordConfirm = ref(false)
const formRef = ref(null)

const rules = {
  required: value => !!value || 'Обязательное поле',
  email: value => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(value) || 'Некорректный email'
  },
  minLength: value => value.length >= 6 || 'Минимум 6 символов',
  passwordMatch: value => value === form.password || 'Пароли не совпадают'
}

const handleSubmit = async () => {
  const { valid } = await formRef.value.validate()

  if (valid) {
    const { passwordConfirm, agreeTerms, ...userData } = form

    console.log(userData)
    const result = await authStore.register(userData)
    console.log(result)

    if (result.success) {
      router.push('/catalog')
    }
  }
}

const clearError = () => {
  authStore.clearError()
}
</script>