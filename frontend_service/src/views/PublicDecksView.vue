<template>
  <div class="public-decks">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="text-h5">
              Public Flashcard Decks
              <v-spacer></v-spacer>
              <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                hide-details
                class="ml-4"
                style="max-width: 300px"
              ></v-text-field>
            </v-card-title>

            <v-card-text>
              <v-alert
                v-if="decksStore.error"
                type="error"
                dismissible
                @click:close="decksStore.clearError()"
              >
                {{ decksStore.error }}
              </v-alert>

              <v-row v-if="decksStore.loading">
                <v-col cols="12" class="text-center">
                  <v-progress-circular
                    indeterminate
                    color="primary"
                  ></v-progress-circular>
                </v-col>
              </v-row>

              <v-row v-else-if="filteredDecks.length === 0">
                <v-col cols="12" class="text-center">
                  <p>No public decks found.</p>
                </v-col>
              </v-row>

              <v-row v-else>
                <v-col
                  v-for="deck in filteredDecks"
                  :key="deck.id"
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-card
                    class="deck-card"
                    outlined
                    @click="viewDeck(deck)"
                  >
                    <v-card-title>
                      {{ deck.title }}
                      <v-chip
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
                      <div class="text-caption">
                        Created: {{ formatDate(deck.created_at) }}
                      </div>
                      <div class="text-caption">
                        By: {{ deck.owner ? deck.owner.username : 'Unknown' }}
                      </div>
                    </v-card-text>

                    <v-card-actions>
                      <v-btn
                        text
                        color="primary"
                        @click.stop="studyDeck(deck)"
                      >
                        <v-icon left>mdi-book-open-variant</v-icon>
                        Study
                      </v-btn>

                      <v-spacer></v-spacer>

                      <v-btn
                        v-if="isAuthenticated"
                        icon
                        @click.stop="cloneDeck(deck)"
                        title="Clone to My Decks"
                      >
                        <v-icon>mdi-content-copy</v-icon>
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions>
              <v-btn
                color="secondary"
                @click="goToMain"
              >
                <v-icon left>mdi-arrow-left</v-icon>
                Back to Main
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Clone Deck Dialog -->
    <v-dialog
      v-model="showCloneDialog"
      max-width="500px"
    >
      <v-card>
        <v-card-title class="text-h5">
          Clone Deck
        </v-card-title>

        <v-card-text>
          <p>
            You are about to clone the deck <strong>{{ selectedDeck?.title }}</strong> to your personal collection.
            You can customize the title and description below.
          </p>

          <v-form ref="cloneForm">
            <v-text-field
              v-model="cloneForm.title"
              label="Deck Title"
              required
              :rules="[v => !!v || 'Title is required']"
            ></v-text-field>

            <v-textarea
              v-model="cloneForm.description"
              label="Description"
              rows="3"
            ></v-textarea>

            <v-switch
              v-model="cloneForm.is_public"
              label="Make this deck public"
              color="primary"
            ></v-switch>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="showCloneDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            @click="confirmClone"
            :loading="cloning"
          >
            Clone
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { useDecksStore } from '../store/decks'
import { useAuthStore } from '../store/auth'
import { useFlashcardsStore } from '../store/flashcards'
import { mapState } from 'pinia'

export default {
  name: 'PublicDecksView',
  data() {
    return {
      decksStore: useDecksStore(),
      flashcardsStore: useFlashcardsStore(),
      search: '',
      showCloneDialog: false,
      selectedDeck: null,
      cloneForm: {
        title: '',
        description: '',
        is_public: false
      },
      cloning: false
    }
  },
  computed: {
    ...mapState(useAuthStore, ['isAuthenticated']),

    filteredDecks() {
      if (!this.search) {
        return this.decksStore.publicDecks
      }

      const searchLower = this.search.toLowerCase()
      return this.decksStore.publicDecks.filter(deck =>
        deck.title.toLowerCase().includes(searchLower) ||
        (deck.description && deck.description.toLowerCase().includes(searchLower))
      )
    }
  },
  created() {
    this.fetchPublicDecks()
  },
  methods: {
    async fetchPublicDecks() {
      await this.decksStore.fetchPublicDecks()
    },

    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    },

    viewDeck(deck) {
      this.$router.push(`/decks/${deck.id}`)
    },

    studyDeck(deck) {
      this.$router.push(`/study/${deck.id}`)
    },

    cloneDeck(deck) {
      if (!this.isAuthenticated) {
        this.$router.push('/login')
        return
      }

      this.selectedDeck = deck
      this.cloneForm = {
        title: `Copy of ${deck.title}`,
        description: deck.description || '',
        is_public: false
      }
      this.showCloneDialog = true
    },

    async confirmClone() {
      if (!this.selectedDeck || !this.$refs.cloneForm.validate()) return

      this.cloning = true

      try {
        // Create a new deck
        const newDeck = await this.decksStore.createDeck(this.cloneForm)

        if (newDeck) {
          // Fetch flashcards from the original deck
          await this.flashcardsStore.fetchFlashcards(this.selectedDeck.id)

          // Clone each flashcard to the new deck
          for (const card of this.flashcardsStore.flashcards) {
            await this.flashcardsStore.createFlashcard({
              question: card.question,
              answer: card.answer,
              deck_id: newDeck.id
            })
          }

          // Show success message and redirect to the new deck
          this.showCloneDialog = false
          this.$router.push(`/decks/${newDeck.id}`)
        }
      } catch (error) {
        console.error('Failed to clone deck:', error)
      } finally {
        this.cloning = false
      }
    },

    goToMain() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.deck-card {
  height: 100%;
  cursor: pointer;
  transition: transform 0.2s;
}

.deck-card:hover {
  transform: translateY(-5px);
}
</style>
