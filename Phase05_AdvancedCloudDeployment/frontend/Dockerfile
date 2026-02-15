# ================================
# Next.js Frontend (Production)
# ================================

# -------- Stage 1: Builder --------
# Lightweight Node.js image for building the app
FROM node:22-alpine AS builder

# Set working directory inside container
WORKDIR /app

# Copy dependency definition files first
# Improves Docker layer caching
COPY package.json package-lock.json ./

# Install exact dependencies (includes devDependencies for build)
RUN npm ci

# Copy application source code
# NOTE: .env files are intentionally NOT copied
# Environment variables should be injected at runtime
COPY . .

# Build the Next.js application
RUN npm run build


# -------- Stage 2: Runner --------
# Minimal runtime image (no build tools)
FROM node:22-alpine AS runner

# Set working directory
WORKDIR /app

# Mark environment as production
ENV NODE_ENV=production

# Copy only required build artifacts from builder stage
# This keeps the image small and secure
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./

# Install only production dependencies
RUN npm install --omit=dev

# Expose the port used by Next.js
EXPOSE 3000

# IMPORTANT:
# - Do NOT bake .env files into the image
# - Use one of the following instead:
#   1) Docker:   docker run --env-file .env frontend:latest
#   2) K8s:      ConfigMaps / Secrets
#   3) Helm:     values.yaml -> env / envFrom
CMD ["npm", "start"]
