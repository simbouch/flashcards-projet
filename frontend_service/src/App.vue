<template>
  <v-app>
    <!-- Modern Navigation Bar with Glass Effect -->
    <v-app-bar
      app
      :elevation="0"
      class="glass-effect modern-navbar"
      height="80"
    >
      <v-container class="d-flex align-center">
        <!-- Mobile Menu Button -->
        <v-app-bar-nav-icon
          @click="drawer = !drawer"
          class="d-md-none modern-btn"
        ></v-app-bar-nav-icon>

        <!-- Logo and Brand -->
        <router-link to="/" class="text-decoration-none d-flex align-center">
          <v-avatar size="48" class="gradient-primary mr-3 animate-pulse">
            <v-icon size="28" color="white">mdi-cards</v-icon>
          </v-avatar>
          <div class="brand-text d-none d-sm-block">
            <h2 class="text-h5 font-weight-bold mb-0 gradient-text">FlashCards</h2>
            <p class="text-caption mb-0 text-medium-emphasis">AI-Powered Learning</p>
          </div>
        </router-link>

        <v-spacer></v-spacer>

        <!-- Desktop Navigation Menu -->
        <div class="d-none d-md-flex align-center">
          <template v-if="isAuthenticated">
            <v-btn
              variant="text"
              to="/documents"
              class="modern-btn mx-1"
              prepend-icon="mdi-file-document"
            >
              Documents
            </v-btn>

            <v-btn
              variant="text"
              to="/decks"
              class="modern-btn mx-1"
              prepend-icon="mdi-cards"
            >
              My Decks
            </v-btn>

            <v-btn
              variant="text"
              to="/public-decks"
              class="modern-btn mx-1"
              prepend-icon="mdi-cards-outline"
            >
              Public Decks
            </v-btn>

            <!-- User Menu -->
            <v-menu offset-y>
              <template v-slot:activator="{ props }">
                <v-btn
                  icon
                  v-bind="props"
                  class="ml-2"
                >
                  <v-avatar size="40" class="gradient-secondary">
                    <v-icon color="white">mdi-account-circle</v-icon>
                  </v-avatar>
                </v-btn>
              </template>
              <v-list class="modern-card">
                <v-list-item @click="logout" class="modern-btn">
                  <template v-slot:prepend>
                    <v-icon>mdi-logout</v-icon>
                  </template>
                  <v-list-item-title>Logout</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </template>

          <template v-else>
            <v-btn
              variant="text"
              to="/public-decks"
              class="modern-btn mx-1"
              prepend-icon="mdi-cards-outline"
            >
              Public Decks
            </v-btn>

            <v-btn
              variant="outlined"
              to="/login"
              class="modern-btn mx-1"
              prepend-icon="mdi-login"
            >
              Login
            </v-btn>

            <v-btn
              variant="flat"
              to="/register"
              class="modern-btn-primary mx-1"
              prepend-icon="mdi-account-plus"
            >
              Register
            </v-btn>
          </template>
        </div>
      </v-container>
    </v-app-bar>

    <!-- Modern Mobile Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      app
      temporary
      class="modern-card"
      width="280"
    >
      <div class="pa-4">
        <div class="d-flex align-center mb-4">
          <v-avatar size="40" class="gradient-primary mr-3">
            <v-icon color="white">mdi-cards</v-icon>
          </v-avatar>
          <div>
            <h3 class="text-h6 font-weight-bold gradient-text">FlashCards</h3>
            <p class="text-caption mb-0 text-medium-emphasis">AI-Powered Learning</p>
          </div>
        </div>
        <v-divider class="mb-4"></v-divider>
      </div>

      <v-list class="space-y-2 px-2">
        <v-list-item
          to="/"
          class="modern-btn mb-2"
          prepend-icon="mdi-home"
          title="Home"
        ></v-list-item>

        <v-list-item
          v-if="isAuthenticated"
          to="/documents"
          class="modern-btn mb-2"
          prepend-icon="mdi-file-document"
          title="Documents"
        ></v-list-item>

        <v-list-item
          v-if="isAuthenticated"
          to="/decks"
          class="modern-btn mb-2"
          prepend-icon="mdi-cards"
          title="My Decks"
        ></v-list-item>

        <v-list-item
          to="/public-decks"
          class="modern-btn mb-2"
          prepend-icon="mdi-cards-outline"
          title="Public Decks"
        ></v-list-item>

        <v-list-item
          v-if="isAuthenticated"
          to="/study-history"
          class="modern-btn mb-2"
          prepend-icon="mdi-history"
          title="Study History"
        ></v-list-item>

        <v-list-item
          v-if="isAuthenticated"
          to="/profile"
          class="modern-btn mb-2"
          prepend-icon="mdi-account"
          title="Profile"
        ></v-list-item>

        <v-divider class="my-4" v-if="isAuthenticated"></v-divider>

        <v-list-item
          v-if="isAuthenticated"
          @click="logout"
          class="modern-btn mb-2"
          prepend-icon="mdi-logout"
          title="Logout"
        ></v-list-item>

        <template v-if="!isAuthenticated">
          <v-divider class="my-4"></v-divider>
          <v-list-item
            to="/login"
            class="modern-btn mb-2"
            prepend-icon="mdi-login"
            title="Login"
          ></v-list-item>
          <v-list-item
            to="/register"
            class="modern-btn-primary mb-2"
            prepend-icon="mdi-account-plus"
            title="Register"
          ></v-list-item>
        </template>
      </v-list>
    </v-navigation-drawer>

    <!-- Main Content with Smooth Transitions -->
    <v-main class="main-content">
      <transition name="page" mode="out-in">
        <router-view />
      </transition>
    </v-main>

    <!-- Modern Footer -->
    <v-footer class="gradient-primary text-center py-4">
      <div class="text-white">
        <p class="mb-1 font-weight-medium">
          {{ new Date().getFullYear() }} — <strong>FlashCards App</strong>
        </p>
        <p class="text-caption mb-0 opacity-80">
          Powered by AI • Built with ❤️
        </p>
      </div>
    </v-footer>
  </v-app>
</template>

<script>
import { useAuthStore } from './store/auth'
import { mapState } from 'pinia'

export default {
  name: 'App',
  data() {
    return {
      drawer: false,
      snackbar: {
        show: false,
        message: '',
        color: 'info',
        timeout: 4000
      }
    }
  },
  computed: {
    ...mapState(useAuthStore, ['isAuthenticated'])
  },
  methods: {
    logout() {
      const authStore = useAuthStore()
      authStore.logout()
      this.$router.push('/login')
    },
    getSnackbarIcon() {
      const iconMap = {
        success: 'mdi-check-circle',
        error: 'mdi-alert-circle',
        warning: 'mdi-alert',
        info: 'mdi-information'
      }
      return iconMap[this.snackbar.color] || 'mdi-information'
    }
  }
}
</script>

<style scoped>
/* Modern App Styles */
.modern-navbar {
  backdrop-filter: blur(20px) !important;
  background: rgba(255, 255, 255, 0.95) !important;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1) !important;
}

.brand-text {
  transition: all var(--transition-fast);
}

.gradient-text {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.main-content {
  background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
  min-height: calc(100vh - 160px);
}

/* Page Transitions */
.page-enter-active,
.page-leave-active {
  transition: all 0.4s ease-in-out;
}

.page-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.page-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .brand-text h2 {
    font-size: 1.2rem !important;
  }

  .brand-text p {
    font-size: 0.7rem !important;
  }
}

/* Dark mode adjustments */
.v-theme--dark .modern-navbar {
  background: rgba(30, 41, 59, 0.95) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.v-theme--dark .main-content {
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
}

/* Custom scrollbar for navigation drawer */
.v-navigation-drawer ::-webkit-scrollbar {
  width: 6px;
}

.v-navigation-drawer ::-webkit-scrollbar-track {
  background: transparent;
}

.v-navigation-drawer ::-webkit-scrollbar-thumb {
  background: var(--gradient-primary);
  border-radius: 3px;
}
</style>
