# SpeechRAG Pipeline Architecture

This document provides a deep-dive into how the real-time, cross-modal RAG system works.

## The Core Problem

Traditional voice AI assistants follow this pipeline:
1.  User speaks.
2.  **Speech-to-Text (STT)** converts audio to text (200-500ms latency).
3.  Text is used to search a knowledge base.
4.  Context is injected into the AI's response.

**Our Innovation**: We eliminate step 2 by comparing audio directly to text in a shared semantic space using **Meta SONAR**.

---

## Meta SONAR: The Key Technology

Meta's **SONAR** (Sentence-level multimOdal and laNguage-Agnostic Representations) converts:
-   **Text** → 1024-dimensional vector
-   **Speech Audio** → 1024-dimensional vector

Both vectors exist in the **same semantic space**. A spoken sentence about "water pressure in Senai" will have a vector mathematically similar to a text alert about "Senai - Pressure Adjustment".

---

## Component Breakdown

### 1. `main.py` (FastAPI Server)
The entry point. Responsibilities:
-   Serves the frontend dashboard (`/`).
-   Opens a WebSocket (`/ws/audio`) for streaming audio.
-   Receives raw PCM audio chunks from the client.
-   Passes audio to `LogicBrain` for RAG processing.
-   Sends `CONTEXT_INJECTION` messages if a match is found.

### 2. `bridge/stream_buffer.py` (AudioStreamBuffer)
A sliding window buffer that accumulates audio chunks.
-   Collects incoming bytes (e.g., 4096 bytes at a time).
-   When enough data is collected (2 seconds of audio), returns that window for processing.
-   Uses a stride to prevent redundant re-processing.

### 3. `bridge/logic_brain.py` (LogicBrain)
The **orchestrator** of the RAG pipeline:
1.  **Encode Audio**: Sends audio to `SonarClient` → Returns a 1024-dim vector.
2.  **Search Qdrant**: Sends the vector to `QdrantVectorStore` → Returns matching alerts.
3.  **Threshold Check**: If similarity score > 0.38, the match is relevant.
4.  **Format Output**: Wraps the alert in `<context>...</context>` tags.

### 4. `rag_engine/sonar_client.py` (SonarClient)
An HTTP client for the SONAR microservice:
-   `encode_audio(bytes)`: Base64 encodes audio → POSTs to `/encode_audio` → Returns vector.
-   `encode_text(str)`: POSTs text to `/encode_text` → Returns vector.

### 5. `rag_engine/qdrant_store.py` (QdrantVectorStore)
A wrapper around the Qdrant vector database:
-   `initialize_collection()`: Creates the `ranhill_alerts` collection.
-   `upsert(id, vector, payload)`: Adds alerts to the database.
-   `search(vector, limit, score_threshold)`: Finds similar alerts.

### 6. `sonar_service/main.py` (Real SONAR Service)
A Dockerized FastAPI server running:
-   `text_sonar_basic_encoder` (text encoding).
-   `sonar_speech_encoder_eng` (audio encoding).
-   Exposes `/encode_text` and `/encode_audio` endpoints.
-   Runs on **GPU (CUDA)** for fast inference.

### 7. `scripts/seed_db.py`
A one-time setup script that:
-   Reads `alerts_index.json` (operational alerts).
-   Encodes each alert's text using `SonarClient.encode_text()`.
-   Stores the vectors in Qdrant.

### 8. `frontend/index.html` (Dashboard)
A browser-based debugging UI:
-   Connects to the WebSocket.
-   Simulates audio streaming (sends random noise).
-   Displays `CONTEXT_INJECTION` messages in real-time.
-   Shows latency metrics.

---

## Data Flow

```
┌───────────────┐       Audio Bytes        ┌──────────────────┐
│   Browser     │ ───────────────────────► │   main.py        │
│  (Frontend)   │                          │  (FastAPI/WS)    │
└───────────────┘                          └────────┬─────────┘
                                                    │
                                                    ▼
                                           ┌────────────────────┐
                                           │   LogicBrain       │
                                           │   (Orchestrator)   │
                                           └────────┬───────────┘
                                                    │
                         ┌──────────────────────────┼──────────────────────────┐
                         ▼                                                     ▼
                ┌─────────────────┐                                 ┌─────────────────┐
                │  SonarClient    │                                 │ QdrantVectorStore│
                │  (HTTP Client)  │                                 │  (Vector DB)    │
                └────────┬────────┘                                 └────────┬────────┘
                         │                                                   │
                         ▼                                                   ▼
                ┌─────────────────┐                                 ┌─────────────────┐
                │ sonar_service   │                                 │   Qdrant        │
                │ (Docker+GPU)    │                                 │ (Docker:6333)   │
                └─────────────────┘                                 └─────────────────┘
```

---

## Verification Results

| Test Case | Input | Similarity Score | Result |
|-----------|-------|------------------|--------|
| Valid Query | "Water pressure too low in Senai" | **0.43** | ✅ Match Found |
| Audio Noise | Random bytes | **0.26** | ❌ Correctly Filtered |

**Threshold**: 0.38 (Calibrated to separate signal from noise)

---

## Why This Matters

This pipeline enables **PersonaPlex** (the voice AI) to:
-   Instantly detect relevant user queries.
-   Inject real-time operational context.
-   Do this in **< 50ms**, enabling truly conversational AI.

The "empty dashboard" during noise is the **correct behavior**: the system knows random noise is not a query about water pipes.
