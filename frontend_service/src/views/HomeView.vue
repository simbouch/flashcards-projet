<template>
  <div class="home">
    <v-container class="py-8">
      <!-- Hero Section -->
      <v-row class="mb-12">
        <v-col cols="12">
          <div class="hero-section text-center animate-fade-in">
            <div class="hero-icon mb-6">
              <v-avatar size="120" class="gradient-primary animate-pulse">
                <v-icon size="60" color="white">mdi-cards</v-icon>
              </v-avatar>
            </div>
            <h1 class="text-h2 font-weight-bold mb-4 gradient-text">
              Welcome to FlashCards
            </h1>
            <p class="text-h6 text-medium-emphasis mb-6 max-width-600 mx-auto">
              Transform your documents into interactive flashcards using cutting-edge OCR and AI technology.
              Learn smarter, not harder.
            </p>
            <div class="hero-stats d-flex justify-center flex-wrap gap-4 mb-8">
              <div class="stat-item text-center">
                <v-icon size="32" class="text-primary mb-2">mdi-lightning-bolt</v-icon>
                <p class="text-h6 font-weight-bold mb-1">Fast</p>
                <p class="text-caption">Instant Processing</p>
              </div>
              <div class="stat-item text-center">
                <v-icon size="32" class="text-success mb-2">mdi-robot</v-icon>
                <p class="text-h6 font-weight-bold mb-1">Smart</p>
                <p class="text-caption">AI-Powered</p>
              </div>
              <div class="stat-item text-center">
                <v-icon size="32" class="text-info mb-2">mdi-chart-line</v-icon>
                <p class="text-h6 font-weight-bold mb-1">Effective</p>
                <p class="text-caption">Track Progress</p>
              </div>
            </div>
          </div>
        </v-col>
      </v-row>

      <!-- Feature Cards for Authenticated Users -->
      <v-row v-if="isAuthenticated" class="mb-8">
        <v-col cols="12" md="6">
          <v-card
            class="modern-card-elevated feature-card animate-slide-in-left"
            height="100%"
            hover
          >
            <div class="card-gradient-overlay"></div>
            <v-card-text class="pa-6 position-relative">
              <div class="feature-icon mb-4">
                <v-avatar size="64" class="gradient-primary">
                  <v-icon size="32" color="white">mdi-file-document</v-icon>
                </v-avatar>
              </div>
              <h3 class="text-h5 font-weight-bold mb-3">Upload Documents</h3>
              <p class="text-body-1 mb-4 text-medium-emphasis">
                Upload images or PDFs to extract text and generate flashcards automatically using our advanced OCR technology.
              </p>
              <v-btn
                class="modern-btn-primary"
                to="/documents"
                size="large"
                block
              >
                <v-icon left>mdi-upload</v-icon>
                Go to Documents
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <v-card
            class="modern-card-elevated feature-card animate-slide-in-right animate-delay-200"
            height="100%"
            hover
          >
            <div class="card-gradient-overlay"></div>
            <v-card-text class="pa-6 position-relative">
              <div class="feature-icon mb-4">
                <v-avatar size="64" class="gradient-success">
                  <v-icon size="32" color="white">mdi-cards</v-icon>
                </v-avatar>
              </div>
              <h3 class="text-h5 font-weight-bold mb-3">My Flashcard Decks</h3>
              <p class="text-body-1 mb-4 text-medium-emphasis">
                View, manage, and study your personalized flashcard decks. Track your progress and improve your learning.
              </p>
              <v-btn
                class="modern-btn-primary"
                to="/decks"
                size="large"
                block
              >
                <v-icon left>mdi-cards</v-icon>
                Go to My Decks
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Public Decks and Authentication Section -->
      <v-row class="mb-8">
        <v-col cols="12" md="6">
          <v-card
            class="modern-card-elevated feature-card animate-scale-in animate-delay-300"
            height="100%"
            hover
          >
            <div class="card-gradient-overlay"></div>
            <v-card-text class="pa-6 position-relative">
              <div class="feature-icon mb-4">
                <v-avatar size="64" class="gradient-info">
                  <v-icon size="32" color="white">mdi-cards-outline</v-icon>
                </v-avatar>
              </div>
              <h3 class="text-h5 font-weight-bold mb-3">Public Flashcard Decks</h3>
              <p class="text-body-1 mb-4 text-medium-emphasis">
                Explore and study from a vast collection of public flashcard decks created by our community of learners.
              </p>
              <v-btn
                class="modern-btn-primary"
                to="/public-decks"
                size="large"
                block
              >
                <v-icon left>mdi-earth</v-icon>
                Browse Public Decks
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="6" v-if="!isAuthenticated">
          <v-card
            class="modern-card-elevated feature-card animate-scale-in animate-delay-400"
            height="100%"
            hover
          >
            <div class="card-gradient-overlay auth-card-gradient"></div>
            <v-card-text class="pa-6 position-relative">
              <div class="feature-icon mb-4">
                <v-avatar size="64" class="gradient-secondary">
                  <v-icon size="32" color="white">mdi-account-plus</v-icon>
                </v-avatar>
              </div>
              <h3 class="text-h5 font-weight-bold mb-3">Get Started Today</h3>
              <p class="text-body-1 mb-4 text-medium-emphasis">
                Join thousands of learners! Create an account to unlock the full potential of AI-powered flashcard generation.
              </p>
              <div class="d-flex gap-2">
                <v-btn
                  class="modern-btn-primary flex-grow-1"
                  to="/register"
                  size="large"
                >
                  <v-icon left>mdi-account-plus</v-icon>
                  Register
                </v-btn>
                <v-btn
                  variant="outlined"
                  class="modern-btn flex-grow-1"
                  to="/login"
                  size="large"
                >
                  <v-icon left>mdi-login</v-icon>
                  Login
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- How It Works Section -->
      <v-row>
        <v-col cols="12">
          <div class="text-center mb-8 animate-fade-in animate-delay-500">
            <h2 class="text-h3 font-weight-bold mb-4 gradient-text">How It Works</h2>
            <p class="text-h6 text-medium-emphasis max-width-600 mx-auto">
              Transform your learning experience in just four simple steps
            </p>
          </div>

          <v-card class="modern-card-elevated pa-6">
            <v-timeline
              side="end"
              class="modern-timeline"
            >
              <v-timeline-item
                dot-color="primary"
                size="large"
                class="animate-slide-in-left animate-delay-600"
              >
                <template v-slot:icon>
                  <v-avatar size="60" class="gradient-primary">
                    <v-icon size="30" color="white">mdi-upload</v-icon>
                  </v-avatar>
                </template>
                <v-card class="modern-card ml-4">
                  <v-card-text class="pa-6">
                    <div class="d-flex align-center mb-3">
                      <v-chip class="gradient-primary text-white mr-3" size="small">Step 1</v-chip>
                      <h3 class="text-h5 font-weight-bold">Upload Documents</h3>
                    </div>
                    <p class="text-body-1 text-medium-emphasis mb-0">
                      Upload images or PDFs containing the text you want to study. Our system supports multiple formats and high-quality image processing.
                    </p>
                  </v-card-text>
                </v-card>
              </v-timeline-item>

              <v-timeline-item
                dot-color="success"
                size="large"
                class="animate-slide-in-right animate-delay-700"
              >
                <template v-slot:icon>
                  <v-avatar size="60" class="gradient-success">
                    <v-icon size="30" color="white">mdi-text-recognition</v-icon>
                  </v-avatar>
                </template>
                <v-card class="modern-card ml-4">
                  <v-card-text class="pa-6">
                    <div class="d-flex align-center mb-3">
                      <v-chip class="gradient-success text-white mr-3" size="small">Step 2</v-chip>
                      <h3 class="text-h5 font-weight-bold">OCR Processing</h3>
                    </div>
                    <p class="text-body-1 text-medium-emphasis mb-0">
                      Our advanced OCR technology extracts text from your documents with high accuracy, preserving formatting and context.
                    </p>
                  </v-card-text>
                </v-card>
              </v-timeline-item>

              <v-timeline-item
                dot-color="info"
                size="large"
                class="animate-slide-in-left animate-delay-800"
              >
                <template v-slot:icon>
                  <v-avatar size="60" class="gradient-info">
                    <v-icon size="30" color="white">mdi-robot</v-icon>
                  </v-avatar>
                </template>
                <v-card class="modern-card ml-4">
                  <v-card-text class="pa-6">
                    <div class="d-flex align-center mb-3">
                      <v-chip class="gradient-info text-white mr-3" size="small">Step 3</v-chip>
                      <h3 class="text-h5 font-weight-bold">AI-Generated Flashcards</h3>
                    </div>
                    <p class="text-body-1 text-medium-emphasis mb-0">
                      Our intelligent AI analyzes the extracted text and automatically generates meaningful question-answer pairs optimized for learning.
                    </p>
                  </v-card-text>
                </v-card>
              </v-timeline-item>

              <v-timeline-item
                dot-color="secondary"
                size="large"
                class="animate-slide-in-right animate-delay-900"
              >
                <template v-slot:icon>
                  <v-avatar size="60" class="gradient-secondary">
                    <v-icon size="30" color="white">mdi-book-open-variant</v-icon>
                  </v-avatar>
                </template>
                <v-card class="modern-card ml-4">
                  <v-card-text class="pa-6">
                    <div class="d-flex align-center mb-3">
                      <v-chip class="gradient-secondary text-white mr-3" size="small">Step 4</v-chip>
                      <h3 class="text-h5 font-weight-bold">Study and Learn</h3>
                    </div>
                    <p class="text-body-1 text-medium-emphasis mb-0">
                      Review your flashcards with our interactive study mode, track your progress, and improve your retention with spaced repetition.
                    </p>
                  </v-card-text>
                </v-card>
              </v-timeline-item>
            </v-timeline>
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
  },
  mounted() {
    // Add staggered animation to elements
    this.$nextTick(() => {
      const elements = document.querySelectorAll('.animate-fade-in, .animate-slide-in-left, .animate-slide-in-right, .animate-scale-in')
      elements.forEach((el, index) => {
        el.style.animationDelay = `${index * 0.1}s`
      })
    })
  }
}
</script>

<style scoped>
/* Hero Section Styles */
.hero-section {
  padding: 4rem 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: var(--border-radius-2xl);
  margin-bottom: 2rem;
}

.hero-icon {
  position: relative;
}

.hero-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 140px;
  height: 140px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  z-index: -1;
}

.gradient-text {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.max-width-600 {
  max-width: 600px;
}

.hero-stats {
  gap: 2rem;
}

.stat-item {
  padding: 1rem;
  border-radius: var(--border-radius-lg);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  transition: all var(--transition-normal);
  min-width: 120px;
}

.stat-item:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

/* Feature Cards */
.feature-card {
  position: relative;
  overflow: hidden;
  transition: all var(--transition-normal);
}

.feature-card:hover {
  transform: translateY(-10px) scale(1.02);
}

.card-gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--gradient-primary);
}

.auth-card-gradient {
  background: var(--gradient-secondary) !important;
}

.feature-icon {
  position: relative;
}

.feature-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  z-index: -1;
}

/* Timeline Styles */
.modern-timeline {
  padding: 2rem 0;
}

.modern-timeline .v-timeline-item {
  margin-bottom: 2rem;
}

.modern-timeline .v-timeline-item:last-child {
  margin-bottom: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-section {
    padding: 2rem 0;
  }

  .hero-stats {
    gap: 1rem;
  }

  .stat-item {
    min-width: 100px;
    padding: 0.75rem;
  }

  .feature-card {
    margin-bottom: 1rem;
  }

  .d-flex.gap-2 {
    flex-direction: column;
  }

  .d-flex.gap-2 .v-btn {
    margin-bottom: 0.5rem;
  }
}

/* Dark mode adjustments */
.v-theme--dark .hero-section {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
}

.v-theme--dark .stat-item {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Animation improvements */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.hero-icon .v-avatar {
  animation: float 3s ease-in-out infinite;
}

/* Hover effects for timeline items */
.v-timeline-item:hover .v-card {
  transform: translateX(10px);
  box-shadow: var(--shadow-xl);
}

.v-timeline-item .v-card {
  transition: all var(--transition-normal);
}
</style>
