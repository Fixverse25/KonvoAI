# =============================================================================
# EVA-Dev Frontend Dockerfile
# Multi-stage build for development and production
# =============================================================================

FROM node:18-alpine as base

# Set working directory
WORKDIR /app

# Install dependencies for node-gyp
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# =============================================================================
# Development Stage
# =============================================================================
FROM base as development

# Install all dependencies (including dev)
RUN npm ci

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Development command
CMD ["npm", "start"]

# =============================================================================
# Build Stage
# =============================================================================
FROM base as build

# Install all dependencies for build
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# =============================================================================
# Production Stage
# =============================================================================
FROM nginx:alpine as production

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application
COPY --from=build /app/build /usr/share/nginx/html

# Add non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Change ownership
RUN chown -R nextjs:nodejs /usr/share/nginx/html && \
    chown -R nextjs:nodejs /var/cache/nginx && \
    chown -R nextjs:nodejs /var/log/nginx && \
    chown -R nextjs:nodejs /etc/nginx/conf.d

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
