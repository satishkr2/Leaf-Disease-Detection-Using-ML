FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY preprocessing/ ./preprocessing/
COPY model/ ./model/

WORKDIR /app/backend

ENV PYTHONPATH=/app
ENV MODEL_PATH=/app/model/saved_models/best_model.h5
ENV CLASS_LABELS_PATH=/app/model/saved_models/class_labels.json

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
