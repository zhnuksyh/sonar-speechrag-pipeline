# Ranhill SAJ SpeechRAG - Verification Dashboard Manual

## Overview
The Verification Dashboard is a web-based tool for testing the SpeechRAG pipeline without needing external audio hardware.

## Access
1. **URL**: `http://localhost:8000`
2. **Status Indicator**: Located in the top right. Should be **Green (Connected)**.

## How to Test
1. **Prepare**: Ensure the backend server is running (`python main.py`).
2. **Start Simulation**:
   - Click the **"Start Stream"** button.
   - This sends 16kHz PCM16 audio packets (random noise) to the backend every 100ms.
   - The backend buffers this audio (2-second window).
   - Every 320ms (stride), it triggers the RAG pipeline.
3. **Observe**:
   - **Live Feed**: Watch for "Cards" appearing in the feed. Each card represents a retrieved maintenance alert injected by the Logic Brain.
   - **Latency**: The "AVG LATENCY" metric updates with each injection, showing the round-trip time.

## Troubleshooting
- **No Cards Appearing?**
  - Check the server logs (`server.log`).
  - Ensure the simulation is actually sending data (Check browser Console F12).
  - The demo uses random vectors, so matching is probabilistic (but we set threshold to 0.0 for this demo).

## Backend State
- **SONAR**: Mocked (Random Vectors)
- **Qdrant**: Local Docker Container (Port 6333)
- **Logic Brain**: Threshold temporarily lowered to 0.0 for easy testing.
