import { defineStore } from 'pinia'
import { decksAPI } from '../api'

export const useDecksStore = defineStore('decks', {
  state: () => ({
    decks: [],
    publicDecks: [],
    currentDeck: null,
    loading: false,
    error: null
  }),

  getters: {
    getDeckById: (state) => (id) => {
      return state.decks.find(deck => deck.id === id) ||
             state.publicDecks.find(deck => deck.id === id)
    }
  },

  actions: {
    async fetchDecks() {
      this.loading = true
      this.error = null

      try {
        const response = await decksAPI.getDecks()
        this.decks = response.data
        this.loading = false
        return this.decks
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to fetch decks'
        return []
      }
    },

    async fetchPublicDecks() {
      this.loading = true
      this.error = null

      try {
        const response = await decksAPI.getPublicDecks()
        this.publicDecks = response.data
        this.loading = false
        return this.publicDecks
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to fetch public decks'
        return []
      }
    },

    async fetchDeck(id) {
      this.loading = true
      this.error = null

      try {
        const response = await decksAPI.getDeck(id)
        this.currentDeck = response.data
        this.loading = false
        return this.currentDeck
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to fetch deck'
        return null
      }
    },

    async createDeck(deckData) {
      this.loading = true
      this.error = null

      try {
        const response = await decksAPI.createDeck(deckData)
        // Add the new deck to the list
        this.decks.push(response.data)
        this.loading = false
        return response.data
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to create deck'
        return null
      }
    },

    async updateDeck(id, deckData) {
      this.loading = true
      this.error = null

      try {
        const response = await decksAPI.updateDeck(id, deckData)
        // Update the deck in the list
        const index = this.decks.findIndex(deck => deck.id === id)
        if (index !== -1) {
          this.decks[index] = response.data
        }
        // Update current deck if it's the one being edited
        if (this.currentDeck && this.currentDeck.id === id) {
          this.currentDeck = response.data
        }
        this.loading = false
        return response.data
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to update deck'
        return null
      }
    },

    async deleteDeck(id) {
      this.loading = true
      this.error = null

      try {
        await decksAPI.deleteDeck(id)
        // Remove the deck from the list
        this.decks = this.decks.filter(deck => deck.id !== id)
        // Clear current deck if it's the one being deleted
        if (this.currentDeck && this.currentDeck.id === id) {
          this.currentDeck = null
        }
        this.loading = false
        return true
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to delete deck'
        return false
      }
    },

    async shareDeck(deckId, userId) {
      this.loading = true
      this.error = null

      try {
        const response = await decksAPI.shareDeck(deckId, userId)
        this.loading = false
        return response.data
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to share deck'
        return null
      }
    },

    clearError() {
      this.error = null
    }
  }
})
