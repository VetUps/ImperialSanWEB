<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" md="6" class="text-center">
        <v-icon size="120" color="grey-lighten-2">mdi-emoticon-sad-outline</v-icon>
        
        <h1 class="text-h2 font-weight-bold mt-8">404</h1>
        <h2 class="text-h5 mb-4">Страница не найдена</h2>
        
        <p class="text-body-1 text-disabled mb-8">
          Извините, но страница, которую вы ищете, не существует или была перемещена.
        </p>
        
        <v-btn
          color="primary"
          size="large"
          to="/"
          prepend-icon="mdi-home"
        >
          На главную
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
</script>