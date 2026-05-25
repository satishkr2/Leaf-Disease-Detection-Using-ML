#!/bin/bash
# Full project setup script
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Plant Leaf Disease Detection - Setup ==="

# Python venv
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
PIP="$(dirname "$0")/../venv/bin/pip"
PYTHON="$(dirname "$0")/../venv/bin/python"
"$PIP" install -r requirements.txt

# Demo model
echo "Creating demo ML model..."
"$PYTHON" model/create_demo_model.py

# Sample images
echo "Creating sample test images..."
"$PYTHON" sample_images/create_samples.py

# Backend env
if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo "Created backend/.env"
fi

# Frontend
cd frontend
npm install
if [ ! -f .env ]; then
  cp .env.example .env
fi
cd ..

echo ""
echo "Setup complete!"
echo "  Backend:  cd backend && uvicorn app.main:app --reload --port 8000"
echo "  Frontend: cd frontend && npm run dev"
echo "  Train:    python model/train.py (requires dataset)"
