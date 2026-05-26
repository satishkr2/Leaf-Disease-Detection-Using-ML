# Plant Leaf Disease Detection System

A production-ready full-stack AI web application that detects plant leaf diseases using **Deep Learning (CNN + Transfer Learning)**, **OpenCV image processing**, and a modern **React + FastAPI** stack.

![Tech Stack](https://img.shields.io/badge/React-18-61DAFB) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688) ![TensorFlow](https://img.shields.io/badge/TensorFlow-2.18-FF6F00) ![OpenCV](https://img.shields.io/badge/OpenCV-4.10-5C3EE8)

## Features

| Category | Features |
|----------|----------|
| **ML/DL** | CNN, MobileNetV2, ResNet50, EfficientNetB0 comparison, metrics, confusion matrix |
| **Leaf gate** | Binary Leaf / Non-leaf detector runs **before** disease prediction |
| **CV** | Resize, denoise, background clean, CLAHE, Canny edges, HSV leaf segmentation |
| **Frontend** | Landing page, drag-drop upload, webcam, dark mode, i18n (EN/ES/HI), Framer Motion |
| **Backend** | REST API, JWT auth, SQLite, PDF reports, chatbot, admin dashboard |
| **Extra** | Prediction history, voice explanation, Docker, cloud deployment guides |

## Project Structure

```
plant-leaf-disease-detection/
├── frontend/                 # React + Vite + Tailwind + Framer Motion
│   ├── src/
│   │   ├── components/       # Navbar, ImageUpload, PredictionResult, Chatbot...
│   │   ├── pages/            # Home, Detect, Webcam, History, Admin...
│   │   ├── context/          # Auth, Theme, Language
│   │   └── utils/            # API client, i18n
├── backend/                  # FastAPI application
│   └── app/
│       ├── routes/           # auth, predict, history
│       ├── services/           # predictor, disease info, PDF, chatbot
│       └── models.py         # SQLAlchemy ORM
├── model/                    # Training & inference
│   ├── train.py              # Compare 3 transfer learning models
│   ├── create_demo_model.py  # Quick-start model
│   └── data/disease_info.json
├── preprocessing/            # OpenCV pipeline
├── dataset/plantvillage/     # Training data (PlantVillage)
├── sample_images/            # Test images
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.9+ (3.10+ recommended)
- Node.js 18+
- (Optional) CUDA for faster training

### 1. Automated Setup

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Manual Setup

```bash
# Backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp backend/.env.example backend/.env
python model/create_demo_model.py
python sample_images/create_samples.py

# Frontend
cd frontend && npm install && cp .env.example .env
```

### 3. Run Application

**Terminal 1 – Backend:**
```bash
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 – Frontend:**
```bash
cd frontend
npm run dev
```

Open **http://localhost:5173**

### Default Admin Account

| Field | Value |
|-------|-------|
| Email | `admin@plantcare.local` |
| Password | `admin123` |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | User registration |
| POST | `/api/login` | JWT login (form: username=email, password) |
| GET | `/api/me` | Current user |
| POST | `/api/upload` | Upload image only |
| POST | `/api/predict` | Upload + predict disease |
| POST | `/api/predict/webcam` | Webcam frame prediction |
| GET | `/api/history` | User prediction history |
| GET | `/api/report/{id}` | Download PDF report |
| POST | `/api/chat` | Farming chatbot |
| GET | `/api/admin/stats` | Admin statistics |
| GET | `/health` | Health check |

API docs: **http://localhost:8000/docs**

## Training the Model

### Dataset Setup (PlantVillage)

1. Download from [Kaggle PlantVillage](https://www.kaggle.com/datasets/abdallahalidev/plantvillage)
2. Copy these folders to `dataset/plantvillage/`:
   - `Tomato___Early_blight`
   - `Tomato___Late_blight`
   - `Potato___Early_blight`
   - `Potato___healthy`
   - `Pepper__bell___Bacterial_spot`
   - `Tomato___healthy`

Or try auto-download:
```bash
python model/download_dataset.py
```

### Train Leaf / Non-Leaf Detector

```bash
python model/leaf_detector/prepare_dataset.py
python model/leaf_detector/train.py
# Or one command:
python model/leaf_detector/create_demo_model.py
```

Add real non-leaf photos (faces, sky, objects) to `dataset/leaf_binary/non_leaf/` for best results.

### Train & Compare Disease Models

```bash
python model/train.py
```

This trains **MobileNetV2**, **ResNet50**, and **EfficientNetB0**, compares F1 scores, and saves:
- `model/saved_models/best_model.h5`
- `model/saved_models/class_labels.json`
- `model/plots/*_training.png`, `*_confusion_matrix.png`

## Image Preprocessing Pipeline

Applied before every prediction (`preprocessing/pipeline.py`):

1. Resize (256×256)
2. Noise reduction (fastNlMeans)
3. Background cleaning (Otsu mask)
4. Color normalization (CLAHE)
5. Edge detection (Canny)
6. Leaf segmentation (HSV green mask)
7. Final resize (224×224 for model)

## Docker

```bash
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

## Deployment

### Frontend (Vercel / Netlify)

```bash
cd frontend
npm run build
```

Environment variable:
```
VITE_API_URL=https://your-backend.onrender.com
```

Deploy `dist/` folder. Configure SPA redirects to `index.html`.

### Backend (Render / Railway)

1. Set root directory to `backend`
2. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Environment variables:
   ```
   SECRET_KEY=<strong-random-key>
   CORS_ORIGINS=https://your-frontend.vercel.app
   MODEL_PATH=/app/model/saved_models/best_model.h5
   ```
4. Upload `model/saved_models/best_model.h5` or build during deploy

### Model Hosting

- Bundle `.h5` with backend container (recommended)
- Or use cloud storage (S3) and download on startup

## Supported Disease Classes

- Tomato Early Blight
- Tomato Late Blight
- Potato Early Blight
- Potato Healthy
- Pepper Bell Bacterial Spot
- Tomato Healthy

## Tech Stack Summary

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, Tailwind CSS, Framer Motion, Recharts |
| Backend | FastAPI, SQLAlchemy, SQLite, JWT |
| ML | TensorFlow/Keras, Transfer Learning |
| CV | OpenCV (opencv-python-headless) |
| Reports | ReportLab PDF |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Model not loaded | Run `python model/create_demo_model.py` |
| CORS errors | Add frontend URL to `CORS_ORIGINS` in backend `.env` |
| Camera not working | Use HTTPS in production; allow browser permissions |
| Low accuracy | Train with full PlantVillage dataset via `model/train.py` |

## License

MIT License – Educational and research use.

## Acknowledgments

- [PlantVillage Dataset](https://www.kaggle.com/datasets/abdallahalidev/plantvillage)
- TensorFlow Applications (MobileNetV2, ResNet50, EfficientNetB0)
