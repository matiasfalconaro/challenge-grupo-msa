# Frontend Dockerfile for Astro application
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application source
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=3000
ENV PUBLIC_BACKEND_URL=$PUBLIC_BACKEND_URL

# Start the application
CMD ["node", "./dist/server/entry.mjs"]
