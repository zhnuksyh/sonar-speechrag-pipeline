FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libsndfile1 ffmpeg build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
# Let pip resolve versions. sonar-space likely pulls a compatible torch.
# We also need torchaudio.
RUN pip install --no-cache-dir fastapi uvicorn numpy pydantic sonar-space torchaudio

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
