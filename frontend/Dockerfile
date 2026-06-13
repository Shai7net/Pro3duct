FROM node:22-alpine AS builder

WORKDIR /workspace
RUN npm install -g pnpm@10.23.0

# Copy lock and configurations
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# Copy source code and build
COPY . .
RUN pnpm build

FROM node:22-alpine AS runner
WORKDIR /workspace
RUN npm install -g pnpm@10.23.0

COPY --from=builder /workspace/next.config.ts ./
COPY --from=builder /workspace/package.json ./
COPY --from=builder /workspace/public ./public
COPY --from=builder /workspace/.next ./.next
COPY --from=builder /workspace/node_modules ./node_modules

EXPOSE 3000
CMD ["pnpm", "start"]
