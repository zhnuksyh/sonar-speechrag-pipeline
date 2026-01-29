import httpx
import base64
import logging

# Configure logging
logger = logging.getLogger(__name__)

class SonarClient:
    def __init__(self, service_url: str = "http://localhost:8001"):
        self.service_url = service_url
        self.audio_endpoint = f"{service_url}/encode_audio"
        self.text_endpoint = f"{service_url}/encode_text"
    
    async def encode_audio(self, audio_bytes: bytes) -> list[float]:
        """
        Sends PCM audio bytes to the SONAR service and returns a vector.
        """
        try:
            # Base64 encode the audio bytes
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.audio_endpoint,
                    json={"audio_base64": audio_b64},
                    timeout=2.0 
                )
                response.raise_for_status()
                data = response.json()
                return data.get("vector", [])
                
        except Exception as e:
            logger.error(f"Failed to encode audio via SONAR: {e}")
            return []

    async def encode_text(self, text: str) -> list[float]:
        """
        Sends text to the SONAR service and returns a vector.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.text_endpoint,
                    json={"text": text},
                    timeout=2.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("vector", [])
        except Exception as e:
            logger.error(f"Failed to encode text via SONAR: {e}")
            return []
