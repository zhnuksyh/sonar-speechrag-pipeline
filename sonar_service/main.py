import torch
import torchaudio
import io
import base64
import numpy as np
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from sonar.inference_pipelines.text import TextToEmbeddingModelPipeline
from sonar.inference_pipelines.speech import SpeechToEmbeddingModelPipeline

app = FastAPI(title="Real SONAR Encoder")

# Global models
text_pipeline = None
speech_pipeline = None

@app.on_event("startup")
async def load_models():
    global text_pipeline, speech_pipeline
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading SONAR models on {device}...", flush=True)
        
        # Load Text Encoder
        # Explicitly passing 'tokenizer' which was the original error
        print("Loading Text Encoder...", flush=True)
        text_pipeline = TextToEmbeddingModelPipeline(encoder="text_sonar_basic_encoder", tokenizer="text_sonar_basic_encoder", device=device)
        print("Text Encoder loaded.", flush=True)
        
        # Load Speech Encoder
        # Using English encoder as found in docs
        print("Loading Speech Encoder...", flush=True)
        speech_pipeline = SpeechToEmbeddingModelPipeline(encoder="sonar_speech_encoder_eng", device=device)
        print("Speech Encoder loaded.", flush=True)
        
        print("SONAR models loaded successfully.", flush=True)
    except Exception as e:
        print(f"CRITICAL ERROR loading models: {e}", flush=True)
        raise e

@app.post("/encode_audio")
async def encode_audio(payload: dict = Body(...)):
    """
    Expects 'audio_base64' (PCM16 16kHz raw bytes or wav)
    """
    try:
        b64_data = payload.get("audio_base64")
        if not b64_data:
            raise HTTPException(status_code=400, detail="Missing audio_base64")

        audio_bytes = base64.b64decode(b64_data)
        
        # Convert raw PCM bytes to Tensor
        # Assuming input is raw PCM 16-bit 16kHz Mono as per project spec
        # We need to wrap it into a float tensor for SONAR
        # Note: SONAR usually expects a waveform tensor.
        
        # Method 1: Torchaudio load (if it's a WAV container)
        # But our system sends raw PCM. 
        # We construct a tensor from raw bytes:
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        audio_tensor = torch.from_numpy(audio_np).unsqueeze(0) # (1, T)
        
        # SONAR pipeline expects just the tensor usually
        embeddings = speech_pipeline.predict([audio_tensor], n_parallel=1)
        
        # embeddings is a wrapper, we need the actual tensor
        # It usually returns a list of tensors or a stacked tensor
        # Let's inspect the output type carefully or ensure we convert to list
        # predict returns a list of Tensors
        
        vector = embeddings[0].cpu().numpy().tolist()
        return {"vector": vector}

    except Exception as e:
        print(f"Error encoding audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/encode_text")
async def encode_text(payload: dict = Body(...)):
    try:
        text = payload.get("text")
        if not text:
            raise HTTPException(status_code=400, detail="Missing text")
            
        embeddings = text_pipeline.predict([text], source_lang="eng_Latn")
        vector = embeddings[0].cpu().numpy().tolist()
        return {"vector": vector}
        
    except Exception as e:
        print(f"Error encoding text: {e}")
        raise HTTPException(status_code=500, detail=str(e))
