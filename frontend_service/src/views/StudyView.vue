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
                    Card {{ currentCardIndex + 1 }} of {{ deck.flashcards.length }}
                  </div>
                  <v-progress-linear
                    :value="(currentCardIndex / deck.flashcards.length) * 100"
                    color="primary"
                    class="mt-2"
                  ></v-progress-linear>
                </div>

                <v-card
                  class="flashcard-container"
                  :class="{ 'flipped': showAnswer }"
                  elevation="4"
                  @click="toggleAnswer"
                >
                  <div class="flashcard">
                    <div class="flashcard-front">
                      <v-icon class="question-icon mb-2" large>mdi-help-circle</v-icon>
                      <div class="text-h6 mb-3 primary--text">Question:</div>
                      <div class="text-body-1 question-text">{{ currentCard.question }}</div>
                      <v-chip class="mt-4" color="primary" small>
                        <v-icon left small>mdi-gesture-tap</v-icon>
                        Click to see answer
                      </v-chip>
                    </div>

                    <div class="flashcard-back">
                      <v-icon class="answer-icon mb-2" large>mdi-lightbulb-on</v-icon>
                      <div class="text-h6 mb-3 amber--text text--darken-2">Answer:</div>
                      <div class="text-body-1 answer-text">{{ currentCard.answer }}</div>
                      <v-chip class="mt-4" color="amber" small>
                        <v-icon left small>mdi-gesture-tap</v-icon>
                        Click to see question
                      </v-chip>
                    </div>
                  </div>
                </v-card>

                <div class="text-center mt-6" v-if="showAnswer">
                  <div class="text-h6 mb-3">How well did you know this?</div>
                  <v-btn-toggle
                    v-model="selectedDifficulty"
                    mandatory
                    class="difficulty-buttons"
                  >
                    <v-btn
                      value="hard"
                      color="red"
                      :outlined="selectedDifficulty !== 'hard'"
                      :dark="selectedDifficulty === 'hard'"
                      class="mx-2 px-4 difficulty-btn"
                      height="50"
                    >
                      <v-icon left>mdi-emoticon-sad</v-icon>
                      Hard
                    </v-btn>

                    <v-btn
                      value="medium"
                      color="orange"
                      :outlined="selectedDifficulty !== 'medium'"
                      :dark="selectedDifficulty === 'medium'"
                      class="mx-2 px-4 difficulty-btn"
                      height="50"
                    >
                      <v-icon left>mdi-emoticon-neutral</v-icon>
                      Medium
                    </v-btn>

                    <v-btn
                      value="easy"
                      color="green"
                      :outlined="selectedDifficulty !== 'easy'"
                      :dark="selectedDifficulty === 'easy'"
                      class="mx-2 px-4 difficulty-btn"
                      height="50"
                    >
                      <v-icon left>mdi-emoticon-happy</v-icon>
                      Easy
                    </v-btn>
                  </v-btn-toggle>
                </div>
              </v-card-text>

              <v-card-actions>
                <v-btn
                  color="grey darken-1"
                  outlined
                  @click="previousCard"
                  :disabled="currentCardIndex === 0 || !showAnswer"
                  class="px-4"
                >
                  <v-icon left>mdi-arrow-left</v-icon>
                  Previous
                </v-btn>

                <v-spacer></v-spacer>

                <v-tooltip bottom :disabled="showAnswer && selectedDifficulty">
                  <template v-slot:activator="{ on, attrs }">
                    <div v-on="on" v-bind="attrs">
                      <v-btn
                        color="primary"
                        @click="nextCard"
                        :disabled="!showAnswer || !selectedDifficulty"
                        :loading="saving"
                        class="px-4"
                      >
                        {{ isLastCard ? 'Finish' : 'Next' }}
                        <v-icon right>mdi-arrow-right</v-icon>
                      </v-btn>
                    </div>
                  </template>
                  <span v-if="!showAnswer">Flip the card to see the answer first</span>
                  <span v-else-if="!selectedDifficulty">Select how well you knew this card</span>
                </v-tooltip>
              </v-card-actions>
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
                <v-list-item-title>Easy: {{ stats.easy }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-icon>
                <v-icon color="orange">mdi-alert-circle</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>Medium: {{ stats.medium }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-icon>
                <v-icon color="red">mdi-close-circle</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>Hard: {{ stats.hard }}</v-list-item-title>
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
      loading: true,
      saving: false,
      currentCardIndex: 0,
      showAnswer: false,
      selectedDifficulty: null,
      showCompleteDialog: false,
      studySession: null,
      cardResponses: [],
      stats: {
        easy: 0,
        medium: 0,
        hard: 0
      }
    }
  },
  computed: {
    deck() {
      return this.decksStore.currentDeck
    },
    currentCard() {
      if (!this.deck || !this.deck.flashcards || this.deck.flashcards.length === 0) {
        return null
      }
      return this.deck.flashcards[this.currentCardIndex]
    },
    isLastCard() {
      return this.currentCardIndex === this.deck.flashcards.length - 1
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
        await this.decksStore.fetchDeck(this.deckId)

        // If deck not found, check if it's a public deck
        if (!this.deck && this.decksStore.error) {
          console.log('Trying to fetch as public deck...')
          // Fetch public decks if not already loaded
          if (this.decksStore.publicDecks.length === 0) {
            await this.decksStore.fetchPublicDecks()
          }

          // Find the deck in public decks
          const publicDeck = this.decksStore.publicDecks.find(d => d.id === this.deckId)
          if (publicDeck) {
            // Set the current deck to the found public deck
            this.decksStore.currentDeck = publicDeck

            // Fetch flashcards for this deck
            try {
              const flashcardsResponse = await this.flashcardsStore.fetchFlashcards(this.deckId)
              if (flashcardsResponse) {
                // Add flashcards to the deck
                this.decksStore.currentDeck.flashcards = flashcardsResponse
              }
            } catch (flashcardsError) {
              console.error('Failed to fetch flashcards:', flashcardsError)
            }
          }
        }

        // Only create a study session if the user is authenticated
        if (localStorage.getItem('token')) {
          await this.createStudySession()
        }
      } catch (error) {
        console.error('Failed to fetch deck:', error)
      } finally {
        this.loading = false
      }
    },

    async createStudySession() {
      try {
        this.studySession = await this.studyStore.createStudySession(this.deckId)
      } catch (error) {
        console.error('Failed to create study session:', error)
      }
    },

    toggleAnswer() {
      this.showAnswer = !this.showAnswer
    },

    previousCard() {
      if (this.currentCardIndex > 0) {
        this.currentCardIndex--
        this.showAnswer = false
        this.selectedDifficulty = null
      }
    },

    async nextCard() {
      if (!this.selectedDifficulty) return

      this.saving = true

      try {
        // Record the response
        const isCorrect = this.selectedDifficulty !== 'hard'
        this.cardResponses.push({
          flashcardId: this.currentCard.id,
          difficulty: this.selectedDifficulty,
          isCorrect
        })

        // Update stats
        this.stats[this.selectedDifficulty]++

        // Save study record
        if (this.studySession) {
          try {
            await this.studyStore.createStudyRecord(
              this.studySession.id,
              this.currentCard.id,
              isCorrect
            )
          } catch (error) {
            console.error('Failed to save study record:', error)
          }
        }

        if (this.isLastCard) {
          // End study session
          if (this.studySession) {
            try {
              await this.studyStore.endStudySession(this.studySession.id)
            } catch (error) {
              console.error('Failed to end study session:', error)
            }
          }

          // Show completion dialog
          this.showCompleteDialog = true
        } else {
          // Move to next card
          this.currentCardIndex++
          this.showAnswer = false
          this.selectedDifficulty = null
        }
      } catch (error) {
        console.error('Error during next card operation:', error)
      } finally {
        this.saving = false
      }
    },

    restartStudy() {
      this.currentCardIndex = 0
      this.showAnswer = false
      this.selectedDifficulty = null
      this.showCompleteDialog = false
      this.createStudySession()

      // Reset stats
      this.stats = {
        easy: 0,
        medium: 0,
        hard: 0
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
  perspective: 1000px;
  height: 350px;
  cursor: pointer;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  margin: 20px 0;
  border-radius: 12px;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1) !important;
}

.flashcard-container.flipped {
  transform: rotateY(180deg);
}

.flashcard {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flashcard-front, .flashcard-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 30px;
  border-radius: 12px;
}

.flashcard-front {
  background-color: #e3f2fd;
  border: 2px solid #2196F3;
}

.flashcard-back {
  background-color: #fff8e1;
  border: 2px solid #FFC107;
  transform: rotateY(180deg);
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

.difficulty-buttons {
  display: flex;
  justify-content: center;
}

.difficulty-btn {
  transition: all 0.3s ease;
}

.difficulty-btn:hover {
  transform: translateY(-3px);
}
</style>
