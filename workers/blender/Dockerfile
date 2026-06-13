FROM python:3.11-slim

# Install system dependencies and Blender
RUN apt-get update && apt-get install -y \
    blender \
    libglu1-mesa \
    libxi6 \
    libxrender1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy requirements from backend and install them
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and workers directories
COPY backend/ /workspace/backend
COPY workers/ /workspace/workers

ENV PYTHONPATH=/workspace/backend
ENV BLENDER_PATH=blender

CMD ["python", "workers/blender/worker.py"]
