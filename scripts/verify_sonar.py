import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from rag_engine.sonar_client import SonarClient
from rag_engine.qdrant_store import QdrantVectorStore

async def verify():
    print("Verifying Real SONAR Pipeline...")
    
    sonar = SonarClient()
    qdrant = QdrantVectorStore()
    
    # 1. Encode a semantic query
    query_text = "Water pressure too low in Senai"
    print(f"Query: '{query_text}'")
    
    try:
        vector = await sonar.encode_text(query_text)
        print(f"Vector generated. Dimensions: {len(vector)}")
    except Exception as e:
        print(f"SONAR Encoding failed: {e}")
        return

    # 2. Search
    try:
        results = qdrant.search(vector, limit=3, score_threshold=0.0)
        print(f"Found {len(results)} matches.")
        for res in results:
            print(f" - [{res.score:.4f}] {res.payload['location']} : {res.payload['status']}")
            
    except Exception as e:
        print(f"Qdrant Search failed: {e}")

    # 3. Test Audio Noise (to debug false positives)
    print("\nTesting Audio Noise (Simulated)...")
    try:
        # Create random bytes (similar to frontend) - 4096 bytes
        import os
        import base64
        noise_bytes = os.urandom(4096)
        # Pass bytes directly to SonarClient.encode_audio (it handles b64 encoding)
        noise_vector = await sonar.encode_audio(noise_bytes)
        print(f"Noise Vector generated. Dimensions: {len(noise_vector)}")
        
        noise_results = qdrant.search(noise_vector, limit=3, score_threshold=0.0)
        print(f"Found {len(noise_results)} matches for NOISE.")
        for res in noise_results:
            print(f" - [{res.score:.4f}] {res.payload['location']}")
            
    except Exception as e:
        print(f"Audio Noise Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
