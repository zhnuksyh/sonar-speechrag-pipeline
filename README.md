# SpeechRAG Pipeline with Meta SONAR

A real-time, cross-modal Retrieval Augmented Generation (RAG) pipeline designed for low-latency context injection into speech conversations. This system uses Meta's **SONAR** (Sentence-level multimOdal and laNguage-Agnostic Representations) model to embed both live audio streams and text alerts into a shared semantic vector space, enabling instant retrieval of relevant updates based on spoken context.

## 🚀 Features

*   **Cross-Modal RAG**: Retrieves text alerts using raw audio embeddings—no Speech-to-Text (STT) required.
*   **Real-Time Processing**: Designed for < 160ms end-to-end latency.
*   **Meta SONAR Integration**: Uses official `sonar-space` library with `sonar_speech_encoder_eng` and `text_sonar_basic_encoder`.
*   **Vector Search**: Powered by **Qdrant** for high-performance similarity search.
*   **Neural Dashboard**: Real-time WebSocket-based frontend to visualize context injections and latency.
*   **Dockerized Architecture**: fully containerized services for easy deployment.

## 🏗 Architecture

The system consists of three main components orchestrated via Docker Compose:

1.  **SpeechRAG Core (`main.py`)**:
    *   FastAPI & WebSocket server handling audio streams.
    *   `LogicBrain`: Orchestrates the RAG flow (Audio -> Vector -> Search -> Threshold -> Injection).
    *   `AudioStreamBuffer`: Manages sliding window buffers for continuous audio processing.

2.  **SONAR Encoder Service (`sonar_service/`)**:
    *   Dedicated microservice running PyTorch and `sonar-space`.
    *   Exposes HTTP endpoints for encoding Audio (PCM16) and Text into fixed-size vectors (1024-dim).
    *   Optimized for CUDA GPU acceleration.

3.  **Vector Database (Qdrant)**:
    *   Stores semantic embeddings of operational alerts.
    *   Allows efficient similarity search with tunable thresholds.

## 🛠️ Installation & Setup

### Prerequisites
*   Docker & Docker Compose
*   NVIDIA GPU (Recommended) with Container Toolkit
*   Python 3.10+

### 1. Clone & Infrastructure
```bash
git clone https://github.com/zhnuksyh/sonar-speechrag-pipeline.git
cd sonar-speechrag-pipeline
```

### 2. Start Services
Launch Qdrant and the SONAR Encoder service:
```bash
docker compose up -d --build
```
*Note: The first run of `sonar_encoder` will download ~3GB of model weights. Check progress with `docker compose logs -f sonar_encoder`.*

### 3. Seed Database
Populate Qdrant with the initial set of alerts (from `alerts_index.json`) using the real text encoder:
```bash
# Ensure services are up first!
python scripts/seed_db.py
```

### 4. Run the Pipeline
Start the main application server:
```bash
python main.py
```

## 🖥️ Usage

### Dashboard
Open `http://localhost:8000` in your browser.
*   **Start Stream**: Simulates an audio stream (noise) to test the pipeline.
*   **Live Feed**: Displays active Context Injections when a match is found.
*   **Latency Monitor**: Real-time tracking of processing overhead.

### Verification Script
To test specific scenarios without speaking, use the verification script:
```bash
python scripts/verify_sonar.py
```
This tests:
1.  **Valid Query**: "Water pressure too low in Senai" (Should Match)
2.  **Noise**: Random audio noise (Should be Filtered)

## 📂 Project Structure

*   `bridge/`: Core logic (`LogicBrain`) and stream buffering.
*   `rag_engine/`: Clients for SONAR (`sonar_client.py`) and Qdrant (`qdrant_store.py`).
*   `sonar_service/`: The Dockerized SONAR model server.
*   `frontend/`: HTML/JS dashboard.
*   `scripts/`: Utilities for seeding and verification.
*   `data/`: Raw alert data (`alerts_index.json`).

## 🧠 Logic & Calibration

The system uses a calibrated Similarity Threshold to distinguish between relevant context and noise.
*   **Current Threshold**: `0.38`
*   **Valid Match Score**: ~0.43+
*   **Noise Score**: ~0.26

This ensures that random conversation or silence does not trigger irrelevant context injections.
