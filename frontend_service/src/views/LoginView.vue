<template>
  <div class="login">
    <v-container class="py-8">
      <v-row justify="center" align="center" class="min-height-screen">
        <v-col cols="12" sm="10" md="8" lg="6" xl="4">
          <!-- Login Card -->
          <v-card class="modern-card-elevated auth-card animate-scale-in">
            <!-- Header Section -->
            <div class="auth-header text-center pa-8 pb-4">
              <v-avatar size="100" class="gradient-primary mb-6 animate-pulse">
                <v-icon size="50" color="white">mdi-account-circle</v-icon>
              </v-avatar>
              <h1 class="text-h3 font-weight-bold gradient-text mb-2">Welcome Back</h1>
              <p class="text-h6 text-medium-emphasis">Sign in to your account to continue learning</p>
            </div>

            <v-card-text class="pa-8 pt-4">
              <!-- Error Alert -->
              <v-alert
                v-if="authStore.error"
                type="error"
                variant="tonal"
                class="mb-6 modern-card"
                closable
                @click:close="authStore.clearError()"
              >
                <template v-slot:prepend>
                  <v-icon>mdi-alert-circle</v-icon>
                </template>
                {{ authStore.error }}
              </v-alert>

              <!-- Login Form -->
              <v-form @submit.prevent="login" ref="form" class="space-y-6">
                <v-text-field
                  v-model="username"
                  label="Username"
                  variant="outlined"
                  required
                  :rules="[v => !!v || 'Username is required']"
                  prepend-inner-icon="mdi-account"
                  class="modern-input"
                  color="primary"
                ></v-text-field>

                <v-text-field
                  v-model="password"
                  label="Password"
                  variant="outlined"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  :rules="[v => !!v || 'Password is required']"
                  prepend-inner-icon="mdi-lock"
                  :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                  @click:append-inner="showPassword = !showPassword"
                  class="modern-input"
                  color="primary"
                ></v-text-field>

                <v-btn
                  type="submit"
                  class="modern-btn-primary"
                  size="large"
                  block
                  :loading="authStore.loading"
                  :disabled="authStore.loading"
                  prepend-icon="mdi-login"
                >
                  Sign In
                </v-btn>
              </v-form>
            </v-card-text>

            <!-- Footer Section -->
            <v-card-actions class="pa-8 pt-0">
              <div class="w-100 text-center">
                <v-divider class="mb-6"></v-divider>
                <p class="text-body-2 text-medium-emphasis mb-4">
                  Don't have an account yet?
                </p>
                <v-btn
                  variant="outlined"
                  class="modern-btn"
                  to="/register"
                  size="large"
                  prepend-icon="mdi-account-plus"
                >
                  Create Account
                </v-btn>
              </div>
            </v-card-actions>
          </v-card>

          <!-- Additional Info -->
          <div class="text-center mt-8 animate-fade-in animate-delay-300">
            <p class="text-body-2 text-medium-emphasis">
              <v-icon size="16" class="mr-1">mdi-shield-check</v-icon>
              Your data is secure and encrypted
            </p>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { useAuthStore } from '../store/auth'

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      showPassword: false,
      authStore: useAuthStore()
    }
  },
  methods: {
    async login() {
      // Validate form
      const isValid = this.$refs.form.validate()
      if (!isValid) return

      // Attempt login
      const success = await this.authStore.login(this.username, this.password)

      if (success) {
        // Redirect to home page
        this.$router.push('/')
      }
    }
  }
}
</script>

<style scoped>
/* Auth Layout */
.min-height-screen {
  min-height: calc(100vh - 160px);
}

.auth-card {
  max-width: 500px;
  margin: 0 auto;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.auth-header {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: var(--border-radius-2xl) var(--border-radius-2xl) 0 0;
}

.gradient-text {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Form Styling */
.modern-input {
  margin-bottom: 1.5rem;
}

.modern-input :deep(.v-field) {
  border-radius: var(--border-radius-lg);
  transition: all var(--transition-normal);
}

.modern-input :deep(.v-field:hover) {
  box-shadow: var(--shadow-sm);
}

.modern-input :deep(.v-field--focused) {
  box-shadow: var(--shadow-md);
}

/* Responsive Design */
@media (max-width: 768px) {
  .auth-header {
    padding: 2rem 1.5rem 1rem !important;
  }

  .auth-card .v-card-text {
    padding: 1.5rem !important;
  }

  .auth-card .v-card-actions {
    padding: 1.5rem !important;
    padding-top: 0 !important;
  }
}

/* Dark mode adjustments */
.v-theme--dark .auth-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.v-theme--dark .auth-header {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
}

/* Animation improvements */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.auth-header .v-avatar {
  animation: float 3s ease-in-out infinite;
}

/* Focus improvements */
.modern-input :deep(.v-field--focused .v-field__outline) {
  --v-field-border-width: 2px;
  --v-field-border-opacity: 1;
}
</style>
