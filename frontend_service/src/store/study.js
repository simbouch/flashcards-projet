import { defineStore } from 'pinia'
import { studyAPI } from '../api'

export const useStudyStore = defineStore('study', {
  state: () => ({
    sessions: [],
    currentSession: null,
    records: [],
    loading: false,
    error: null
  }),
  
  getters: {
    getSessionById: (state) => (id) => {
      return state.sessions.find(session => session.id === id)
    }
  },
  
  actions: {
    async fetchStudySessions() {
      this.loading = true
      this.error = null
      
      try {
        const response = await studyAPI.getStudySessions()
        this.sessions = response.data
        this.loading = false
        return this.sessions
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to fetch study sessions'
        return []
      }
    },
    
    async fetchStudySession(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await studyAPI.getStudySession(id)
        this.currentSession = response.data
        this.loading = false
        return this.currentSession
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to fetch study session'
        return null
      }
    },
    
    async createStudySession(deckId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await studyAPI.createStudySession(deckId)
        // Add the new session to the list
        this.sessions.push(response.data)
        this.currentSession = response.data
        this.loading = false
        return response.data
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to create study session'
        return null
      }
    },
    
    async endStudySession(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await studyAPI.endStudySession(id)
        // Update the session in the list
        const index = this.sessions.findIndex(session => session.id === id)
        if (index !== -1) {
          this.sessions[index] = response.data
        }
        // Update current session if it's the one being ended
        if (this.currentSession && this.currentSession.id === id) {
          this.currentSession = response.data
        }
        this.loading = false
        return response.data
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to end study session'
        return null
      }
    },
    
    async fetchStudyRecords(sessionId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await studyAPI.getStudyRecords(sessionId)
        this.records = response.data
        this.loading = false
        return this.records
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to fetch study records'
        return []
      }
    },
    
    async createStudyRecord(sessionId, flashcardId, isCorrect) {
      this.loading = true
      this.error = null
      
      try {
        const response = await studyAPI.createStudyRecord(sessionId, flashcardId, isCorrect)
        // Add the new record to the list
        this.records.push(response.data)
        this.loading = false
        return response.data
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to create study record'
        return null
      }
    },
    
    clearError() {
      this.error = null
    }
  }
})
