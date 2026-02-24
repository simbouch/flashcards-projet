import { defineStore } from 'pinia'
import { authAPI } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
    currentUser: (state) => state.user
  },

  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null

      try {
        const response = await authAPI.login(username, password)
        const { access_token, refresh_token } = response.data

        // Save tokens
        this.token = access_token
        this.refreshToken = refresh_token
        localStorage.setItem('token', access_token)
        localStorage.setItem('refreshToken', refresh_token)

        // Get user profile
        await this.fetchUserProfile()

        this.loading = false
        return true
      } catch (error) {
        this.loading = false
        const status = error.response?.status
        const detail = error.response?.data?.detail
        const detailText = typeof detail === 'string' ? detail : null

        if (status === 401 || (detailText && /incorrect username or password/i.test(detailText))) {
          this.error = 'Incorrect username or password. Please try again.'
        } else {
          this.error = detailText || 'Login failed. Please try again.'
        }
        return false
      }
    },

    async register(userData) {
      this.loading = true
      this.error = null

      try {
        await authAPI.register(userData)
        this.loading = false
        return true
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Registration failed'
        return false
      }
    },

    async fetchUserProfile() {
      this.loading = true

      try {
        const response = await authAPI.getProfile()
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
        // Store userId in localStorage for other stores to use
        localStorage.setItem('userId', response.data.id)
        this.loading = false
        return response.data
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to fetch user profile'
        return null
      }
    },

    async updateProfile(userData) {
      this.loading = true
      this.error = null

      try {
        const response = await authAPI.updateProfile(userData)
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
        this.loading = false
        return true
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to update profile'
        return false
      }
    },

    async deleteAccount(password) {
      this.loading = true
      this.error = null

      try {
        await authAPI.deleteAccount(password)

        // Clear auth state + localStorage immediately (user is deleted)
        this.user = null
        this.token = null
        this.refreshToken = null
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        localStorage.removeItem('userId')

        this.loading = false
        return true
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to delete account'
        return false
      }
    },

    async logout() {
      try {
        // Call the logout API to revoke the refresh token
        if (this.refreshToken) {
          await authAPI.logout(this.refreshToken)
        }
      } catch (error) {
        console.error('Error during logout:', error)
      } finally {
        // Clear state and local storage regardless of API success
        this.user = null
        this.token = null
        this.refreshToken = null
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        localStorage.removeItem('userId')
      }
    },

    async refreshAccessToken() {
      if (!this.refreshToken) {
        return false
      }

      try {
        const response = await authAPI.refreshToken(this.refreshToken)
        const { access_token, refresh_token } = response.data

        // Update tokens
        this.token = access_token
        this.refreshToken = refresh_token
        localStorage.setItem('token', access_token)
        localStorage.setItem('refreshToken', refresh_token)

        return true
      } catch (error) {
        console.error('Failed to refresh token:', error)
        // If refresh token is invalid, logout the user
        this.logout()
        return false
      }
    },

    clearError() {
      this.error = null
    }
  }
})


