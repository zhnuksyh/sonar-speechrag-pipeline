#!/bin/bash

# SpeechRAG Pipeline Startup Script
# This script starts all required services for the SpeechRAG pipeline.

set -e

echo "=========================================="
echo "  SpeechRAG Pipeline Startup"
echo "=========================================="

# 1. Start Docker services (Qdrant + SONAR Encoder)
echo ""
echo "[1/3] Starting Docker services (Qdrant, SONAR Encoder)..."
docker compose up -d

# 2. Wait for services to be ready
echo ""
echo "[2/3] Waiting for services to initialize..."
echo "      - Qdrant: http://localhost:6333"
echo "      - SONAR Encoder: http://localhost:8001"

# Wait for Qdrant health check
until curl -s http://localhost:6333/health > /dev/null 2>&1; do
    echo "      Waiting for Qdrant..."
    sleep 2
done
echo "      ✓ Qdrant is ready."

# Wait for SONAR service (may take a while for model download on first run)
echo "      Waiting for SONAR Encoder (this may take a few minutes on first run)..."
until curl -s http://localhost:8001/docs > /dev/null 2>&1; do
    sleep 5
done
echo "      ✓ SONAR Encoder is ready."

# 3. Start the main FastAPI server
echo ""
echo "[3/3] Starting SpeechRAG Server..."
echo "      Dashboard: http://localhost:8000"
echo ""
echo "=========================================="
echo "  All services running! Press Ctrl+C to stop."
echo "=========================================="

python main.py
