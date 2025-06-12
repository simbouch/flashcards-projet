<template>
  <div class="study">
    <v-container class="py-8">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state text-center py-12 animate-fade-in">
        <v-progress-circular
          indeterminate
          color="primary"
          size="80"
          width="6"
          class="mb-4"
        ></v-progress-circular>
        <h3 class="text-h5 font-weight-bold mb-2">Loading Study Session</h3>
        <p class="text-body-1 text-medium-emphasis">Preparing your flashcards...</p>
      </div>

      <!-- Main Study Interface -->
      <template v-else-if="deck && deck.flashcards && deck.flashcards.length > 0">
        <!-- Header Section -->
        <div class="study-header mb-8 animate-fade-in">
          <div class="d-flex align-center justify-space-between flex-wrap gap-4">
            <div>
              <h1 class="text-h3 font-weight-bold gradient-text mb-2">{{ deck.title }}</h1>
              <p class="text-h6 text-medium-emphasis">Study Session in Progress</p>
            </div>
            <v-btn
              variant="outlined"
              class="modern-btn"
              @click="$router.push(`/decks/${deckId}`)"
              size="large"
              prepend-icon="mdi-arrow-left"
            >
              Back to Deck
            </v-btn>
          </div>
        </div>

        <!-- Progress Section -->
        <v-row class="mb-6">
          <v-col cols="12">
            <v-card class="modern-card-elevated progress-card animate-slide-in-left">
              <v-card-text class="pa-6">
                <div class="d-flex align-center justify-space-between mb-4">
                  <h3 class="text-h5 font-weight-bold">Progress</h3>
                  <v-chip class="gradient-primary text-white" size="large">
                    {{ currentCardIndex + 1 }} / {{ activeCards.length }}
                  </v-chip>
                </div>

                <v-progress-linear
                  :model-value="(currentCardIndex / activeCards.length) * 100"
                  color="primary"
                  height="12"
                  rounded
                  class="mb-4"
                ></v-progress-linear>

                <div class="stats-grid">
                  <div class="stat-item">
                    <v-icon color="success" size="24" class="mb-2">mdi-check-circle</v-icon>
                    <p class="text-h6 font-weight-bold mb-1">{{ stats.mastered + stats.removed }}</p>
                    <p class="text-caption text-medium-emphasis">Mastered</p>
                  </div>
                  <div class="stat-item">
                    <v-icon color="info" size="24" class="mb-2">mdi-arrow-down-bold-circle</v-icon>
                    <p class="text-h6 font-weight-bold mb-1">{{ stats.fullback }}</p>
                    <p class="text-caption text-medium-emphasis">Review Later</p>
                  </div>
                  <div class="stat-item">
                    <v-icon color="info" size="24" class="mb-2">mdi-cards</v-icon>
                    <p class="text-h6 font-weight-bold mb-1">{{ activeCards.length }}</p>
                    <p class="text-caption text-medium-emphasis">Remaining</p>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Flashcard Display -->
        <v-row class="mb-6">
          <v-col cols="12">
            <div class="flashcard-wrapper">
              <!-- Question Card -->
              <transition name="flip" mode="out-in">
                <v-card
                  v-if="!showAnswer"
                  key="question"
                  class="flashcard-container question-card modern-card-elevated animate-scale-in"
                  @click="toggleAnswer"
                  hover
                >
                  <div class="card-gradient-overlay question-gradient"></div>
                  <div class="flashcard-content">
                    <div class="flashcard-header mb-6">
                      <v-avatar size="80" class="gradient-primary mb-4 animate-pulse">
                        <v-icon size="40" color="white">mdi-help-circle</v-icon>
                      </v-avatar>
                      <h3 class="text-h4 font-weight-bold text-primary mb-2">Question</h3>
                    </div>

                    <div class="flashcard-text mb-6">
                      <p class="text-h5 font-weight-medium text-center">{{ currentCard.question }}</p>
                    </div>

                    <div class="flashcard-footer">
                      <v-chip class="gradient-primary text-white" size="large">
                        <v-icon start>mdi-gesture-tap</v-icon>
                        Tap to reveal answer
                      </v-chip>
                    </div>
                  </div>
                </v-card>

                <!-- Answer Card -->
                <v-card
                  v-else
                  key="answer"
                  class="flashcard-container answer-card modern-card-elevated animate-scale-in"
                  @click="toggleAnswer"
                  hover
                >
                  <div class="card-gradient-overlay answer-gradient"></div>
                  <div class="flashcard-content">
                    <div class="flashcard-header mb-6">
                      <v-avatar size="80" class="gradient-info mb-4 animate-pulse">
                        <v-icon size="40" color="white">mdi-lightbulb-on</v-icon>
                      </v-avatar>
                      <h3 class="text-h4 font-weight-bold text-info mb-2">Answer</h3>
                    </div>

                    <div class="flashcard-text mb-6">
                      <p class="text-h5 font-weight-medium text-center">{{ currentCard.answer }}</p>
                    </div>

                    <div class="flashcard-footer">
                      <v-chip class="gradient-info text-white" size="large">
                        <v-icon start>mdi-gesture-tap</v-icon>
                        Tap to see question
                      </v-chip>
                    </div>
                  </div>
                </v-card>
              </transition>
            </div>
          </v-col>
        </v-row>

        <!-- Study Controls -->
        <v-row>
          <v-col cols="12">
            <v-card class="modern-card-elevated controls-card animate-slide-in-right">
              <v-card-text class="pa-6">
                <h3 class="text-h5 font-weight-bold text-center mb-6">Study Controls</h3>

                <div class="controls-grid">
                  <!-- Next Button -->
                  <v-tooltip location="top">
                    <template v-slot:activator="{ props }">
                      <v-btn
                        class="modern-btn control-btn"
                        color="primary"
                        size="large"
                        v-bind="props"
                        @click="nextCard"
                        :loading="saving"
                        block
                      >
                        <v-icon start>mdi-arrow-right-bold-circle</v-icon>
                        Next
                      </v-btn>
                    </template>
                    <span>Move card behind the next one</span>
                  </v-tooltip>

                  <!-- Fullback Button -->
                  <v-tooltip location="top">
                    <template v-slot:activator="{ props }">
                      <v-btn
                        class="modern-btn control-btn"
                        color="info"
                        size="large"
                        v-bind="props"
                        @click="fullbackCard"
                        :loading="saving"
                        block
                      >
                        <v-icon start>mdi-arrow-down-bold-circle</v-icon>
                        Review Later
                        <v-chip
                          v-if="currentCardFullbackCount > 0"
                          class="ml-2"
                          size="small"
                          color="white"
                        >
                          {{ currentCardFullbackCount }}
                        </v-chip>
                      </v-btn>
                    </template>
                    <span>Move to end of deck. Second review removes card.</span>
                  </v-tooltip>

                  <!-- Mastered Button -->
                  <v-tooltip location="top">
                    <template v-slot:activator="{ props }">
                      <v-btn
                        class="modern-btn control-btn"
                        color="success"
                        size="large"
                        v-bind="props"
                        @click="downCard"
                        :loading="saving"
                        block
                      >
                        <v-icon start>mdi-check-bold</v-icon>
                        Mastered
                      </v-btn>
                    </template>
                    <span>Mark as learned and remove from session</span>
                  </v-tooltip>

                  <!-- Quit Button -->
                  <v-tooltip location="top">
                    <template v-slot:activator="{ props }">
                      <v-btn
                        variant="outlined"
                        class="modern-btn control-btn"
                        color="error"
                        size="large"
                        v-bind="props"
                        @click="quitStudy"
                        block
                      >
                        <v-icon start>mdi-exit-to-app</v-icon>
                        End Session
                      </v-btn>
                    </template>
                    <span>End study session and return to deck</span>
                  </v-tooltip>
                </div>

                <div class="text-center mt-6">
                  <p class="text-body-2 text-medium-emphasis">
                    <v-icon size="16" class="mr-1">mdi-information</v-icon>
                    Tap the flashcard to flip between question and answer
                  </p>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </template>

      <template v-else-if="deck">
        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-title class="text-h5">
                {{ deck.title }}
              </v-card-title>

              <v-card-text>
                <v-alert type="info">
                  This deck doesn't have any flashcards yet.
                </v-alert>
              </v-card-text>

              <v-card-actions>
                <v-btn
                  color="primary"
                  @click="$router.push(`/decks/${deckId}`)"
                >
                  Back to Deck
                </v-btn>
              </v-card-actions>
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

    <!-- Study Complete Dialog -->
    <v-dialog
      v-model="showCompleteDialog"
      max-width="500px"
      persistent
    >
      <v-card>
        <v-card-title class="text-h5">
          Study Session Complete!
        </v-card-title>

        <v-card-text>
          <p>You've completed studying all flashcards in this deck.</p>

          <v-list>
            <v-list-item>
              <v-list-item-icon>
                <v-icon color="green">mdi-check-circle</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>Mastered (Down + Double Fullback): {{ stats.mastered + stats.removed }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-icon>
                <v-icon color="amber">mdi-arrow-down-bold-circle</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>Fullback: {{ stats.fullback }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-icon>
                <v-icon color="blue">mdi-information-outline</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>Total Cards Studied: {{ stats.mastered + stats.removed + stats.fullback }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card-text>

        <v-card-actions>
          <v-btn
            color="secondary"
            text
            @click="restartStudy"
          >
            Study Again
          </v-btn>

          <v-spacer></v-spacer>

          <v-btn
            color="primary"
            @click="finishStudy"
          >
            Finish
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { useDecksStore } from '../store/decks'
import { useStudyStore } from '../store/study'
import { useFlashcardsStore } from '../store/flashcards'

export default {
  name: 'StudyView',
  props: {
    deckId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      decksStore: useDecksStore(),
      studyStore: useStudyStore(),
      flashcardsStore: useFlashcardsStore(),
      loading: true,
      saving: false,
      currentCardIndex: 0,
      showAnswer: false,
      selectedDifficulty: null,
      showCompleteDialog: false,
      studySession: null,
      cardResponses: [],
      // Track the active cards in the study session
      activeCards: [],
      // Track fullback counts for each card
      fullbackCounts: {},
      stats: {
        mastered: 0,
        fullback: 0,
        removed: 0
      }
    }
  },
  computed: {
    deck() {
      return this.decksStore.currentDeck
    },
    currentCard() {
      if (!this.activeCards || this.activeCards.length === 0) {
        return null
      }
      return this.activeCards[this.currentCardIndex]
    },
    isLastCard() {
      return this.currentCardIndex === this.activeCards.length - 1
    },
    remainingCards() {
      return this.activeCards.length
    },
    isStudyComplete() {
      return this.activeCards.length === 0
    },
    // Get the fullback count for the current card
    currentCardFullbackCount() {
      if (!this.currentCard) return 0
      return this.fullbackCounts[this.currentCard.id] || 0
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
        const deck = await this.decksStore.fetchDeck(this.deckId)

        // If deck not found, check if it's a public deck
        if (!deck && this.decksStore.error) {
          // Try to fetch as public deck
          // Fetch public decks if not already loaded
          if (this.decksStore.publicDecks.length === 0) {
            await this.decksStore.fetchPublicDecks()
          }

          // Find the deck in public decks
          const publicDeck = this.decksStore.publicDecks.find(d => d.id === this.deckId)
          if (publicDeck) {
            // Create a deep copy of the public deck to avoid reference issues
            const publicDeckCopy = JSON.parse(JSON.stringify(publicDeck))

            // Set the current deck to the copy of the public deck
            this.decksStore.currentDeck = publicDeckCopy

            // Fetch flashcards for this deck
            try {
              const flashcardsResponse = await this.flashcardsStore.fetchFlashcards(this.deckId)
              if (flashcardsResponse) {
                // Add flashcards to the deck
                this.decksStore.currentDeck.flashcards = flashcardsResponse
                // Flashcards added to the deck
              }
            } catch (flashcardsError) {
              // Failed to fetch flashcards
            }
          }
        }

        // Initialize the active cards array with all flashcards from the deck
        if (this.deck && this.deck.flashcards && this.deck.flashcards.length > 0) {
          // Make a deep copy of the flashcards to avoid modifying the original
          this.activeCards = JSON.parse(JSON.stringify(this.deck.flashcards))

          // Initialize fullback counts for all cards
          this.activeCards.forEach(card => {
            this.fullbackCounts[card.id] = 0
          })

          // Study session initialized with cards
        } else {
          // No flashcards found in the deck
        }

        // Only create a study session if the user is authenticated
        if (localStorage.getItem('token')) {
          await this.createStudySession()
        }
      } catch (error) {
        // Failed to fetch deck
      } finally {
        this.loading = false
      }
    },

    async createStudySession() {
      try {
        this.studySession = await this.studyStore.createStudySession(this.deckId)
      } catch (error) {
        // Failed to create study session
      }
    },

    // Toggle between question and answer
    toggleAnswer() {
      this.showAnswer = !this.showAnswer
    },

    // Move to the next card (current card goes behind the next one)
    async nextCard() {
      if (!this.currentCard || this.activeCards.length <= 1) {
        this.checkStudyCompletion()
        return
      }

      this.saving = true

      try {
        // Get the current card
        const currentCard = this.activeCards[this.currentCardIndex]

        // Remove the current card from its position
        this.activeCards.splice(this.currentCardIndex, 1)

        // If there's a next card, insert the current card behind it
        if (this.currentCardIndex < this.activeCards.length) {
          // Insert the card just behind the next one (current position + 1)
          this.activeCards.splice(this.currentCardIndex + 1, 0, currentCard)
        } else {
          // If we're at the end, add it to the end
          this.activeCards.push(currentCard)
        }

        // Save study record if authenticated
        if (this.studySession) {
          try {
            await this.studyStore.createStudyRecord(
              this.studySession.id,
              currentCard.id,
              true // Considered correct since we're just moving it back
            )
          } catch (error) {
            // Failed to save study record
          }
        }

        // Update stats
        this.stats.fullback++

        // Reset for the next card
        this.showAnswer = false

        // Check if we need to show completion dialog
        this.checkStudyCompletion()
      } catch (error) {
        // Error during next card operation
      } finally {
        this.saving = false
      }
    },

    // Fullback - move card to end or remove if second fullback
    async fullbackCard() {
      if (!this.currentCard) return

      this.saving = true

      try {
        // Get the current card and its ID
        const currentCard = this.activeCards[this.currentCardIndex]
        const cardId = currentCard.id

        // Increment fullback count for this card
        this.fullbackCounts[cardId] = (this.fullbackCounts[cardId] || 0) + 1

        // Check if this is the second fullback
        if (this.fullbackCounts[cardId] >= 2) {
          // Remove the card (same as "down")
          this.activeCards.splice(this.currentCardIndex, 1)

          // Update stats
          this.stats.mastered++
        } else {
          // First fullback - move to end of deck

          // Remove the current card from its position
          this.activeCards.splice(this.currentCardIndex, 1)

          // Add it to the end
          this.activeCards.push(currentCard)

          // Update stats
          this.stats.fullback++
        }

        // Save study record if authenticated
        if (this.studySession) {
          try {
            await this.studyStore.createStudyRecord(
              this.studySession.id,
              cardId,
              this.fullbackCounts[cardId] >= 2 // Considered correct if mastered
            )
          } catch (error) {
            console.error('Failed to save study record:', error)
          }
        }

        // Reset for the next card
        this.showAnswer = false

        // Check if we need to show completion dialog
        this.checkStudyCompletion()
      } catch (error) {
        console.error('Error during fullback operation:', error)
      } finally {
        this.saving = false
      }
    },

    // Down - remove card from session (mark as learned)
    async downCard() {
      if (!this.currentCard) return

      this.saving = true

      try {
        // Get the current card ID before removing it
        const cardId = this.activeCards[this.currentCardIndex].id

        // Remove the card from the active cards
        this.activeCards.splice(this.currentCardIndex, 1)

        // Update stats
        this.stats.removed++

        // Save study record if authenticated
        if (this.studySession) {
          try {
            await this.studyStore.createStudyRecord(
              this.studySession.id,
              cardId,
              true // Considered correct since we're removing it
            )
          } catch (error) {
            console.error('Failed to save study record:', error)
          }
        }

        // Reset for the next card
        this.showAnswer = false

        // Check if we need to show completion dialog
        this.checkStudyCompletion()
      } catch (error) {
        console.error('Error during down card operation:', error)
      } finally {
        this.saving = false
      }
    },

    // Check if the study session is complete
    checkStudyCompletion() {
      // If no cards left or at the end of the deck
      if (this.activeCards.length === 0) {
        // End study session if authenticated
        if (this.studySession) {
          this.endStudySession()
        }

        // Show completion dialog
        this.showCompleteDialog = true
      }
    },

    // End the current study session
    async endStudySession() {
      if (!this.studySession) return

      try {
        await this.studyStore.endStudySession(this.studySession.id)
      } catch (error) {
        console.error('Failed to end study session:', error)
      }
    },

    // Quit the study session
    quitStudy() {
      // End study session if authenticated
      if (this.studySession) {
        this.endStudySession()
      }

      // Navigate back to the deck
      this.$router.push(`/decks/${this.deckId}`)
    },

    restartStudy() {
      // Reset UI state
      this.currentCardIndex = 0
      this.showAnswer = false
      this.selectedDifficulty = null
      this.showCompleteDialog = false

      // Reinitialize the active cards array with all flashcards from the deck
      if (this.deck && this.deck.flashcards && this.deck.flashcards.length > 0) {
        // Make a deep copy of the flashcards to avoid modifying the original
        this.activeCards = JSON.parse(JSON.stringify(this.deck.flashcards))

        // Reset fullback counts for all cards
        this.fullbackCounts = {}
        this.activeCards.forEach(card => {
          this.fullbackCounts[card.id] = 0
        })

        console.log(`Restarted study session with ${this.activeCards.length} cards`)
      }

      // Create a new study session if authenticated
      if (localStorage.getItem('token')) {
        this.createStudySession()
      }

      // Reset stats
      this.stats = {
        mastered: 0,
        fullback: 0,
        removed: 0
      }
      this.cardResponses = []
    },

    finishStudy() {
      this.$router.push(`/decks/${this.deckId}`)
    }
  }
}
</script>

<style scoped>
/* Header Section */
.study-header {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: var(--border-radius-2xl);
  padding: 2rem;
  margin-bottom: 2rem;
}

.gradient-text {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Progress Card */
.progress-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%);
  backdrop-filter: blur(10px);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  border-radius: var(--border-radius-lg);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  transition: all var(--transition-normal);
}

.stat-item:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

/* Flashcard Styles */
.flashcard-wrapper {
  perspective: 1000px;
  min-height: 500px;
}

.flashcard-container {
  height: 500px;
  cursor: pointer;
  border-radius: var(--border-radius-2xl);
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%);
  backdrop-filter: blur(20px);
}

.flashcard-container:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: var(--shadow-2xl);
}

.card-gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px;
  z-index: 1;
}

.question-gradient {
  background: var(--gradient-primary);
}

.answer-gradient {
  background: var(--gradient-info);
}

.flashcard-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 3rem;
  text-align: center;
  position: relative;
  z-index: 2;
}

.flashcard-header {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.flashcard-text {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 100%;
  overflow-wrap: break-word;
  word-break: break-word;
}

.flashcard-text p {
  line-height: 1.6;
  max-height: 200px;
  overflow-y: auto;
}

.flashcard-footer {
  margin-top: auto;
}

/* Controls Card */
.controls-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%);
  backdrop-filter: blur(10px);
}

.controls-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.control-btn {
  height: 60px !important;
  font-weight: 600 !important;
  transition: all var(--transition-normal) !important;
}

.control-btn:hover {
  transform: translateY(-5px) !important;
  box-shadow: var(--shadow-lg) !important;
}

/* Flip Animation */
.flip-enter-active,
.flip-leave-active {
  transition: all 0.6s ease-in-out;
}

.flip-enter-from {
  opacity: 0;
  transform: rotateY(-90deg) scale(0.8);
}

.flip-leave-to {
  opacity: 0;
  transform: rotateY(90deg) scale(0.8);
}

/* Loading State */
.loading-state {
  padding: 4rem 2rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .study-header {
    padding: 1.5rem;
    text-align: center;
  }

  .study-header .d-flex {
    flex-direction: column;
    gap: 1rem;
  }

  .flashcard-container {
    height: 400px;
  }

  .flashcard-content {
    padding: 2rem;
  }

  .controls-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }

  .stat-item {
    padding: 0.75rem;
  }
}

/* Dark mode adjustments */
.v-theme--dark .study-header {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
}

.v-theme--dark .progress-card,
.v-theme--dark .controls-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
}

.v-theme--dark .flashcard-container {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
}

.v-theme--dark .stat-item {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Animation improvements */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.flashcard-header .v-avatar {
  animation: float 3s ease-in-out infinite;
}

/* Custom scrollbar for flashcard text */
.flashcard-text p::-webkit-scrollbar {
  width: 6px;
}

.flashcard-text p::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.flashcard-text p::-webkit-scrollbar-thumb {
  background: var(--gradient-primary);
  border-radius: 3px;
}
</style>
