<!-- src/views/DashboardView.vue -->
<template>
  <v-container fluid class="pa-4">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h3 font-weight-bold text-primary mb-6">
          <v-icon class="mr-2" size="large">mdi-view-dashboard</v-icon>
          Панель управления
        </h1>
      </v-col>
    </v-row>

    <!-- Здесь будут отображаться дочерние страницы -->
    <router-view />
  </v-container>
</template>

<script setup>
// Здесь ничего не нужно, кроме возможной проверки прав
</script>