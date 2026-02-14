import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import router from './router'
import App from './App.vue'

import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import './assets/main.css'

// Создаем тему Imperial San
const imperialSanTheme = {
  dark: false,
  colors: {
    primary: '#2196F3',      // Синий (вода)
    secondary: '#607D8B',    // Серый (металл)
    accent: '#03A9F4',       // Голубой акцент
    error: '#F44336',
    warning: '#FF9800',
    info: '#00BCD4',
    success: '#4CAF50',
    background: '#F5F5F5',
    surface: '#FFFFFF',
    'surface-bright': '#FFFFFF',
    'surface-light': '#F5F5F5',
    'surface-variant': '#E0E0E0',
    'on-surface-variant': '#757575'
  }
}

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi }
  },
  theme: {
    defaultTheme: 'imperialSanTheme',
    themes: {
      imperialSanTheme
    }
  },
  defaults: {
    VBtn: {
      variant: 'tonal',
      rounded: 'lg'
    },
    VCard: {
      rounded: 'lg',
      elevation: 2
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable'
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable'
    }
  }
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(vuetify)

app.mount('#app')