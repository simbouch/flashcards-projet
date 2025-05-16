<template>
  <div class="study">
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

      <template v-else-if="deck && deck.flashcards && deck.flashcards.length > 0">
        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-title class="text-h5">
                Studying: {{ deck.title }}
                <v-spacer></v-spacer>
                <v-btn
                  color="primary"
                  text
                  @click="$router.push(`/decks/${deckId}`)"
                >
                  <v-icon left>mdi-arrow-left</v-icon>
                  Back to Deck
                </v-btn>
              </v-card-title>

              <v-card-text>
                <div class="text-center mb-4">
                  <div class="text-body-1">
                    Card {{ currentCardIndex + 1 }} of {{ activeCards.length }}
                  </div>
                  <v-progress-linear
                    :value="(currentCardIndex / activeCards.length) * 100"
                    color="primary"
                    class="mt-2"
                  ></v-progress-linear>
                  <div class="text-caption mt-1">
                    <span class="mr-2">Mastered: {{ stats.mastered }}</span>
                    <span class="mr-2">Fullback: {{ stats.fullback }}</span>
                    <span>Removed: {{ stats.removed }}</span>
                  </div>
                </div>

                <!-- Question Card (shown when showAnswer is false) -->
                <v-card
                  v-if="!showAnswer"
                  class="flashcard-container question-card"
                  elevation="4"
                  @click="toggleAnswer"
                >
                  <div class="flashcard-content">
                    <v-icon class="question-icon mb-2" large>mdi-help-circle</v-icon>
                    <div class="text-h6 mb-3 primary--text">Question:</div>
                    <div class="text-body-1 question-text">{{ currentCard.question }}</div>
                    <v-chip class="mt-4" color="primary" small>
                      <v-icon left small>mdi-gesture-tap</v-icon>
                      Click to see answer
                    </v-chip>
                  </div>
                </v-card>

                <!-- Answer Card (shown when showAnswer is true) -->
                <v-card
                  v-else
                  class="flashcard-container answer-card"
                  elevation="4"
                  @click="toggleAnswer"
                >
                  <div class="flashcard-content">
                    <v-icon class="answer-icon mb-2" large>mdi-lightbulb-on</v-icon>
                    <div class="text-h6 mb-3 amber--text text--darken-2">Answer:</div>
                    <div class="text-body-1 answer-text">{{ currentCard.answer }}</div>
                    <v-chip class="mt-4" color="amber" small>
                      <v-icon left small>mdi-gesture-tap</v-icon>
                      Click to see question
                    </v-chip>
                  </div>
                </v-card>

                <!-- Study controls are always visible -->
                <div class="text-center mt-6">
                  <div class="text-h6 mb-3">Study Controls</div>
                  <div class="study-controls">
                    <v-tooltip bottom>
                      <template v-slot:activator="{ on, attrs }">
                        <v-btn
                          color="primary"
                          class="mx-2 px-4 control-btn"
                          height="50"
                          v-bind="attrs"
                          v-on="on"
                          @click="nextCard"
                          :loading="saving"
                        >
                          <v-icon left>mdi-arrow-right-bold-circle</v-icon>
                          Next
                        </v-btn>
                      </template>
                      <span>Move card behind the next one</span>
                    </v-tooltip>

                    <v-tooltip bottom>
                      <template v-slot:activator="{ on, attrs }">
                        <v-btn
                          color="amber darken-2"
                          class="mx-2 px-4 control-btn"
                          height="50"
                          v-bind="attrs"
                          v-on="on"
                          @click="fullbackCard"
                          :loading="saving"
                        >
                          <v-icon left>mdi-arrow-down-bold-circle</v-icon>
                          Fullback <span v-if="currentCardFullbackCount > 0" class="ml-1">({{ currentCardFullbackCount }})</span>
                        </v-btn>
                      </template>
                      <span>Move to end of deck. Second fullback removes card.</span>
                    </v-tooltip>

                    <v-tooltip bottom>
                      <template v-slot:activator="{ on, attrs }">
                        <v-btn
                          color="green"
                          class="mx-2 px-4 control-btn"
                          height="50"
                          v-bind="attrs"
                          v-on="on"
                          @click="downCard"
                          :loading="saving"
                        >
                          <v-icon left>mdi-check-bold</v-icon>
                          Down
                        </v-btn>
                      </template>
                      <span>Remove card from session (mark as learned)</span>
                    </v-tooltip>

                    <v-tooltip bottom>
                      <template v-slot:activator="{ on, attrs }">
                        <v-btn
                          color="grey darken-1"
                          class="mx-2 px-4 control-btn"
                          height="50"
                          v-bind="attrs"
                          v-on="on"
                          @click="quitStudy"
                        >
                          <v-icon left>mdi-exit-to-app</v-icon>
                          Quit
                        </v-btn>
                      </template>
                      <span>End study session</span>
                    </v-tooltip>
                  </div>

                  <div class="text-caption mt-3">
                    Click on the card to flip between question and answer
                  </div>
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
.flashcard-container {
  height: 350px;
  cursor: pointer;
  margin: 20px 0;
  border-radius: 12px;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1) !important;
  transition: all 0.3s ease;
}

.flashcard-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15) !important;
}

.question-card {
  background-color: #e3f2fd;
  border: 2px solid #2196F3;
}

.answer-card {
  background-color: #fff8e1;
  border: 2px solid #FFC107;
}

.flashcard-content {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 30px;
  text-align: center;
}

.question-text, .answer-text {
  font-size: 1.2rem;
  line-height: 1.6;
  max-width: 100%;
  overflow-wrap: break-word;
  margin-bottom: 20px;
}

.question-icon {
  color: #2196F3;
}

.answer-icon {
  color: #FFC107;
}

.study-controls {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
}

.control-btn {
  transition: all 0.3s ease;
  margin-bottom: 10px;
}

.control-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
</style>
