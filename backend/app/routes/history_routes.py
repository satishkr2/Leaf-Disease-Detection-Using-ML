"""Prediction history and admin API routes."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin, require_user
from app.database import get_db
from app.models import Prediction, User
from app.schemas import AdminStats, HistoryItem, PredictionResponse

router = APIRouter(tags=["History"])


@router.get("/history", response_model=List[HistoryItem])
async def get_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_user),
):
    result = await db.execute(
        select(Prediction)
        .where(Prediction.user_id == user.id)
        .order_by(Prediction.created_at.desc())
        .limit(limit)
    )
    predictions = result.scalars().all()
    return predictions


@router.get("/history/{prediction_id}", response_model=PredictionResponse)
async def get_prediction_detail(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_user),
):
    result = await db.execute(
        select(Prediction).where(
            Prediction.id == prediction_id, Prediction.user_id == user.id
        )
    )
    pred = result.scalar_one_or_none()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    processed_url = None
    if pred.processed_image_path:
        from pathlib import Path

        processed_url = f"/api/processed/{Path(pred.processed_image_path).name}"

    return PredictionResponse(
        id=pred.id,
        disease_name=pred.disease_name,
        confidence=pred.confidence,
        description=pred.description or "",
        symptoms=pred.symptoms or "",
        causes=pred.causes or "",
        prevention=pred.prevention or "",
        prescription=pred.prescription or "",
        processed_image_url=processed_url,
        created_at=pred.created_at,
    )


@router.get("/admin/stats", response_model=AdminStats)
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    users_count = await db.scalar(select(func.count(User.id)))
    preds_count = await db.scalar(select(func.count(Prediction.id)))

    today = datetime.utcnow() - timedelta(days=1)
    today_count = await db.scalar(
        select(func.count(Prediction.id)).where(Prediction.created_at >= today)
    )

    dist_result = await db.execute(
        select(Prediction.disease_name, func.count(Prediction.id)).group_by(
            Prediction.disease_name
        )
    )
    distribution = {row[0]: row[1] for row in dist_result.all()}

    return AdminStats(
        total_users=users_count or 0,
        total_predictions=preds_count or 0,
        predictions_today=today_count or 0,
        disease_distribution=distribution,
    )


@router.get("/admin/predictions", response_model=List[HistoryItem])
async def admin_all_predictions(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(
        select(Prediction).order_by(Prediction.created_at.desc()).limit(limit)
    )
    return result.scalars().all()
