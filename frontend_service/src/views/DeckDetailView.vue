<template>
  <div class="deck-detail-view">
    <v-container class="py-8">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12 animate-fade-in">
        <v-progress-circular
          color="primary"
          size="64"
          width="6"
          indeterminate
          class="mb-4"
        ></v-progress-circular>
        <p class="text-h6 text-medium-emphasis">Loading deck details...</p>
      </div>

      <!-- Deck Content -->
      <template v-else-if="deck">
        <v-row justify="center">
          <v-col cols="12" md="10" lg="8">
            <!-- Deck Header -->
            <v-card class="modern-card mb-6 animate-slide-in-up">
              <div class="gradient-primary pa-6">
                <div class="d-flex align-center justify-space-between">
                  <div class="d-flex align-center">
                    <v-avatar size="64" class="gradient-secondary mr-4">
                      <v-icon size="32" color="white">mdi-cards-outline</v-icon>
                    </v-avatar>
                    <div>
                      <h1 class="text-h3 font-weight-bold text-white mb-2">{{ deck.title }}</h1>
                      <div class="d-flex align-center gap-2">
                        <v-chip
                          v-if="deck.is_public"
                          class="gradient-success text-white"
                          size="small"
                        >
                          <v-icon start size="16">mdi-earth</v-icon>
                          Public
                        </v-chip>
                        <v-chip
                          v-if="isSystemDeck"
                          class="gradient-info text-white"
                          size="small"
                        >
                          <v-icon start size="16">mdi-star</v-icon>
                          Native
                        </v-chip>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <v-card-text class="pa-6">
                <p v-if="deck.description" class="text-h6 mb-4">{{ deck.description }}</p>

                <!-- Deck Stats -->
                <div class="d-flex align-center justify-space-between mb-4">
                  <div class="d-flex align-center">
                    <v-icon size="20" class="text-medium-emphasis mr-2">mdi-calendar</v-icon>
                    <span class="text-body-2 text-medium-emphasis">Created: {{ formatDate(deck.created_at) }}</span>
                  </div>
                  <div class="d-flex align-center">
                    <v-icon size="20" class="text-medium-emphasis mr-2">mdi-card-multiple</v-icon>
                    <span class="text-body-2 text-medium-emphasis">{{ deck.flashcards ? deck.flashcards.length : 0 }} cards</span>
                  </div>
                </div>

                <!-- Action Buttons -->
                <div class="d-flex flex-wrap gap-2 mb-6">
                  <v-btn
                    class="modern-btn"
                    color="grey"
                    variant="outlined"
                    @click="goBack"
                    prepend-icon="mdi-arrow-left"
                  >
                    Back
                  </v-btn>

                  <v-btn
                    class="modern-btn"
                    color="primary"
                    @click="startStudySession"
                    :disabled="!deck.flashcards || deck.flashcards.length === 0"
                    prepend-icon="mdi-book-open-variant"
                  >
                    Study
                  </v-btn>

                  <v-btn
                    class="modern-btn"
                    color="info"
                    to="/study-history"
                    prepend-icon="mdi-history"
                  >
                    Study History
                  </v-btn>

                  <v-btn
                    v-if="!isSystemDeck"
                    class="modern-btn"
                    color="secondary"
                    @click="showAddCardDialog = true"
                    prepend-icon="mdi-plus"
                  >
                    Add Card
                  </v-btn>

                  <v-btn
                    v-if="!isSystemDeck"
                    class="modern-btn"
                    color="error"
                    variant="outlined"
                    @click="confirmDeleteDeck"
                    prepend-icon="mdi-delete"
                  >
                    Delete Deck
                  </v-btn>
                </div>

                <!-- Error Alert -->
                <v-alert
                  v-if="flashcardsStore.error"
                  type="error"
                  variant="tonal"
                  closable
                  @click:close="flashcardsStore.clearError()"
                  class="mb-6"
                >
                  {{ flashcardsStore.error }}
                </v-alert>
              </v-card-text>
            </v-card>

            <!-- Empty State -->
            <div v-if="!deck.flashcards || deck.flashcards.length === 0" class="text-center py-12 animate-fade-in">
              <v-avatar size="120" class="gradient-secondary mb-6 animate-pulse">
                <v-icon size="60" color="white">mdi-card-plus</v-icon>
              </v-avatar>
              <h3 class="text-h4 font-weight-bold mb-4">No Flashcards Yet</h3>
              <p class="text-h6 text-medium-emphasis mb-6">
                {{ isSystemDeck ? 'This is a native deck with no flashcards.' : 'Start building your deck by adding your first flashcard!' }}
              </p>
              <v-btn
                v-if="!isSystemDeck"
                class="modern-btn"
                color="primary"
                size="large"
                @click="showAddCardDialog = true"
                prepend-icon="mdi-plus"
              >
                Add Your First Flashcard
              </v-btn>
            </div>

            <!-- Flashcards List -->
            <div v-else class="animate-slide-in-up animate-delay-200">
              <h2 class="text-h4 font-weight-bold mb-6 text-center">
                Flashcards ({{ deck.flashcards.length }})
              </h2>

              <div class="flashcards-grid">
                <v-card
                  v-for="(card, index) in deck.flashcards"
                  :key="card.id"
                  class="modern-card flashcard-item mb-4 animate-scale-in"
                  :class="`animate-delay-${100 + (index % 5) * 100}`"
                >
                  <!-- Question Side -->
                  <div class="gradient-primary pa-4">
                    <div class="d-flex align-center justify-space-between">
                      <v-chip class="gradient-secondary text-white" size="small">
                        Card {{ index + 1 }}
                      </v-chip>
                      <v-icon color="white">mdi-help-circle</v-icon>
                    </div>
                  </div>

                  <v-card-text class="pa-6">
                    <h3 class="text-h6 font-weight-bold mb-4 text-white">Question</h3>
                    <p class="text-body-1 mb-6">{{ card.question }}</p>

                    <!-- Answer Section -->
                    <div class="answer-section">
                      <div class="d-flex align-center mb-3">
                        <v-avatar size="32" class="gradient-info mr-3">
                          <v-icon size="16" color="white">mdi-lightbulb</v-icon>
                        </v-avatar>
                        <h4 class="text-h6 font-weight-bold text-info">Answer</h4>
                      </div>
                      <div class="answer-card pa-4">
                        <p class="text-body-1 mb-0">{{ card.answer }}</p>
                      </div>
                    </div>

                    <!-- Card Actions -->
                    <div v-if="!isSystemDeck" class="d-flex justify-end gap-2 mt-4">
                      <v-btn
                        class="modern-btn"
                        color="primary"
                        size="small"
                        @click.stop="editCard(card)"
                        prepend-icon="mdi-pencil"
                      >
                        Edit
                      </v-btn>

                      <v-btn
                        class="modern-btn"
                        color="error"
                        size="small"
                        variant="outlined"
                        @click.stop="deleteCard(card)"
                        prepend-icon="mdi-delete"
                      >
                        Delete
                      </v-btn>
                    </div>
                  </v-card-text>
                </v-card>
              </div>
            </div>
          </v-col>
        </v-row>
      </template>

      <!-- Error State -->
      <div v-else class="text-center py-12 animate-fade-in">
        <v-avatar size="120" class="gradient-error mb-6">
          <v-icon size="60" color="white">mdi-alert-circle</v-icon>
        </v-avatar>
        <h3 class="text-h4 font-weight-bold mb-4">Deck Not Found</h3>
        <p class="text-h6 text-medium-emphasis mb-6">
          The deck you're looking for doesn't exist or has been removed.
        </p>
        <v-btn
          class="modern-btn"
          color="primary"
          size="large"
          to="/decks"
          prepend-icon="mdi-arrow-left"
        >
          Back to Decks
        </v-btn>
      </div>
    </v-container>

    <!-- Add/Edit Card Dialog -->
    <v-dialog
      v-model="showAddCardDialog"
      max-width="500px"
      class="glass-effect"
    >
      <v-card class="modern-card">
        <v-card-title class="pa-6 pb-4">
          <div class="d-flex align-center">
            <v-avatar size="48" class="gradient-primary mr-4">
              <v-icon size="24" color="white">{{ editMode ? 'mdi-pencil' : 'mdi-plus' }}</v-icon>
            </v-avatar>
            <div>
              <h3 class="text-h5 font-weight-bold">{{ editMode ? 'Edit Flashcard' : 'Add New Flashcard' }}</h3>
              <p class="text-caption text-medium-emphasis mb-0">{{ editMode ? 'Update your flashcard content' : 'Create a new flashcard for this deck' }}</p>
            </div>
          </div>
        </v-card-title>

        <v-card-text class="pa-6 pt-0">
          <v-form ref="cardForm">
            <v-textarea
              v-model="cardForm.question"
              label="Question"
              variant="outlined"
              rows="3"
              class="mb-4"
              prepend-inner-icon="mdi-help-circle"
              :rules="[v => !!v || 'Question is required']"
            ></v-textarea>

            <v-textarea
              v-model="cardForm.answer"
              label="Answer"
              variant="outlined"
              rows="3"
              class="mb-4"
              prepend-inner-icon="mdi-lightbulb"
              :rules="[v => !!v || 'Answer is required']"
            ></v-textarea>
          </v-form>
        </v-card-text>

        <v-card-actions class="pa-6 pt-0">
          <v-spacer></v-spacer>
          <v-btn
            class="modern-btn"
            color="grey"
            variant="outlined"
            @click="showAddCardDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            class="modern-btn ml-2"
            color="primary"
            @click="saveCard"
            :loading="saving"
            :prepend-icon="editMode ? 'mdi-content-save' : 'mdi-plus'"
          >
            {{ editMode ? 'Update Card' : 'Add Card' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Card Confirmation Dialog -->
    <v-dialog
      v-model="showDeleteCardDialog"
      max-width="400px"
      class="glass-effect"
    >
      <v-card class="modern-card">
        <v-card-title class="pa-6 pb-4">
          <div class="d-flex align-center">
            <v-avatar size="48" class="gradient-error mr-4">
              <v-icon size="24" color="white">mdi-delete</v-icon>
            </v-avatar>
            <div>
              <h3 class="text-h5 font-weight-bold">Confirm Delete</h3>
              <p class="text-caption text-medium-emphasis mb-0">This action cannot be undone</p>
            </div>
          </div>
        </v-card-title>

        <v-card-text class="pa-6 pt-0">
          <p class="text-body-2">
            Are you sure you want to delete this flashcard?
            This action cannot be undone.
          </p>
        </v-card-text>

        <v-card-actions class="pa-6 pt-0">
          <v-spacer></v-spacer>
          <v-btn
            class="modern-btn"
            color="grey"
            variant="outlined"
            @click="showDeleteCardDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            class="modern-btn ml-2"
            color="error"
            @click="confirmDeleteCard"
            :loading="deleting"
            prepend-icon="mdi-delete"
          >
            Delete Card
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Deck Confirmation Dialog -->
    <v-dialog
      v-model="showDeleteDeckDialog"
      max-width="500px"
      class="glass-effect"
    >
      <v-card class="modern-card">
        <v-card-title class="pa-6 pb-4">
          <div class="d-flex align-center">
            <v-avatar size="48" class="gradient-error mr-4">
              <v-icon size="24" color="white">mdi-delete</v-icon>
            </v-avatar>
            <div>
              <h3 class="text-h5 font-weight-bold">Confirm Delete Deck</h3>
              <p class="text-caption text-medium-emphasis mb-0">This action cannot be undone</p>
            </div>
          </div>
        </v-card-title>

        <v-card-text class="pa-6 pt-0">
          <p class="text-body-2 mb-4">
            Are you sure you want to delete the deck <strong>{{ deck?.title }}</strong>?
          </p>
          <v-alert
            type="warning"
            variant="tonal"
            class="mb-4"
          >
            This will also delete all flashcards in this deck. This action cannot be undone.
          </v-alert>
        </v-card-text>

        <v-card-actions class="pa-6 pt-0">
          <v-spacer></v-spacer>
          <v-btn
            class="modern-btn"
            color="grey"
            variant="outlined"
            @click="showDeleteDeckDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            class="modern-btn ml-2"
            color="error"
            @click="deleteDeck"
            :loading="deletingDeck"
            prepend-icon="mdi-delete"
          >
            Delete Deck
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { useDecksStore } from '../store/decks'
import { useFlashcardsStore } from '../store/flashcards'

export default {
  name: 'DeckDetailView',
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      decksStore: useDecksStore(),
      flashcardsStore: useFlashcardsStore(),
      loading: true,
      showAddCardDialog: false,
      showDeleteCardDialog: false,
      showDeleteDeckDialog: false,
      editMode: false,
      cardForm: {
        question: '',
        answer: ''
      },
      selectedCard: null,
      saving: false,
      deleting: false,
      deletingDeck: false
    }
  },
  computed: {
    deck() {
      return this.decksStore.currentDeck
    },
    isSystemDeck() {
      // Check if this is a system deck (public native deck)
      const result = this.deck &&
             this.deck.owner_id &&
             this.deck.owner_id.includes('system');

      console.log(`isSystemDeck check for deck ${this.deck?.title}:`, {
        hasDeck: !!this.deck,
        isPublic: this.deck?.is_public,
        ownerId: this.deck?.owner_id,
        includesSystem: this.deck?.owner_id?.includes('system'),
        result: result
      });

      return result;
    },

    isOwner() {
      if (!this.deck || !this.deck.owner_id) return false;

      const userId = this.decksStore.userId || localStorage.getItem('userId');
      const result = this.deck.owner_id === userId;

      console.log(`isOwner check for deck ${this.deck?.title}:`, {
        deckOwnerId: this.deck.owner_id,
        userId: userId,
        result: result
      });

      return result;
    }
  },
  created() {
    // Set userId from localStorage if not already set
    if (!this.decksStore.userId && localStorage.getItem('userId')) {
      this.decksStore.userId = localStorage.getItem('userId')
    }

    console.log('DeckDetailView created with userId:', {
      storeUserId: this.decksStore.userId,
      localStorageUserId: localStorage.getItem('userId')
    })

    this.fetchDeck()
  },
  methods: {
    async fetchDeck() {
      this.loading = true
      try {
        // Try to fetch the deck
        const deck = await this.decksStore.fetchDeck(this.id)

        if (deck) {
          console.log(`Successfully fetched deck: ${deck.title} with ${deck.flashcards?.length || 0} flashcards`, {
            deckOwnerId: deck.owner_id,
            storeUserId: this.decksStore.userId,
            localStorageUserId: localStorage.getItem('userId'),
            isOwner: deck.owner_id === this.decksStore.userId || deck.owner_id === localStorage.getItem('userId'),
            isSystemDeck: this.isSystemDeck
          })
        } else {
          console.log('Trying to fetch as public deck...')
          // Fetch public decks if not already loaded
          if (this.decksStore.publicDecks.length === 0) {
            await this.decksStore.fetchPublicDecks()
          }

          // Find the deck in public decks
          const publicDeck = this.decksStore.publicDecks.find(d => d.id === this.id)
          if (publicDeck) {
            // Create a deep copy to avoid reference issues
            this.decksStore.currentDeck = JSON.parse(JSON.stringify(publicDeck))

            // Fetch flashcards for this deck
            try {
              const flashcardsResponse = await this.flashcardsStore.fetchFlashcards(this.id)
              if (flashcardsResponse) {
                // Add flashcards to the deck
                this.decksStore.currentDeck.flashcards = flashcardsResponse
                console.log(`Added ${flashcardsResponse.length} flashcards to public deck ${this.id}`)
              }
            } catch (flashcardsError) {
              console.error('Failed to fetch flashcards:', flashcardsError)
            }
          }
        }
      } catch (error) {
        console.error('Failed to fetch deck:', error)
      } finally {
        this.loading = false
      }
    },

    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    },

    goBack() {
      // If it's a public deck, go back to public decks, otherwise go to my decks
      if (this.deck && this.deck.is_public && !this.deck.owner_id.includes(this.decksStore.userId)) {
        this.$router.push('/public-decks')
      } else {
        this.$router.push('/decks')
      }
    },

    startStudySession() {
      this.$router.push(`/study/${this.id}`)
    },

    editCard(card) {
      this.editMode = true
      this.selectedCard = card
      this.cardForm = {
        question: card.question,
        answer: card.answer
      }
      this.showAddCardDialog = true
    },

    deleteCard(card) {
      this.selectedCard = card
      this.showDeleteCardDialog = true
    },

    resetCardForm() {
      this.editMode = false
      this.selectedCard = null
      this.cardForm = {
        question: '',
        answer: ''
      }
      if (this.$refs.cardForm) {
        this.$refs.cardForm.reset()
      }
    },

    async saveCard() {
      // Validate form
      if (this.$refs.cardForm.validate()) {
        this.saving = true

        try {
          if (this.editMode) {
            // Update existing card
            await this.flashcardsStore.updateFlashcard(this.selectedCard.id, this.cardForm)

            // Update the card in the deck
            const index = this.deck.flashcards.findIndex(c => c.id === this.selectedCard.id)
            if (index !== -1) {
              this.deck.flashcards[index] = {
                ...this.deck.flashcards[index],
                ...this.cardForm
              }
            }
          } else {
            // Create new card
            const newCard = await this.flashcardsStore.createFlashcard({
              ...this.cardForm,
              deck_id: this.id
            })

            // Add the new card to the deck
            if (newCard) {
              if (!this.deck.flashcards) {
                this.deck.flashcards = []
              }
              this.deck.flashcards.push(newCard)
            }
          }

          this.showAddCardDialog = false
          this.resetCardForm()
        } catch (error) {
          console.error('Failed to save card:', error)
        } finally {
          this.saving = false
        }
      }
    },

    async confirmDeleteCard() {
      if (!this.selectedCard) return

      this.deleting = true

      try {
        await this.flashcardsStore.deleteFlashcard(this.selectedCard.id)

        // Remove the card from the deck
        const index = this.deck.flashcards.findIndex(c => c.id === this.selectedCard.id)
        if (index !== -1) {
          this.deck.flashcards.splice(index, 1)
        }

        this.showDeleteCardDialog = false
      } catch (error) {
        console.error('Failed to delete card:', error)
      } finally {
        this.deleting = false
      }
    },

    confirmDeleteDeck() {
      this.showDeleteDeckDialog = true
    },

    async deleteDeck() {
      this.deletingDeck = true

      try {
        const result = await this.decksStore.deleteDeck(this.id)

        if (result) {
          console.log(`Successfully deleted deck: ${this.id}`)
          // Close the dialog before navigation
          this.showDeleteDeckDialog = false
          // Navigate back to decks list after successful deletion
          this.$router.push('/decks')
        } else {
          console.error('Failed to delete deck: API returned false')
          this.decksStore.error = 'Failed to delete deck. Please try again.'
        }
      } catch (error) {
        console.error('Failed to delete deck:', error)
        this.decksStore.error = error.message || 'Failed to delete deck. Please try again.'
      } finally {
        this.deletingDeck = false
      }
    }
  }
}
</script>

<style scoped>
.deck-detail-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.v-theme--dark .deck-detail-view {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.flashcards-grid {
  display: grid;
  gap: 24px;
}

.flashcard-item {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.flashcard-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.answer-section {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(37, 99, 235, 0.05) 100%);
  border-radius: var(--border-radius-lg);
  padding: 16px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.answer-card {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: var(--border-radius-lg);
  border-left: 4px solid #3B82F6;
}

.v-theme--dark .answer-card {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border-left-color: #60A5FA;
}

.v-theme--dark .answer-section {
  background: linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
  border-color: rgba(96, 165, 250, 0.3);
}

/* Animation classes */
.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

.animate-slide-in-up {
  animation: slideInUp 0.6s ease-out;
}

.animate-scale-in {
  animation: scaleIn 0.5s ease-out;
}

.animate-pulse {
  animation: pulse 2s infinite;
}

.animate-delay-100 { animation-delay: 0.1s; }
.animate-delay-200 { animation-delay: 0.2s; }
.animate-delay-300 { animation-delay: 0.3s; }
.animate-delay-400 { animation-delay: 0.4s; }
.animate-delay-500 { animation-delay: 0.5s; }

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* Responsive design */
@media (max-width: 600px) {
  .flashcards-grid {
    gap: 16px;
  }

  .flashcard-item {
    margin-bottom: 16px;
  }
}
</style>
