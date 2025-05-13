import { defineStore } from 'pinia'
import { flashcardsAPI } from '../api'

export const useFlashcardsStore = defineStore('flashcards', {
  state: () => ({
    flashcards: [],
    currentFlashcard: null,
    loading: false,
    error: null
  }),

  getters: {
    getFlashcardById: (state) => (id) => {
      return state.flashcards.find(card => card.id === id)
    }
  },

  actions: {
    async fetchFlashcards(deckId) {
      this.loading = true
      this.error = null

      try {
        const response = await flashcardsAPI.getFlashcards(deckId)
        this.flashcards = response.data
        this.loading = false
        return this.flashcards
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to fetch flashcards'
        return []
      }
    },

    async fetchFlashcard(id) {
      this.loading = true
      this.error = null

      try {
        const response = await flashcardsAPI.getFlashcard(id)
        this.currentFlashcard = response.data
        this.loading = false
        return this.currentFlashcard
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to fetch flashcard'
        return null
      }
    },

    async createFlashcard(flashcardData) {
      this.loading = true
      this.error = null

      try {
        const response = await flashcardsAPI.createFlashcard(flashcardData)
        // Add the new flashcard to the list
        this.flashcards.push(response.data)
        this.loading = false
        return response.data
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to create flashcard'
        return null
      }
    },

    async updateFlashcard(id, flashcardData) {
      this.loading = true
      this.error = null

      try {
        const response = await flashcardsAPI.updateFlashcard(id, flashcardData)
        // Update the flashcard in the list
        const index = this.flashcards.findIndex(card => card.id === id)
        if (index !== -1) {
          this.flashcards[index] = response.data
        }
        // Update current flashcard if it's the one being edited
        if (this.currentFlashcard && this.currentFlashcard.id === id) {
          this.currentFlashcard = response.data
        }
        this.loading = false
        return response.data
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to update flashcard'
        return null
      }
    },

    async deleteFlashcard(id) {
      this.loading = true
      this.error = null

      try {
        await flashcardsAPI.deleteFlashcard(id)
        // Remove the flashcard from the list
        this.flashcards = this.flashcards.filter(card => card.id !== id)
        // Clear current flashcard if it's the one being deleted
        if (this.currentFlashcard && this.currentFlashcard.id === id) {
          this.currentFlashcard = null
        }
        this.loading = false
        return true
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to delete flashcard'
        return false
      }
    },

    clearError() {
      this.error = null
    }
  }
})
