<template>
  <div class="login">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" sm="8" md="6">
          <v-card>
            <v-card-title class="text-h5 text-center">
              Login
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
              
              <v-form @submit.prevent="login" ref="form">
                <v-text-field
                  v-model="username"
                  label="Username"
                  required
                  :rules="[v => !!v || 'Username is required']"
                  prepend-icon="mdi-account"
                ></v-text-field>
                
                <v-text-field
                  v-model="password"
                  label="Password"
                  type="password"
                  required
                  :rules="[v => !!v || 'Password is required']"
                  prepend-icon="mdi-lock"
                ></v-text-field>
                
                <v-btn
                  color="primary"
                  type="submit"
                  block
                  :loading="authStore.loading"
                  :disabled="authStore.loading"
                  class="mt-4"
                >
                  Login
                </v-btn>
              </v-form>
            </v-card-text>
            
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                text
                color="primary"
                to="/register"
              >
                Don't have an account? Register
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
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
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
