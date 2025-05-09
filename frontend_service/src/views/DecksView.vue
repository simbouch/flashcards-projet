<template>
  <div class="decks">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="text-h5">
              My Flashcard Decks
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                @click="showCreateDialog = true"
              >
                <v-icon left>mdi-plus</v-icon>
                Create Deck
              </v-btn>
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
              
              <v-row v-else-if="decksStore.decks.length === 0">
                <v-col cols="12" class="text-center">
                  <p>You don't have any flashcard decks yet.</p>
                  <v-btn
                    color="primary"
                    @click="showCreateDialog = true"
                    class="mt-2"
                  >
                    Create Your First Deck
                  </v-btn>
                </v-col>
              </v-row>
              
              <v-row v-else>
                <v-col
                  v-for="deck in decksStore.decks"
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
                      <div class="text-caption">
                        Created: {{ formatDate(deck.created_at) }}
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
                        icon
                        @click.stop="editDeck(deck)"
                      >
                        <v-icon>mdi-pencil</v-icon>
                      </v-btn>
                      
                      <v-btn
                        icon
                        @click.stop="deleteDeck(deck)"
                      >
                        <v-icon>mdi-delete</v-icon>
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-col>
              </v-row>
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
