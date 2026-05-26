"""Prediction and upload API routes."""
from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_optional
from app.config import get_settings
from app.database import get_db
from app.models import Prediction, User
from app.schemas import ChatMessage, ChatResponse, PredictionResponse
from app.services.chatbot import get_chat_response
from app.services.pdf_service import generate_prediction_pdf
from app.services.leaf_detector import leaf_detector_service
from app.services.predictor import predictor_service

NO_LEAF_MESSAGE = (
    "No plant leaf detected in this image. "
    "Please upload a clear, close-up photo of a single plant leaf on a plain background."
)

router = APIRouter(tags=["Prediction"])
settings = get_settings()

UPLOAD_DIR = Path(__file__).resolve().parents[2] / settings.uploads_dir
PROCESSED_DIR = Path(__file__).resolve().parents[2] / settings.processed_dir
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def ensure_leaf_in_image(image_path: str) -> None:
    """Reject images that do not contain a detectable plant leaf."""
    check = leaf_detector_service.check_image(image_path)
    if not check["is_leaf"]:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "NO_LEAF_DETECTED",
                "message": NO_LEAF_MESSAGE,
                "confidence": check["confidence"],
                "detected_as": check["label"],
                "method": check["method"],
            },
        )


def validate_image(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    validate_image(file.filename or "image.jpg")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    file_id = str(uuid.uuid4())
    ext = Path(file.filename or "img.jpg").suffix.lower()
    save_path = UPLOAD_DIR / f"{file_id}{ext}"
    with open(save_path, "wb") as f:
        f.write(content)

    return {"filename": file.filename, "path": str(save_path), "file_id": file_id}


@router.post("/predict", response_model=PredictionResponse)
async def predict_disease(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    validate_image(file.filename or "image.jpg")
    content = await file.read()
    if len(content) < 1000:
        raise HTTPException(status_code=400, detail="Image file too small or corrupt")

    file_id = str(uuid.uuid4())
    ext = Path(file.filename or "img.jpg").suffix.lower()
    save_path = UPLOAD_DIR / f"{file_id}{ext}"
    with open(save_path, "wb") as f:
        f.write(content)

    ensure_leaf_in_image(str(save_path))

    try:
        result = predictor_service.predict(str(save_path), str(PROCESSED_DIR))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}") from e

    prediction = Prediction(
        user_id=current_user.id if current_user else None,
        disease_name=result["disease_name"],
        confidence=result["confidence"],
        image_path=str(save_path),
        processed_image_path=result.get("processed_image_path"),
        description=result["description"],
        symptoms=result["symptoms"],
        causes=result["causes"],
        prevention=result["prevention"],
        prescription=result["prescription"],
    )
    db.add(prediction)
    await db.commit()
    await db.refresh(prediction)

    processed_url = None
    if result.get("processed_image_path"):
        proc_name = Path(result["processed_image_path"]).name
        processed_url = f"/api/processed/{proc_name}"

    return PredictionResponse(
        id=prediction.id,
        disease_name=result["disease_name"],
        confidence=result["confidence"],
        description=result["description"],
        symptoms=result["symptoms"],
        causes=result["causes"],
        prevention=result["prevention"],
        prescription=result["prescription"],
        processed_image_url=processed_url,
        preprocessing_steps=result.get("preprocessing_steps", []),
        top_predictions=result.get("top_predictions", []),
        created_at=prediction.created_at,
    )


@router.post("/predict/webcam", response_model=PredictionResponse)
async def predict_webcam(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    return await predict_disease(file=file, db=db, current_user=current_user)


@router.post("/chat", response_model=ChatResponse)
async def farming_chat(msg: ChatMessage):
    reply = get_chat_response(msg.message, msg.language)
    return ChatResponse(reply=reply)


@router.get("/report/{prediction_id}")
async def download_report(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    from sqlalchemy import select

    result = await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    pred = result.scalar_one_or_none()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    if current_user and pred.user_id and pred.user_id != current_user.id:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")

    data = {
        "disease_name": pred.disease_name,
        "confidence": pred.confidence,
        "description": pred.description or "",
        "symptoms": pred.symptoms or "",
        "causes": pred.causes or "",
        "prevention": pred.prevention or "",
        "prescription": pred.prescription or "",
    }
    username = current_user.username if current_user else "Guest"
    pdf_bytes = generate_prediction_pdf(data, username)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=plant_report_{prediction_id}.pdf"
        },
    )
