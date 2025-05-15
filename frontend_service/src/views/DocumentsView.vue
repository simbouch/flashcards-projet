<template>
  <div class="documents">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="text-h5">
              My Documents
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                @click="showUploadDialog = true"
              >
                <v-icon left>mdi-upload</v-icon>
                Upload Document
              </v-btn>
            </v-card-title>

            <v-card-text>
              <v-alert
                v-if="documentsStore.error"
                type="error"
                dismissible
                @click:close="documentsStore.clearError()"
              >
                {{ documentsStore.error }}
              </v-alert>

              <v-data-table
                :headers="headers"
                :items="documentsStore.documents"
                :loading="documentsStore.loading"
                :items-per-page="10"
                class="elevation-1"
                :no-data-text="documentsStore.loading ? 'Loading documents...' : 'No documents found'"
              >
                <template v-slot:item.status="{ item }">
                  <v-chip
                    :color="getStatusColor(item.status)"
                    small
                  >
                    {{ formatStatus(item.status) }}
                  </v-chip>
                </template>

                <template v-slot:item.created_at="{ item }">
                  {{ formatDate(item.created_at) }}
                </template>

                <template v-slot:item.actions="{ item }">
                  <v-btn
                    color="primary"
                    small
                    @click="viewDocument(item)"
                    :disabled="!isProcessingComplete(item)"
                    class="mr-2"
                  >
                    <v-icon left>mdi-eye</v-icon>
                    View Document
                  </v-btn>

                  <v-btn
                    color="error"
                    small
                    @click="deleteDocument(item)"
                    class="ml-2"
                  >
                    <v-icon left>mdi-delete</v-icon>
                    Delete
                  </v-btn>
                </template>
              </v-data-table>
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

    <!-- Upload Dialog -->
    <v-dialog
      v-model="showUploadDialog"
      max-width="500px"
    >
      <v-card>
        <v-card-title class="text-h5">
          Upload Document
        </v-card-title>

        <v-card-text>
          <v-file-input
            v-model="fileToUpload"
            label="Select Document"
            accept="image/jpeg,image/png,application/pdf"
            prepend-icon="mdi-file-document"
            show-size
            :rules="[v => !!v || 'Please select a file to upload']"
          ></v-file-input>

          <v-alert
            v-if="uploadError"
            type="error"
            dismissible
            @click:close="uploadError = null"
          >
            {{ uploadError }}
          </v-alert>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="showUploadDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            @click="uploadDocument"
            :loading="uploading"
            :disabled="!fileToUpload || uploading"
          >
            Upload
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- View Document Dialog -->
    <v-dialog
      v-model="showViewDialog"
      max-width="800px"
    >
      <v-card v-if="selectedDocument">
        <v-card-title class="text-h5">
          {{ selectedDocument.filename }}
        </v-card-title>

        <v-card-text>
          <v-tabs v-model="activeTab">
            <v-tab>Document Info</v-tab>
            <v-tab>Extracted Text</v-tab>
            <v-tab>Generated Flashcards</v-tab>
          </v-tabs>

          <v-tabs-items v-model="activeTab">
            <v-tab-item>
              <v-list>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Filename</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedDocument.filename }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>

                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Status</v-list-item-title>
                    <v-list-item-subtitle>
                      <v-chip
                        :color="getStatusColor(selectedDocument.status)"
                        small
                      >
                        {{ formatStatus(selectedDocument.status) }}
                      </v-chip>
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>

                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Uploaded</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDate(selectedDocument.created_at) }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>

                <v-list-item v-if="selectedDocument.error_message">
                  <v-list-item-content>
                    <v-list-item-title>Error</v-list-item-title>
                    <v-list-item-subtitle class="text-error">{{ selectedDocument.error_message }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-tab-item>

            <v-tab-item>
              <div v-if="extractedText" class="pa-4">
                <pre class="extracted-text">{{ extractedText.content }}</pre>
              </div>
              <div v-else class="pa-4 text-center">
                <v-progress-circular
                  v-if="loadingText"
                  indeterminate
                  color="primary"
                ></v-progress-circular>
                <p v-else>No text extracted yet.</p>
              </div>
            </v-tab-item>

            <v-tab-item>
              <div v-if="flashcards && flashcards.length > 0" class="pa-4">
                <v-card
                  v-for="(card, index) in flashcards"
                  :key="index"
                  class="mb-4"
                  outlined
                >
                  <v-card-title>{{ card.question }}</v-card-title>
                  <v-card-text>{{ card.answer }}</v-card-text>
                </v-card>
              </div>
              <div v-else class="pa-4 text-center">
                <v-progress-circular
                  v-if="loadingFlashcards"
                  indeterminate
                  color="primary"
                ></v-progress-circular>
                <p v-else>No flashcards generated yet.</p>
              </div>
            </v-tab-item>
          </v-tabs-items>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            text
            @click="showViewDialog = false"
          >
            Close
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
          Are you sure you want to delete this document?
          <strong>{{ selectedDocument?.filename }}</strong>
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
import { useDocumentsStore } from '../store/documents'
import { useFlashcardsStore } from '../store/flashcards'
import { documentsAPI } from '../api'

export default {
  name: 'DocumentsView',
  data() {
    return {
      documentsStore: useDocumentsStore(),
      flashcardsStore: useFlashcardsStore(),
      headers: [
        { text: 'Filename', value: 'filename' },
        { text: 'Status', value: 'status' },
        { text: 'Uploaded', value: 'created_at' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      showUploadDialog: false,
      showViewDialog: false,
      showDeleteDialog: false,
      fileToUpload: null,
      uploading: false,
      uploadError: null,
      selectedDocument: null,
      activeTab: 0,
      extractedText: null,
      loadingText: false,
      flashcards: [],
      loadingFlashcards: false,
      deleting: false
    }
  },
  created() {
    this.fetchDocuments()
  },
  methods: {
    async fetchDocuments() {
      await this.documentsStore.fetchDocuments()
    },

    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    },

    formatStatus(status) {
      if (!status) return ''
      return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },

    getStatusColor(status) {
      if (!status) return 'grey'

      const statusMap = {
        'uploaded': 'blue',
        'ocr_processing': 'amber',
        'ocr_complete': 'light-blue',
        'flashcard_generating': 'orange',
        'flashcard_complete': 'green',
        'error': 'red'
      }

      return statusMap[status] || 'grey'
    },

    isProcessingComplete(document) {
      return document.status === 'flashcard_complete' || document.status === 'error'
    },

    async uploadDocument() {
      if (!this.fileToUpload) {
        this.uploadError = 'Please select a file to upload'
        return
      }

      this.uploading = true
      this.uploadError = null

      try {
        await this.documentsStore.uploadDocument(this.fileToUpload)
        this.showUploadDialog = false
        this.fileToUpload = null
      } catch (error) {
        this.uploadError = error.message || 'Failed to upload document'
      } finally {
        this.uploading = false
      }
    },

    async viewDocument(document) {
      this.selectedDocument = document
      this.showViewDialog = true
      this.activeTab = 0
      this.extractedText = null
      this.flashcards = []

      // Fetch extracted text when tab is changed to text
      this.$watch('activeTab', async (newVal) => {
        if (newVal === 1 && !this.extractedText) {
          await this.fetchExtractedText()
        } else if (newVal === 2 && this.flashcards.length === 0) {
          await this.fetchFlashcards()
        }
      })
    },

    async fetchExtractedText() {
      if (!this.selectedDocument) return

      this.loadingText = true

      try {
        const response = await documentsAPI.getDocumentText(this.selectedDocument.id)
        this.extractedText = response.data
      } catch (error) {
        console.error('Failed to fetch extracted text:', error)
      } finally {
        this.loadingText = false
      }
    },

    async fetchFlashcards() {
      if (!this.selectedDocument) return

      this.loadingFlashcards = true

      try {
        // Find decks associated with this document
        const decksResponse = await this.documentsStore.fetchDocument(this.selectedDocument.id)
        if (decksResponse && decksResponse.decks && decksResponse.decks.length > 0) {
          // Get flashcards for the first deck
          const deckId = decksResponse.decks[0].id
          const flashcardsResponse = await this.flashcardsStore.fetchFlashcards(deckId)
          this.flashcards = flashcardsResponse || []
        }
      } catch (error) {
        console.error('Failed to fetch flashcards:', error)
      } finally {
        this.loadingFlashcards = false
      }
    },

    deleteDocument(document) {
      this.selectedDocument = document
      this.showDeleteDialog = true
    },

    async confirmDelete() {
      if (!this.selectedDocument) return

      this.deleting = true

      try {
        const result = await this.documentsStore.deleteDocument(this.selectedDocument.id)

        if (result) {
          console.log(`Successfully deleted document: ${this.selectedDocument.id}`)
          this.showDeleteDialog = false
          // Refresh the documents list
          await this.documentsStore.fetchDocuments()
        } else {
          console.error('Failed to delete document: API returned false')
          this.documentsStore.error = 'Failed to delete document. Please try again.'
        }
      } catch (error) {
        console.error('Failed to delete document:', error)
        this.documentsStore.error = error.message || 'Failed to delete document. Please try again.'
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
.extracted-text {
  white-space: pre-wrap;
  font-family: monospace;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
}
</style>
