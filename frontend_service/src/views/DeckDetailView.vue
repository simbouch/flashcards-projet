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
                    >
                      <v-icon left>mdi-plus</v-icon>
                      Add Card
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
                    color="primary"
                    @click="showAddCardDialog = true"
                    class="mt-2"
                  >
                    Add Your First Flashcard
                  </v-btn>
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

                        <div class="d-flex justify-end mt-2">
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
      editMode: false,
      cardForm: {
        question: '',
        answer: ''
      },
      selectedCard: null,
      saving: false,
      deleting: false
    }
  },
  computed: {
    deck() {
      return this.decksStore.currentDeck
    }
  },
  created() {
    this.fetchDeck()
  },
  methods: {
    async fetchDeck() {
      this.loading = true
      try {
        // Try to fetch the deck
        await this.decksStore.fetchDeck(this.id)

        // If deck not found, check if it's a public deck
        if (!this.deck && this.decksStore.error) {
          console.log('Trying to fetch as public deck...')
          // Fetch public decks if not already loaded
          if (this.decksStore.publicDecks.length === 0) {
            await this.decksStore.fetchPublicDecks()
          }

          // Find the deck in public decks
          const publicDeck = this.decksStore.publicDecks.find(d => d.id === this.id)
          if (publicDeck) {
            // Set the current deck to the found public deck
            this.decksStore.currentDeck = publicDeck

            // Fetch flashcards for this deck
            try {
              const flashcardsResponse = await this.flashcardsStore.fetchFlashcards(this.id)
              if (flashcardsResponse) {
                // Add flashcards to the deck
                this.decksStore.currentDeck.flashcards = flashcardsResponse
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
