# Deployment Guide

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | `openssl rand -hex 32` |
| `DATABASE_URL` | SQLite async URL | `sqlite+aiosqlite:///./plant_disease.db` |
| `CORS_ORIGINS` | Allowed frontend origins | `https://app.vercel.app` |
| `MODEL_PATH` | Path to `.h5` model | `/app/model/saved_models/best_model.h5` |
| `ADMIN_EMAIL` | Admin seed email | `admin@plantcare.local` |
| `ADMIN_PASSWORD` | Admin seed password | Change in production! |

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API base URL |

---

## Vercel (Frontend)

1. Push repo to GitHub
2. Import project in Vercel, set root: `frontend`
3. Build: `npm run build`, Output: `dist`
4. Environment: `VITE_API_URL=https://your-api.onrender.com`
5. Add `vercel.json` rewrites for SPA:

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

---

## Render (Backend)

1. New **Web Service**, connect GitHub repo
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from table above
6. Upload model file or add build step:
   `python ../model/create_demo_model.py`

**Disk**: Enable persistent disk for `uploads/` and `processed/` if needed.

---

## Railway

Similar to Render:
- Dockerfile at `backend/Dockerfile` (build from project root)
- Set `PORT` automatically
- Mount volume for SQLite DB persistence

---

## Netlify (Frontend Alternative)

- Base directory: `frontend`
- Build: `npm run build`
- Publish: `dist`
- Env: `VITE_API_URL`
- `_redirects` file: `/* /index.html 200`

---

## Docker Production

```bash
docker-compose -f docker-compose.yml up -d --build
```

Scale tips:
- Use PostgreSQL instead of SQLite for multi-instance
- Store uploads in S3/Cloudinary
- Cache model in memory on startup (already implemented)

---

## Model Hosting Options

1. **Bundled** (recommended): Include `best_model.h5` in container (~15-50MB)
2. **S3**: Download on startup via `boto3`
3. **Hugging Face Hub**: `hf_hub_download()` in predictor service

---

## HTTPS & Webcam

Webcam requires **HTTPS** in production. Ensure:
- Vercel/Netlify provide SSL automatically
- Backend CORS includes exact frontend origin (no trailing slash mismatch)

---

## Health Checks

- Backend: `GET /health` → `{"status": "healthy", "model_loaded": true}`
- Configure Render/Railway health check path: `/health`
