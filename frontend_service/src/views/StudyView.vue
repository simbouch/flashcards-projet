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
                      <div class="text-h6 mb-2">Question:</div>
                      <div class="text-body-1">{{ currentCard.question }}</div>
                      <div class="text-caption text-center mt-4">
                        (Click to see answer)
                      </div>
                    </div>
                    
                    <div class="flashcard-back">
                      <div class="text-h6 mb-2">Answer:</div>
                      <div class="text-body-1">{{ currentCard.answer }}</div>
                      <div class="text-caption text-center mt-4">
                        (Click to see question)
                      </div>
                    </div>
                  </div>
                </v-card>
                
                <div class="text-center mt-6" v-if="showAnswer">
                  <div class="text-body-1 mb-2">How well did you know this?</div>
                  <v-btn-toggle
                    v-model="selectedDifficulty"
                    mandatory
                    class="difficulty-buttons"
                  >
                    <v-btn
                      value="hard"
                      color="red"
                      outlined
                      class="mx-1"
                    >
                      Hard
                    </v-btn>
                    
                    <v-btn
                      value="medium"
                      color="orange"
                      outlined
                      class="mx-1"
                    >
                      Medium
                    </v-btn>
                    
                    <v-btn
                      value="easy"
                      color="green"
                      outlined
                      class="mx-1"
                    >
                      Easy
                    </v-btn>
                  </v-btn-toggle>
                </div>
              </v-card-text>
              
              <v-card-actions>
                <v-btn
                  color="grey darken-1"
                  text
                  @click="previousCard"
                  :disabled="currentCardIndex === 0 || !showAnswer"
                >
                  <v-icon left>mdi-arrow-left</v-icon>
                  Previous
                </v-btn>
                
                <v-spacer></v-spacer>
                
                <v-btn
                  color="primary"
                  @click="nextCard"
                  :disabled="!showAnswer || !selectedDifficulty"
                >
                  {{ isLastCard ? 'Finish' : 'Next' }}
                  <v-icon right>mdi-arrow-right</v-icon>
                </v-btn>
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
        await this.decksStore.fetchDeck(this.deckId)
        await this.createStudySession()
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
  height: 300px;
  cursor: pointer;
  transition: transform 0.6s;
  transform-style: preserve-3d;
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
  padding: 20px;
}

.flashcard-back {
  transform: rotateY(180deg);
}

.difficulty-buttons {
  display: flex;
  justify-content: center;
}
</style>
