<template>
  <div class="deck-detail">
    <v-container>
      <v-row v-if="loading">
        <v-col cols="12" class="text-center">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
          ></v-progress-circular>
        </v-col>
      </v-row>

      <template v-else-if="deck">
        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-title class="text-h4">
                {{ deck.title }}
                <v-chip
                  v-if="deck.is_public"
                  color="green"
                  small
                  class="ml-2"
                >
                  Public
                </v-chip>
              </v-card-title>

              <v-card-subtitle v-if="deck.description">
                {{ deck.description }}
              </v-card-subtitle>

              <v-card-text>
                <div class="text-body-2">
                  Created: {{ formatDate(deck.created_at) }}
                </div>

                <v-divider class="my-4"></v-divider>

                <div class="d-flex justify-space-between align-center mb-4">
                  <div class="text-h6">
                    Flashcards ({{ deck.flashcards ? deck.flashcards.length : 0 }})
                  </div>

                  <div>
                    <v-btn
                      color="grey darken-1"
                      @click="goBack"
                      class="mr-2"
                    >
                      <v-icon left>mdi-arrow-left</v-icon>
                      Back
                    </v-btn>

                    <v-btn
                      color="primary"
                      @click="startStudySession"
                      :disabled="!deck.flashcards || deck.flashcards.length === 0"
                      class="mr-2"
                    >
                      <v-icon left>mdi-book-open-variant</v-icon>
                      Study
                    </v-btn>

                    <v-btn
                      color="secondary"
                      @click="showAddCardDialog = true"
                      v-if="!isSystemDeck"
                      class="mr-2"
                    >
                      <v-icon left>mdi-plus</v-icon>
                      Add Card
                    </v-btn>

                    <v-btn
                      color="error"
                      @click="confirmDeleteDeck"
                      v-if="!isSystemDeck"
                    >
                      <v-icon left>mdi-delete</v-icon>
                      Delete Deck
                    </v-btn>
                  </div>
                </div>

                <v-alert
                  v-if="flashcardsStore.error"
                  type="error"
                  dismissible
                  @click:close="flashcardsStore.clearError()"
                >
                  {{ flashcardsStore.error }}
                </v-alert>

                <div v-if="!deck.flashcards || deck.flashcards.length === 0" class="text-center pa-4">
                  <p>No flashcards in this deck yet.</p>
                  <v-btn
                    v-if="!isSystemDeck"
                    color="primary"
                    @click="showAddCardDialog = true"
                    class="mt-2"
                  >
                    Add Your First Flashcard
                  </v-btn>
                  <p v-else class="mt-2 text-caption">
                    This is a native deck. You cannot add flashcards to it.
                  </p>
                </div>

                <v-expansion-panels v-else>
                  <v-expansion-panel
                    v-for="(card, index) in deck.flashcards"
                    :key="card.id"
                    class="mb-3"
                  >
                    <v-expansion-panel-header class="question-header">
                      <div class="d-flex align-center">
                        <v-chip class="mr-3" color="primary" small>{{ index + 1 }}</v-chip>
                        <div class="question-text">{{ card.question }}</div>
                      </div>
                    </v-expansion-panel-header>

                    <v-expansion-panel-content class="answer-content">
                      <div class="pa-4">
                        <v-card class="answer-card mb-3" color="amber lighten-5" outlined>
                          <v-card-text class="text-body-1">{{ card.answer }}</v-card-text>
                        </v-card>

                        <div class="d-flex justify-end mt-2" v-if="!isSystemDeck">
                          <v-btn
                            color="primary"
                            small
                            @click.stop="editCard(card)"
                            class="mr-2"
                          >
                            <v-icon left>mdi-pencil</v-icon>
                            Edit
                          </v-btn>

                          <v-btn
                            color="error"
                            small
                            @click.stop="deleteCard(card)"
                          >
                            <v-icon left>mdi-delete</v-icon>
                            Delete
                          </v-btn>
                        </div>
                      </div>
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-expansion-panels>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </template>

      <v-row v-else>
        <v-col cols="12">
          <v-alert type="error">
            Deck not found
          </v-alert>
          <v-btn
            color="primary"
            to="/decks"
            class="mt-4"
          >
            Back to Decks
          </v-btn>
        </v-col>
      </v-row>
    </v-container>

    <!-- Add/Edit Card Dialog -->
    <v-dialog
      v-model="showAddCardDialog"
      max-width="500px"
    >
      <v-card>
        <v-card-title class="text-h5">
          {{ editMode ? 'Edit Flashcard' : 'Add New Flashcard' }}
        </v-card-title>

        <v-card-text>
          <v-form ref="cardForm">
            <v-textarea
              v-model="cardForm.question"
              label="Question"
              rows="3"
              required
              :rules="[v => !!v || 'Question is required']"
            ></v-textarea>

            <v-textarea
              v-model="cardForm.answer"
              label="Answer"
              rows="3"
              required
              :rules="[v => !!v || 'Answer is required']"
            ></v-textarea>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="showAddCardDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            @click="saveCard"
            :loading="saving"
          >
            {{ editMode ? 'Update' : 'Add' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Card Confirmation Dialog -->
    <v-dialog
      v-model="showDeleteCardDialog"
      max-width="400px"
    >
      <v-card>
        <v-card-title class="text-h5">
          Confirm Delete
        </v-card-title>

        <v-card-text>
          Are you sure you want to delete this flashcard?
          This action cannot be undone.
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="showDeleteCardDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            @click="confirmDeleteCard"
            :loading="deleting"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Deck Confirmation Dialog -->
    <v-dialog
      v-model="showDeleteDeckDialog"
      max-width="400px"
    >
      <v-card>
        <v-card-title class="text-h5">
          Confirm Delete Deck
        </v-card-title>

        <v-card-text>
          Are you sure you want to delete the deck <strong>{{ deck?.title }}</strong>?
          This will also delete all flashcards in this deck.
          This action cannot be undone.
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="showDeleteDeckDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            @click="deleteDeck"
            :loading="deletingDeck"
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
.question-header {
  background-color: #e3f2fd !important;
}

.question-text {
  font-weight: 500;
}

.answer-content {
  background-color: #fff8e1 !important;
}

.answer-card {
  border-left: 4px solid #ffc107;
}
</style>
