from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging

# Configure logging
logger = logging.getLogger(__name__)

class QdrantVectorStore:
    def __init__(self, host="localhost", port=6333, collection_name="ranhill_alerts"):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        
    def initialize_collection(self, vector_size: int = 1024):
        """
        Recreates the collection with the specified vector size.
        """
        try:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Collection '{self.collection_name}' initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise

    def upsert(self, points: list[models.PointStruct]):
        """
        Upserts points into the collection.
        """
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Upserted {len(points)} points.")
        except Exception as e:
            logger.error(f"Failed to upsert points: {e}")
            raise

    def search(self, vector: list[float], limit: int = 1, score_threshold: float = 0.0) -> list[models.ScoredPoint]:
        """
        Searches for the nearest vectors.
        """
        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=limit,
                score_threshold=score_threshold
            ).points # query_points returns a QueryResponse which has points
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
