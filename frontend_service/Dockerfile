# frontend_service/Dockerfile

# Build stage
FROM node:16-alpine AS build-stage

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy ESLint and Babel configs first
COPY .eslintrc.js babel.config.js vue.config.js ./

# Copy project files and build
COPY . .
# Fix permissions for vue-cli-service
RUN chmod +x node_modules/.bin/vue-cli-service
# Disable ESLint during build
RUN npm run build -- --no-lint

# Production stage
FROM nginx:stable-alpine AS production-stage

# Copy built files from build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
