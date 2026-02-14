<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8" lg="6">
        <RegisterForm />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import RegisterForm from '@/components/auth/RegisterForm.vue'
</script>