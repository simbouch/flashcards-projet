<template>
  <div class="register">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" sm="8" md="6">
          <v-card>
            <v-card-title class="text-h5 text-center">
              Register
            </v-card-title>
            
            <v-card-text>
              <v-alert
                v-if="authStore.error"
                type="error"
                dismissible
                @click:close="authStore.clearError()"
              >
                {{ authStore.error }}
              </v-alert>
              
              <v-form @submit.prevent="register" ref="form">
                <v-text-field
                  v-model="email"
                  label="Email"
                  type="email"
                  required
                  :rules="[
                    v => !!v || 'Email is required',
                    v => /.+@.+\..+/.test(v) || 'Email must be valid'
                  ]"
                  prepend-icon="mdi-email"
                ></v-text-field>
                
                <v-text-field
                  v-model="username"
                  label="Username"
                  required
                  :rules="[
                    v => !!v || 'Username is required',
                    v => /^[a-zA-Z0-9_-]+$/.test(v) || 'Username must be alphanumeric with optional underscores and hyphens',
                    v => v.length >= 3 || 'Username must be at least 3 characters'
                  ]"
                  prepend-icon="mdi-account"
                ></v-text-field>
                
                <v-text-field
                  v-model="fullName"
                  label="Full Name"
                  prepend-icon="mdi-account-details"
                ></v-text-field>
                
                <v-text-field
                  v-model="password"
                  label="Password"
                  type="password"
                  required
                  :rules="[
                    v => !!v || 'Password is required',
                    v => v.length >= 8 || 'Password must be at least 8 characters',
                    v => /[A-Z]/.test(v) || 'Password must contain at least one uppercase letter',
                    v => /[a-z]/.test(v) || 'Password must contain at least one lowercase letter',
                    v => /[0-9]/.test(v) || 'Password must contain at least one number'
                  ]"
                  prepend-icon="mdi-lock"
                ></v-text-field>
                
                <v-text-field
                  v-model="confirmPassword"
                  label="Confirm Password"
                  type="password"
                  required
                  :rules="[
                    v => !!v || 'Please confirm your password',
                    v => v === password || 'Passwords do not match'
                  ]"
                  prepend-icon="mdi-lock-check"
                ></v-text-field>
                
                <v-btn
                  color="primary"
                  type="submit"
                  block
                  :loading="authStore.loading"
                  :disabled="authStore.loading"
                  class="mt-4"
                >
                  Register
                </v-btn>
              </v-form>
            </v-card-text>
            
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                text
                color="primary"
                to="/login"
              >
                Already have an account? Login
              </v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { useAuthStore } from '../store/auth'

export default {
  name: 'RegisterView',
  data() {
    return {
      email: '',
      username: '',
      fullName: '',
      password: '',
      confirmPassword: '',
      authStore: useAuthStore()
    }
  },
  methods: {
    async register() {
      // Validate form
      const isValid = this.$refs.form.validate()
      if (!isValid) return
      
      // Create user data object
      const userData = {
        email: this.email,
        username: this.username,
        full_name: this.fullName,
        password: this.password
      }
      
      // Attempt registration
      const success = await this.authStore.register(userData)
      
      if (success) {
        // Show success message and redirect to login
        this.$router.push({
          path: '/login',
          query: { registered: 'true' }
        })
      }
    }
  }
}
</script>
