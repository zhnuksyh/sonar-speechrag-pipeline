import logging
from rag_engine.sonar_client import SonarClient
from rag_engine.qdrant_store import QdrantVectorStore

# Configure logging
logger = logging.getLogger(__name__)

class LogicBrain:
    """
    Simulates the reasoning part of the pipeline (Llama 3.2 3B).
    It decides if the retrieved RAG content is worth interrupting with.
    """
    def __init__(self):
        self.sonar_client = SonarClient()
        self.qdrant_store = QdrantVectorStore()
        # Ensure collection exists (idempotent-ish if we assume it's created or we just search)
        # We rely on previous steps for initialization, or we can lazy init.
        # Strict separation: LogicBrain just uses it.

    async def process_audio_window(self, audio_window: bytes):
        """
        Process audio window: Encode -> Search -> Decide
        """
        try:
            # 1. Encode Audio
            vector = await self.sonar_client.encode_audio(audio_window)
            if not vector:
                return None
            
            # 2. Search Qdrant
            # Threshold 0.38 for Real SONAR (Calibrated: "Water pressure..." -> "Senai" yielded 0.43)
            results = self.qdrant_store.search(vector, limit=1, score_threshold=0.38)
            
            if not results:
                return None
            
            top_result = results[0]
            payload = top_result.payload
            
            # 3. Format Response
            # Steering tag: <context>...</context>
            # We construct a natural language alert from the payload
            alert_text = f"ALERT: {payload.get('location', 'Unknown Location')} - {payload.get('status', 'Status Unknown')}. Recovery: {payload.get('eta', 'N/A')}"
            
            return alert_text

        except Exception as e:
            logger.error(f"LogicBrain error: {e}")
            return None