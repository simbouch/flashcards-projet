<template>
  <div class="home">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-card class="mb-6">
            <v-card-title class="text-h4">
              Welcome to Flashcards App
            </v-card-title>
            <v-card-text>
              <p class="text-body-1">
                Create and study flashcards generated from your documents using OCR and AI technology.
              </p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row v-if="isAuthenticated">
        <v-col cols="12" md="6">
          <v-card class="mb-6" height="100%">
            <v-card-title>
              <v-icon left>mdi-file-document</v-icon>
              Upload Documents
            </v-card-title>
            <v-card-text>
              <p>Upload images or PDFs to extract text and generate flashcards automatically.</p>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/documents">
                Go to Documents
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <v-card class="mb-6" height="100%">
            <v-card-title>
              <v-icon left>mdi-cards</v-icon>
              My Flashcard Decks
            </v-card-title>
            <v-card-text>
              <p>View and study your flashcard decks.</p>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/decks">
                Go to My Decks
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" md="6">
          <v-card class="mb-6" height="100%">
            <v-card-title>
              <v-icon left>mdi-cards-outline</v-icon>
              Public Flashcard Decks
            </v-card-title>
            <v-card-text>
              <p>Browse and study public flashcard decks created by other users.</p>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/public-decks">
                Browse Public Decks
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>

        <v-col cols="12" md="6" v-if="!isAuthenticated">
          <v-card class="mb-6" height="100%">
            <v-card-title>
              <v-icon left>mdi-account</v-icon>
              Get Started
            </v-card-title>
            <v-card-text>
              <p>Create an account or log in to create your own flashcards.</p>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/register" class="mr-2">
                Register
              </v-btn>
              <v-btn color="secondary" to="/login">
                Login
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="text-h5">
              How It Works
            </v-card-title>
            <v-card-text>
              <v-timeline>
                <v-timeline-item>
                  <template v-slot:icon>
                    <v-avatar>
                      <v-icon>mdi-upload</v-icon>
                    </v-avatar>
                  </template>
                  <v-card>
                    <v-card-title class="text-h6">
                      Upload Documents
                    </v-card-title>
                    <v-card-text>
                      Upload images or PDFs containing the text you want to study.
                    </v-card-text>
                  </v-card>
                </v-timeline-item>

                <v-timeline-item>
                  <template v-slot:icon>
                    <v-avatar>
                      <v-icon>mdi-text-recognition</v-icon>
                    </v-avatar>
                  </template>
                  <v-card>
                    <v-card-title class="text-h6">
                      OCR Processing
                    </v-card-title>
                    <v-card-text>
                      Our system extracts text from your documents using OCR technology.
                    </v-card-text>
                  </v-card>
                </v-timeline-item>

                <v-timeline-item>
                  <template v-slot:icon>
                    <v-avatar>
                      <v-icon>mdi-robot</v-icon>
                    </v-avatar>
                  </template>
                  <v-card>
                    <v-card-title class="text-h6">
                      AI-Generated Flashcards
                    </v-card-title>
                    <v-card-text>
                      Our AI automatically generates question-answer pairs from the extracted text.
                    </v-card-text>
                  </v-card>
                </v-timeline-item>

                <v-timeline-item>
                  <template v-slot:icon>
                    <v-avatar>
                      <v-icon>mdi-book-open-variant</v-icon>
                    </v-avatar>
                  </template>
                  <v-card>
                    <v-card-title class="text-h6">
                      Study and Learn
                    </v-card-title>
                    <v-card-text>
                      Review your flashcards and track your progress.
                    </v-card-text>
                  </v-card>
                </v-timeline-item>
              </v-timeline>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { useAuthStore } from '../store/auth'
import { mapState } from 'pinia'

export default {
  name: 'HomeView',
  computed: {
    ...mapState(useAuthStore, ['isAuthenticated'])
  }
}
</script>
