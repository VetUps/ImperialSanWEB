<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <LoginForm />

        <v-card class="mt-4" variant="outlined">
          <v-card-text class="text-center">
            <div class="text-body-2 text-disabled mb-2">Тестовые аккаунты:</div>

            <v-chip-group>
              <v-chip
                v-for="account in testAccounts"
                :key="account.role"
                color="primary"
                variant="outlined"
                @click="fillTestAccount(account)"
                class="ma-1"
              >
                {{ account.role }}
              </v-chip>
            </v-chip-group>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import LoginForm from '@/components/auth/LoginForm.vue'
import { ref } from 'vue'

const testAccounts = ref([
  {
    role: 'Admin',
    user_mail: 'admin@imperialsan.ru',
    password: 'admin123'
  },
  {
    role: 'Manager',
    user_mail: 'manager@imperialsan.ru',
    password: 'manager123'
  },
  {
    role: 'User',
    user_mail: 'user@imperialsan.ru',
    password: 'user123'
  }
])

const fillTestAccount = (account) => {
  // Для демонстрации - можно отправить событие в LoginForm
  console.log('Test account:', account)
}
</script>