#!/bin/bash
# Bootstrapping script for development.

echo "◈ Initializing Pro3duct Development Environment ◈"

# 1. Install dependencies
echo "Installing monorepo root package dependencies..."
pnpm install

# 2. Boot up infrastructure docker containers
echo "Starting PostgreSQL, Redis, MinIO, and Temporal containers..."
docker compose up -d postgres redis minio minio-setup temporal temporal-ui

# 3. Inform user
echo "Infrastructure is booting up in background."
echo "Wait a few seconds for services to pass health checks, then spin up services using:"
echo "  pnpm dev:backend   # Launch FastAPI"
echo "  pnpm dev:frontend  # Launch Next.js"
echo "◈ Bootstrap setup completed successfully! ◈"
