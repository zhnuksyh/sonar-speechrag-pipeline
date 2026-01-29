import asyncio
import json
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from rag_engine.sonar_client import SonarClient
from rag_engine.qdrant_store import QdrantVectorStore
from qdrant_client.http import models

async def seed():
    print("Starting data seeding...")
    
    # 1. Load Data
    try:
        with open('alerts_index.json', 'r') as f:
            data = json.load(f)
            alerts = data.get("alerts", [])
            print(f"Loaded {len(alerts)} alerts.")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # 2. Initialize Clients
    sonar = SonarClient()
    qdrant = QdrantVectorStore()
    
    # 3. Initialize Collection
    try:
        qdrant.initialize_collection()
    except Exception as e:
        print(f"Error initializing Qdrant: {e}")
        return

    points = []
    
    # 4. Process Alerts
    for i, alert in enumerate(alerts):
        text_to_encode = f"{alert['location']} - {alert['status']}"
        print(f"Encoding: {text_to_encode}")
        
        vector = await sonar.encode_text(text_to_encode)
        
        if not vector:
            print(f"Skipping {alert['id']} due to encoding failure.")
            continue
            
        # Create Point
        point = models.PointStruct(
            id=i, # Simple integer ID
            vector=vector,
            payload=alert
        )
        points.append(point)

    # 5. Upsert
    if points:
        qdrant.upsert(points)
        print("Seeding complete.")
    else:
        print("No points to seed.")

if __name__ == "__main__":
    asyncio.run(seed())
