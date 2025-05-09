import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DocumentsView from '../views/DocumentsView.vue'
import DecksView from '../views/DecksView.vue'
import DeckDetailView from '../views/DeckDetailView.vue'
import PublicDecksView from '../views/PublicDecksView.vue'
import ProfileView from '../views/ProfileView.vue'
import StudyView from '../views/StudyView.vue'
import NotFoundView from '../views/NotFoundView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresGuest: true }
  },
  {
    path: '/documents',
    name: 'documents',
    component: DocumentsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/decks',
    name: 'decks',
    component: DecksView,
    meta: { requiresAuth: true }
  },
  {
    path: '/decks/:id',
    name: 'deck-detail',
    component: DeckDetailView,
    props: true
  },
  {
    path: '/public-decks',
    name: 'public-decks',
    component: PublicDecksView
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/study/:deckId',
    name: 'study',
    component: StudyView,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (requiresGuest && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
