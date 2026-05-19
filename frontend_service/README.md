# Frontend Service

Vue.js 3 single-page application that consumes the backend REST API. It
provides authentication, document upload, deck management, AI-assisted card
generation and an interactive study mode. Static assets are built with
`vue-cli-service` and served by Nginx behind the `frontend-service` container.

## Stack

- **Vue 3** with the Options/Composition API
- **Vuetify 3** for Material Design components
- **Vue Router** for client-side routing
- **Pinia** for state management
- **Axios** for HTTP calls (configured in `src/api/`)
- **Nginx** (production image) configured via `nginx.conf`

## Layout

```
frontend_service/
├── Dockerfile
├── nginx.conf
├── package.json
├── vue.config.js
├── babel.config.js
├── public/                 # index.html and static assets
└── src/
    ├── main.js             # App bootstrap (Vue, Vuetify, Pinia, Router)
    ├── App.vue
    ├── api/                # Axios clients (auth, documents, decks, study)
    ├── assets/             # Images, styles, fonts
    ├── router/             # Route definitions and navigation guards
    ├── store/              # Pinia stores
    └── views/              # Top-level page components
```

## Environment

The frontend talks to the backend via `API_URL`. At build time and at runtime
inside the container, it is set to `http://localhost:8002` by default
(see `docker-compose.yml`). For a different deployment, override `API_URL`
and rebuild the image.

## Run

Through Docker Compose:

```bash
docker compose up -d frontend-service
```

The SPA is served at <http://localhost:8080>.

For local development with hot-reload:

```bash
cd frontend_service
npm install
npm run serve
```

## Build

```bash
cd frontend_service
npm install
npm run build
```

The production bundle is emitted to `dist/` and copied into the Nginx image
during the Docker build.

## Tests / linting

```bash
npm run lint
npm run test
```
