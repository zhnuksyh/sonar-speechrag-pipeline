# File: main.py
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from bridge.stream_buffer import AudioStreamBuffer
from bridge.logic_brain import LogicBrain
from bridge.mock_personaplex import MockPersonaPlex

app = FastAPI(title="Ranhill SAJ SpeechRAG Prototype")

# Mount frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
async def read_root():
    return FileResponse('frontend/index.html')

# Initialize our core components
# In a real scenario, these would connect to Triton and Qdrant containers
logic_brain = LogicBrain()
persona_sim = MockPersonaPlex()

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Each connection gets its own rolling buffer
    stream_buffer = AudioStreamBuffer(window_seconds=2.0, sample_rate=16000)
    
    print("DEBUG: Client connected to SpeechRAG Bridge")
    
    try:
        while True:
            # Receive raw PCM16 bytes from the client (Expo app or simulator)
            data = await websocket.receive_bytes()
            
            # 1. Add to rolling buffer
            # 2. Check if it's time to run a speculative search (stride)
            should_search, window = stream_buffer.append_and_check(data)
            
            if should_search:
                # Run RAG in the background to avoid blocking the audio stream
                asyncio.create_task(
                    process_rag_query(window, websocket)
                )

    except WebSocketDisconnect:
        print("DEBUG: Client disconnected")

async def process_rag_query(audio_window: bytes, websocket: WebSocket):
    """
    The SpeechRAG Pipeline: Audio -> Vector -> Search -> Inject
    """
    import time
    start_time = time.perf_counter()

    # 1. Simulate SONAR Embedding (Audio -> 1024d Vector)
    # 2. Search Qdrant/Mock Data for Maintenance Alerts
    # 3. Use Llama 3.2 (Logic Brain) to decide if context is relevant
    try:
        context = await logic_brain.process_audio_window(audio_window)
    except Exception as e:
        print(f"Error in RAG pipeline: {e}")
        context = None
    
    if context:
        # Simulate the 'Injection' into PersonaPlex
        injection_msg = persona_sim.format_injection(context)
        
        # Send the context back to the client for UI visualization
        # In production, this goes to PersonaPlex's input buffer
        await websocket.send_json({
            "type": "CONTEXT_INJECTION",
            "payload": injection_msg,
            "source": "SpeechRAG_Silo_2"
        })
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        print(f"INFO: RAG Injection Triggered | Time to Context: {elapsed_ms:.2f}ms")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)