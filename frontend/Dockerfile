# Install production dependencies
FROM node:22-alpine AS builder

WORKDIR /build

COPY package.json package-lock.json* ./

RUN npm ci --omit=dev


# Lean production image
FROM node:22-alpine

WORKDIR /app

# Create a non-root user
RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --ingroup appgroup appuser

# Copy production node_modules from builder
COPY --from=builder /build/node_modules ./node_modules

# Copy application source (no .env files — injected at runtime)
COPY app.js .
COPY views/ ./views/

RUN chown -R appuser:appgroup /app

USER appuser

ENV NODE_ENV=production

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "app.js"]
