<template>
  <div class="decks">
    <v-container class="py-8">
      <!-- Header Section -->
      <div class="header-section mb-8 animate-fade-in">
        <div class="d-flex align-center justify-space-between flex-wrap gap-4">
          <div>
            <h1 class="text-h3 font-weight-bold gradient-text mb-2">My Flashcard Decks</h1>
            <p class="text-h6 text-medium-emphasis">
              Manage and study your personalized flashcard collections
            </p>
          </div>
          <div class="d-flex gap-2">
            <v-btn
              class="modern-btn-primary"
              @click="showCreateDialog = true"
              size="large"
              prepend-icon="mdi-plus"
            >
              Create Deck
            </v-btn>
            <v-btn
              variant="outlined"
              class="modern-btn"
              @click="goToMain"
              size="large"
              prepend-icon="mdi-arrow-left"
            >
              Back to Main
            </v-btn>
          </div>
        </div>
      </div>

      <!-- Content Section -->
      <v-row>
        <v-col cols="12">
          <v-card class="modern-card-elevated">
            <v-card-text class="pa-6">

              <!-- Error Alert -->
              <v-alert
                v-if="decksStore.error"
                type="error"
                variant="tonal"
                class="mb-6 modern-card"
                closable
                @click:close="decksStore.clearError()"
              >
                <template v-slot:prepend>
                  <v-icon>mdi-alert-circle</v-icon>
                </template>
                {{ decksStore.error }}
              </v-alert>

              <!-- Loading State -->
              <div v-if="decksStore.loading" class="text-center py-12 animate-fade-in">
                <v-progress-circular
                  indeterminate
                  color="primary"
                  size="64"
                  width="6"
                  class="mb-4"
                ></v-progress-circular>
                <p class="text-h6 text-medium-emphasis">Loading your decks...</p>
              </div>

              <!-- Empty State -->
              <div v-else-if="decksStore.decks.length === 0" class="empty-state text-center py-12 animate-scale-in">
                <v-avatar size="120" class="gradient-primary mb-6 animate-pulse">
                  <v-icon size="60" color="white">mdi-cards-outline</v-icon>
                </v-avatar>
                <h3 class="text-h4 font-weight-bold mb-4">No Decks Yet</h3>
                <p class="text-h6 text-medium-emphasis mb-6 max-width-400 mx-auto">
                  Start your learning journey by creating your first flashcard deck!
                </p>
                <v-btn
                  class="modern-btn-primary"
                  @click="showCreateDialog = true"
                  size="large"
                  prepend-icon="mdi-plus"
                >
                  Create Your First Deck
                </v-btn>
              </div>

              <!-- Decks Grid -->
              <div v-else class="decks-grid">
                <v-row>
                  <v-col
                    v-for="(deck, index) in decksStore.decks"
                    :key="deck.id"
                    cols="12"
                    sm="6"
                    lg="4"
                    class="animate-scale-in"
                    :style="{ animationDelay: `${index * 0.1}s` }"
                  >
                    <v-card
                      class="deck-card modern-card-elevated"
                      @click="viewDeck(deck)"
                      hover
                    >
                      <!-- Card Header -->
                      <div class="card-gradient-overlay"></div>
                      <v-card-title class="pa-4 pb-2">
                        <div class="d-flex align-center justify-space-between w-100">
                          <h3 class="text-h6 font-weight-bold text-truncate">{{ deck.title }}</h3>
                          <v-chip
                            v-if="deck.is_public"
                            color="success"
                            size="small"
                            variant="flat"
                          >
                            <v-icon start size="16">mdi-earth</v-icon>
                            Public
                          </v-chip>
                        </div>
                      </v-card-title>

                      <!-- Card Content -->
                      <v-card-text class="pa-4 pt-0">
                        <p v-if="deck.description" class="text-body-2 text-medium-emphasis mb-3 line-clamp-2">
                          {{ deck.description }}
                        </p>
                        <div class="d-flex align-center text-caption text-medium-emphasis">
                          <v-icon size="16" class="mr-1">mdi-calendar</v-icon>
                          Created {{ formatDate(deck.created_at) }}
                        </div>
                      </v-card-text>

                      <!-- Card Actions -->
                      <v-card-actions class="pa-4 pt-0">
                        <v-btn
                          variant="flat"
                          color="primary"
                          class="modern-btn flex-grow-1"
                          @click.stop="studyDeck(deck)"
                          prepend-icon="mdi-book-open-variant"
                        >
                          Study
                        </v-btn>

                        <v-menu offset-y>
                          <template v-slot:activator="{ props }">
                            <v-btn
                              icon="mdi-dots-vertical"
                              variant="text"
                              v-bind="props"
                              @click.stop
                            ></v-btn>
                          </template>
                          <v-list class="modern-card">
                            <v-list-item @click="editDeck(deck)" class="modern-btn">
                              <template v-slot:prepend>
                                <v-icon>mdi-pencil</v-icon>
                              </template>
                              <v-list-item-title>Edit</v-list-item-title>
                            </v-list-item>
                            <v-list-item @click="deleteDeck(deck)" class="modern-btn text-error">
                              <template v-slot:prepend>
                                <v-icon>mdi-delete</v-icon>
                              </template>
                              <v-list-item-title>Delete</v-list-item-title>
                            </v-list-item>
                          </v-list>
                        </v-menu>
                      </v-card-actions>
                    </v-card>
                  </v-col>
                </v-row>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Create/Edit Deck Dialog -->
    <v-dialog
      v-model="showCreateDialog"
      max-width="500px"
    >
      <v-card>
        <v-card-title class="text-h5">
          {{ editMode ? 'Edit Deck' : 'Create New Deck' }}
        </v-card-title>

        <v-card-text>
          <v-form ref="deckForm">
            <v-text-field
              v-model="deckForm.title"
              label="Deck Title"
              required
              :rules="[v => !!v || 'Title is required']"
            ></v-text-field>

            <v-textarea
              v-model="deckForm.description"
              label="Description"
              rows="3"
            ></v-textarea>

            <v-switch
              v-model="deckForm.is_public"
              label="Make this deck public"
              color="primary"
            ></v-switch>

            <v-select
              v-if="!editMode"
              v-model="deckForm.document_id"
              :items="documents"
              item-text="filename"
              item-value="id"
              label="Generate from Document (Optional)"
              clearable
            ></v-select>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="showCreateDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            @click="saveDeck"
            :loading="saving"
          >
            {{ editMode ? 'Update' : 'Create' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog
      v-model="showDeleteDialog"
      max-width="400px"
    >
      <v-card>
        <v-card-title class="text-h5">
          Confirm Delete
        </v-card-title>

        <v-card-text>
          Are you sure you want to delete the deck
          <strong>{{ selectedDeck?.title }}</strong>?
          This will also delete all flashcards in this deck.
          This action cannot be undone.
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="showDeleteDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            @click="confirmDelete"
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
import { useDocumentsStore } from '../store/documents'

export default {
  name: 'DecksView',
  data() {
    return {
      decksStore: useDecksStore(),
      documentsStore: useDocumentsStore(),
      showCreateDialog: false,
      showDeleteDialog: false,
      editMode: false,
      deckForm: {
        title: '',
        description: '',
        is_public: false,
        document_id: null
      },
      selectedDeck: null,
      saving: false,
      deleting: false
    }
  },
  computed: {
    documents() {
      return this.documentsStore.documents.map(doc => ({
        id: doc.id,
        filename: doc.filename
      }))
    }
  },
  created() {
    this.fetchDecks()
    this.fetchDocuments()
  },
  methods: {
    async fetchDecks() {
      await this.decksStore.fetchDecks()
    },

    async fetchDocuments() {
      await this.documentsStore.fetchDocuments()
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

    editDeck(deck) {
      this.editMode = true
      this.selectedDeck = deck
      this.deckForm = {
        title: deck.title,
        description: deck.description || '',
        is_public: deck.is_public
      }
      this.showCreateDialog = true
    },

    deleteDeck(deck) {
      this.selectedDeck = deck
      this.showDeleteDialog = true
    },

    resetForm() {
      this.editMode = false
      this.selectedDeck = null
      this.deckForm = {
        title: '',
        description: '',
        is_public: false,
        document_id: null
      }
      if (this.$refs.deckForm) {
        this.$refs.deckForm.reset()
      }
    },

    async saveDeck() {
      // Validate form
      if (this.$refs.deckForm.validate()) {
        this.saving = true

        try {
          if (this.editMode) {
            // Update existing deck
            await this.decksStore.updateDeck(this.selectedDeck.id, this.deckForm)
          } else {
            // Create new deck
            await this.decksStore.createDeck(this.deckForm)
          }

          this.showCreateDialog = false
          this.resetForm()
        } catch (error) {
          console.error('Failed to save deck:', error)
        } finally {
          this.saving = false
        }
      }
    },

    async confirmDelete() {
      if (!this.selectedDeck) return

      this.deleting = true

      try {
        await this.decksStore.deleteDeck(this.selectedDeck.id)
        this.showDeleteDialog = false
      } catch (error) {
        console.error('Failed to delete deck:', error)
      } finally {
        this.deleting = false
      }
    },

    goToMain() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
/* Header Section */
.header-section {
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

/* Empty State */
.empty-state {
  padding: 4rem 2rem;
}

.max-width-400 {
  max-width: 400px;
}

/* Deck Cards */
.deck-card {
  height: 100%;
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.deck-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: var(--shadow-2xl);
}

.card-gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--gradient-primary);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Decks Grid */
.decks-grid {
  animation: fadeIn 0.6s ease-out;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-section {
    padding: 1.5rem;
    text-align: center;
  }

  .header-section .d-flex {
    flex-direction: column;
    gap: 1rem;
  }

  .empty-state {
    padding: 2rem 1rem;
  }

  .deck-card {
    margin-bottom: 1rem;
  }
}

/* Dark mode adjustments */
.v-theme--dark .header-section {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
}

/* Animation improvements */
.deck-card .v-card-actions .v-btn {
  transition: all var(--transition-fast);
}

.deck-card:hover .v-card-actions .v-btn {
  transform: translateY(-2px);
}

/* Menu styling */
.v-menu .v-list {
  min-width: 150px;
}

.v-menu .v-list-item {
  transition: all var(--transition-fast);
}

.v-menu .v-list-item:hover {
  transform: translateX(5px);
}
</style>
