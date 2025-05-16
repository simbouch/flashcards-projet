<template>
  <div class="study-history">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="text-h5">
              Study History
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                text
                @click="$router.push('/decks')"
              >
                <v-icon left>mdi-arrow-left</v-icon>
                Back to Decks
              </v-btn>
            </v-card-title>

            <v-card-text>
              <v-alert
                v-if="studyStore.error"
                type="error"
                dismissible
                @click:close="studyStore.clearError()"
              >
                {{ studyStore.error }}
              </v-alert>

              <div v-if="studyStore.loading" class="text-center my-5">
                <v-progress-circular
                  indeterminate
                  color="primary"
                  size="64"
                ></v-progress-circular>
                <div class="mt-3">Loading study history...</div>
              </div>

              <div v-else-if="studyStore.sessions.length === 0" class="text-center my-5">
                <v-icon size="64" color="grey lighten-1">mdi-book-open-variant</v-icon>
                <div class="text-h6 mt-3 grey--text text--darken-1">No study sessions found</div>
                <div class="text-body-2 grey--text">Start studying a deck to track your progress</div>
                <v-btn
                  color="primary"
                  class="mt-4"
                  to="/decks"
                >
                  Browse Decks
                </v-btn>
              </div>

              <div v-else>
                <v-expansion-panels>
                  <v-expansion-panel
                    v-for="session in sortedSessions"
                    :key="session.id"
                  >
                    <v-expansion-panel-header>
                      <div class="d-flex align-center">
                        <div>
                          <div class="text-subtitle-1">
                            {{ getDeckTitle(session.deck_id) }}
                          </div>
                          <div class="text-caption">
                            {{ formatDate(session.created_at) }}
                            <v-chip
                              x-small
                              :color="session.ended_at ? 'success' : 'warning'"
                              class="ml-2"
                            >
                              {{ session.ended_at ? 'Completed' : 'In Progress' }}
                            </v-chip>
                          </div>
                        </div>
                        <v-spacer></v-spacer>
                        <div class="text-right">
                          <div class="text-subtitle-2">
                            {{ getSessionStats(session) }}
                          </div>
                          <div class="text-caption">
                            {{ session.ended_at ? formatDuration(session.created_at, session.ended_at) : 'Ongoing' }}
                          </div>
                        </div>
                      </div>
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <v-btn
                        small
                        color="primary"
                        text
                        class="mb-3"
                        @click="loadSessionRecords(session.id)"
                        :loading="loadingRecords === session.id"
                      >
                        <v-icon left small>mdi-refresh</v-icon>
                        Refresh Records
                      </v-btn>

                      <div v-if="!sessionRecords[session.id] || sessionRecords[session.id].length === 0" class="text-center my-3">
                        <div class="text-body-2 grey--text">No records found for this session</div>
                      </div>

                      <v-simple-table v-else>
                        <template v-slot:default>
                          <thead>
                            <tr>
                              <th>Flashcard</th>
                              <th>Result</th>
                              <th>Time</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="record in sessionRecords[session.id]" :key="record.id">
                              <td>{{ getFlashcardQuestion(record.flashcard_id) }}</td>
                              <td>
                                <v-chip
                                  x-small
                                  :color="record.is_correct ? 'success' : 'error'"
                                >
                                  {{ record.is_correct ? 'Correct' : 'Incorrect' }}
                                </v-chip>
                              </td>
                              <td>{{ formatDate(record.created_at) }}</td>
                            </tr>
                          </tbody>
                        </template>
                      </v-simple-table>
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-expansion-panels>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { useStudyStore } from '../store/study'
import { useDecksStore } from '../store/decks'
import { useFlashcardsStore } from '../store/flashcards'

export default {
  name: 'StudyHistoryView',
  data() {
    return {
      studyStore: useStudyStore(),
      decksStore: useDecksStore(),
      flashcardsStore: useFlashcardsStore(),
      sessionRecords: {},
      loadingRecords: null,
      deckCache: {},
      flashcardCache: {}
    }
  },
  computed: {
    sortedSessions() {
      return [...this.studyStore.sessions].sort((a, b) => {
        return new Date(b.created_at) - new Date(a.created_at)
      })
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      // Load sessions
      await this.studyStore.fetchStudySessions()
      
      // Load decks if not already loaded
      if (this.decksStore.decks.length === 0) {
        await this.decksStore.fetchDecks()
      }
      
      // Load public decks if not already loaded
      if (this.decksStore.publicDecks.length === 0) {
        await this.decksStore.fetchPublicDecks()
      }
      
      // Load records for each session
      for (const session of this.studyStore.sessions) {
        await this.loadSessionRecords(session.id)
      }
    },
    
    async loadSessionRecords(sessionId) {
      this.loadingRecords = sessionId
      try {
        await this.studyStore.fetchStudyRecords(sessionId)
        this.sessionRecords[sessionId] = this.studyStore.records
        
        // Preload flashcards for this session if needed
        const deckId = this.studyStore.sessions.find(s => s.id === sessionId)?.deck_id
        if (deckId && !this.deckCache[deckId]) {
          const flashcards = await this.flashcardsStore.fetchFlashcards(deckId)
          if (flashcards) {
            // Cache flashcards by ID for quick lookup
            flashcards.forEach(card => {
              this.flashcardCache[card.id] = card
            })
            this.deckCache[deckId] = true
          }
        }
      } finally {
        this.loadingRecords = null
      }
    },
    
    getDeckTitle(deckId) {
      // Check user decks
      const userDeck = this.decksStore.decks.find(d => d.id === deckId)
      if (userDeck) return userDeck.title
      
      // Check public decks
      const publicDeck = this.decksStore.publicDecks.find(d => d.id === deckId)
      if (publicDeck) return publicDeck.title
      
      return `Deck ${deckId.substring(0, 8)}...`
    },
    
    getFlashcardQuestion(flashcardId) {
      return this.flashcardCache[flashcardId]?.question || `Flashcard ${flashcardId.substring(0, 8)}...`
    },
    
    getSessionStats(session) {
      const records = this.sessionRecords[session.id] || []
      const correctCount = records.filter(r => r.is_correct).length
      const totalCount = records.length
      
      if (totalCount === 0) return 'No cards studied'
      
      const percentage = Math.round((correctCount / totalCount) * 100)
      return `${correctCount}/${totalCount} correct (${percentage}%)`
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    
    formatDuration(startString, endString) {
      if (!startString || !endString) return 'N/A'
      
      const start = new Date(startString)
      const end = new Date(endString)
      const durationMs = end - start
      
      // Format as minutes and seconds
      const minutes = Math.floor(durationMs / 60000)
      const seconds = Math.floor((durationMs % 60000) / 1000)
      
      if (minutes === 0) {
        return `${seconds} seconds`
      } else {
        return `${minutes} min ${seconds} sec`
      }
    }
  }
}
</script>

<style scoped>
.study-history {
  margin-bottom: 30px;
}
</style>
