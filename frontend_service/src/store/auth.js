import { defineStore } from 'pinia'
import { authAPI } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  },
  
  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null
      
      try {
        const response = await authAPI.login(username, password)
        const { access_token } = response.data
        
        // Save token
        this.token = access_token
        localStorage.setItem('token', access_token)
        
        // Get user profile
        await this.fetchUserProfile()
        
        this.loading = false
        return true
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Login failed'
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
    
    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
    
    clearError() {
      this.error = null
    }
  }
})
