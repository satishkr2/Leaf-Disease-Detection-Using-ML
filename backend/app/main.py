"""FastAPI application entry point."""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db
from app.routes import auth_routes, history_routes, predict_routes
from app.services.leaf_detector import leaf_detector_service
from app.services.predictor import predictor_service

# Ensure preprocessing module is importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

settings = get_settings()
PROCESSED_DIR = Path(__file__).resolve().parents[1] / settings.processed_dir
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    predictor_service.load_model()
    leaf_detector_service.load_model()

    # Seed admin user if not exists
    from sqlalchemy import select

    from app.auth import get_password_hash
    from app.database import AsyncSessionLocal
    from app.models import User

    from app.auth import verify_password

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == settings.admin_email))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                email=settings.admin_email,
                username="admin",
                hashed_password=get_password_hash(settings.admin_password),
                is_admin=True,
            )
            db.add(admin)
            await db.commit()
        elif not verify_password(settings.admin_password, admin.hashed_password):
            # Re-hash if DB has legacy passlib hashes after bcrypt migration
            admin.hashed_password = get_password_hash(settings.admin_password)
            admin.is_admin = True
            await db.commit()

    yield


app = FastAPI(
    title="Plant Leaf Disease Detection API",
    description="AI-powered plant disease detection using deep learning and image processing",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"
app.include_router(auth_routes.router, prefix=API_PREFIX)
app.include_router(predict_routes.router, prefix=API_PREFIX)
app.include_router(history_routes.router, prefix=API_PREFIX)

app.mount("/api/processed", StaticFiles(directory=str(PROCESSED_DIR)), name="processed")


@app.get("/")
async def root():
    return {
        "message": "Plant Leaf Disease Detection API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": predictor_service._model is not None,
        "leaf_detector_loaded": leaf_detector_service._model is not None,
    }
