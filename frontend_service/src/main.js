import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import 'vuetify/styles'
import './assets/styles/global.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

// Create Vuetify instance with modern theme
const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#6366F1', // Modern indigo
          secondary: '#64748B', // Slate gray
          accent: '#3B82F6', // Blue instead of amber
          error: '#EF4444', // Modern red
          info: '#3B82F6', // Blue
          success: '#10B981', // Emerald
          warning: '#2563EB', // Blue instead of amber
          surface: '#FFFFFF',
          background: '#F8FAFC', // Light gray background
          'on-surface': '#1E293B',
          'on-background': '#1E293B',
          'primary-lighten-1': '#818CF8',
          'primary-lighten-2': '#A5B4FC',
          'primary-darken-1': '#4F46E5',
          'primary-darken-2': '#4338CA',
        },
      },
      dark: {
        colors: {
          primary: '#818CF8', // Lighter indigo for dark mode
          secondary: '#94A3B8', // Lighter slate
          accent: '#60A5FA', // Lighter blue instead of amber
          error: '#F87171', // Lighter red
          info: '#60A5FA', // Lighter blue
          success: '#34D399', // Lighter emerald
          warning: '#3B82F6', // Blue instead of amber
          surface: '#1E293B',
          background: '#0F172A', // Dark slate background
          'on-surface': '#F1F5F9',
          'on-background': '#F1F5F9',
          'primary-lighten-1': '#A5B4FC',
          'primary-lighten-2': '#C7D2FE',
          'primary-darken-1': '#6366F1',
          'primary-darken-2': '#4F46E5',
        },
      },
    },
  },
})

// Create Pinia store
const pinia = createPinia()

// Create and mount Vue app
const app = createApp(App)
app.use(router)
app.use(pinia)
app.use(vuetify)
app.mount('#app')
