<template>
  <div class="public-decks-view">
    <v-container class="py-8">
      <!-- Page Header -->
      <div class="text-center mb-8 animate-fade-in">
        <v-avatar size="80" class="gradient-info mb-4 animate-pulse">
          <v-icon size="40" color="white">mdi-cards-outline</v-icon>
        </v-avatar>
        <h1 class="text-h3 font-weight-bold mb-2">Public Flashcard Decks</h1>
        <p class="text-h6 text-medium-emphasis">Discover and study community-created flashcard collections</p>
      </div>

      <v-row justify="center">
        <v-col cols="12" md="10" lg="8">
          <!-- Search and Filter Section -->
          <v-card class="modern-card mb-6 animate-slide-in-up">
            <v-card-text class="pa-6">
              <v-text-field
                v-model="search"
                prepend-inner-icon="mdi-magnify"
                label="Search public decks..."
                variant="outlined"
                class="modern-input"
                hide-details
                clearable
              ></v-text-field>
            </v-card-text>
          </v-card>

          <!-- Error Alert -->
          <v-alert
            v-if="decksStore.error"
            type="error"
            variant="tonal"
            class="modern-card mb-6 animate-slide-in-up animate-delay-200"
            closable
            @click:close="decksStore.clearError()"
          >
            {{ decksStore.error }}
          </v-alert>

          <!-- Loading State -->
          <div v-if="decksStore.loading" class="text-center py-12 animate-fade-in">
            <v-progress-circular
              color="primary"
              size="64"
              width="6"
              indeterminate
              class="mb-4"
            ></v-progress-circular>
            <p class="text-h6 text-medium-emphasis">Loading public decks...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="filteredDecks.length === 0" class="text-center py-12 animate-fade-in">
            <v-avatar size="120" class="gradient-secondary mb-6 animate-pulse">
              <v-icon size="60" color="white">mdi-cards-outline</v-icon>
            </v-avatar>
            <h3 class="text-h4 font-weight-bold mb-4">No Public Decks Found</h3>
            <p class="text-h6 text-medium-emphasis mb-6">
              {{ search ? 'Try adjusting your search terms' : 'Be the first to create a public deck!' }}
            </p>
            <v-btn
              class="modern-btn"
              color="primary"
              size="large"
              @click="goToMain"
              prepend-icon="mdi-arrow-left"
            >
              Back to Main
            </v-btn>
          </div>

          <!-- Decks Grid -->
          <div v-else class="animate-slide-in-up animate-delay-400">
            <v-row>
              <v-col
                v-for="(deck, index) in filteredDecks"
                :key="deck.id"
                cols="12"
                sm="6"
                md="4"
                lg="4"
                class="animate-scale-in"
                :class="`animate-delay-${200 + (index % 3) * 100}`"
              >
                <v-card
                  class="modern-card deck-card h-100"
                  @click="viewDeck(deck)"
                  hover
                >
                  <!-- Card Header -->
                  <div class="gradient-primary pa-4">
                    <div class="d-flex align-center justify-space-between">
                      <v-avatar size="48" class="gradient-secondary">
                        <v-icon size="24" color="white">mdi-cards-outline</v-icon>
                      </v-avatar>
                      <v-chip
                        class="gradient-success text-white"
                        size="small"
                      >
                        <v-icon start size="16">mdi-earth</v-icon>
                        Public
                      </v-chip>
                    </div>
                  </div>

                  <!-- Card Content -->
                  <v-card-text class="pa-6">
                    <h3 class="text-h6 font-weight-bold mb-3 text-white">{{ deck.title }}</h3>
                    <p v-if="deck.description" class="text-body-2 text-medium-emphasis mb-4 line-clamp-2">
                      {{ deck.description }}
                    </p>

                    <!-- Deck Stats -->
                    <div class="d-flex align-center justify-space-between mb-4">
                      <div class="d-flex align-center">
                        <v-icon size="16" class="text-medium-emphasis mr-1">mdi-card-multiple</v-icon>
                        <span class="text-caption text-medium-emphasis">{{ deck.flashcards?.length || 0 }} cards</span>
                      </div>
                      <div class="d-flex align-center">
                        <v-icon size="16" class="text-medium-emphasis mr-1">mdi-account</v-icon>
                        <span class="text-caption text-medium-emphasis">{{ deck.owner?.username || 'Unknown' }}</span>
                      </div>
                    </div>

                    <div class="text-caption text-medium-emphasis">
                      Created: {{ formatDate(deck.created_at) }}
                    </div>
                  </v-card-text>

                  <!-- Card Actions -->
                  <v-card-actions class="pa-6 pt-0">
                    <v-btn
                      class="modern-btn"
                      color="primary"
                      variant="flat"
                      @click.stop="studyDeck(deck)"
                      prepend-icon="mdi-book-open-variant"
                      block
                    >
                      Study Now
                    </v-btn>
                  </v-card-actions>

                  <!-- Clone Button -->
                  <v-btn
                    v-if="isAuthenticated"
                    class="clone-btn"
                    color="info"
                    variant="flat"
                    size="small"
                    @click.stop="cloneDeck(deck)"
                    icon="mdi-content-copy"
                  ></v-btn>
                </v-card>
              </v-col>
            </v-row>
          </div>

          <!-- Back to Main Button -->
          <div class="text-center mt-8 animate-fade-in animate-delay-600">
            <v-btn
              class="modern-btn"
              color="secondary"
              size="large"
              @click="goToMain"
              prepend-icon="mdi-arrow-left"
            >
              Back to Main
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-container>

    <!-- Clone Deck Dialog -->
    <v-dialog
      v-model="showCloneDialog"
      max-width="500px"
      class="glass-effect"
    >
      <v-card class="modern-card">
        <v-card-title class="pa-6 pb-4">
          <div class="d-flex align-center">
            <v-avatar size="48" class="gradient-info mr-4">
              <v-icon size="24" color="white">mdi-content-copy</v-icon>
            </v-avatar>
            <div>
              <h3 class="text-h5 font-weight-bold">Clone Deck</h3>
              <p class="text-caption text-medium-emphasis mb-0">Add this deck to your collection</p>
            </div>
          </div>
        </v-card-title>

        <v-card-text class="pa-6 pt-0">
          <p class="text-body-2 mb-6">
            You are about to clone <strong>{{ selectedDeck?.title }}</strong> to your personal collection.
            Customize the details below:
          </p>

          <v-form ref="cloneForm">
            <v-text-field
              v-model="cloneForm.title"
              label="Deck Title"
              variant="outlined"
              class="mb-4"
              prepend-inner-icon="mdi-card-text"
              :rules="[v => !!v || 'Title is required']"
            ></v-text-field>

            <v-textarea
              v-model="cloneForm.description"
              label="Description"
              variant="outlined"
              rows="3"
              class="mb-4"
              prepend-inner-icon="mdi-text"
            ></v-textarea>

            <v-switch
              v-model="cloneForm.is_public"
              label="Make this deck public"
              color="primary"
              class="mb-2"
            ></v-switch>
          </v-form>
        </v-card-text>

        <v-card-actions class="pa-6 pt-0">
          <v-spacer></v-spacer>
          <v-btn
            class="modern-btn"
            color="grey"
            variant="outlined"
            @click="showCloneDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            class="modern-btn ml-2"
            color="primary"
            @click="confirmClone"
            :loading="cloning"
            prepend-icon="mdi-content-copy"
          >
            Clone Deck
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
.public-decks-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.v-theme--dark .public-decks-view {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.deck-card {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.deck-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.deck-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.deck-card:hover::before {
  opacity: 1;
}

.clone-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  opacity: 0;
  transition: all 0.3s ease;
}

.deck-card:hover .clone-btn {
  opacity: 1;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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

.animate-delay-200 { animation-delay: 0.2s; }
.animate-delay-400 { animation-delay: 0.4s; }
.animate-delay-600 { animation-delay: 0.6s; }

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
</style>
