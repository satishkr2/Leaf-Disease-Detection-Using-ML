"""Pydantic request/response schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionResponse(BaseModel):
    id: Optional[int] = None
    disease_name: str
    confidence: float
    description: str
    symptoms: str
    causes: str
    prevention: str
    prescription: str
    processed_image_url: Optional[str] = None
    preprocessing_steps: List[str] = []
    top_predictions: List[Dict[str, Any]] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HistoryItem(BaseModel):
    id: int
    disease_name: str
    confidence: float
    image_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    message: str
    language: str = "en"


class ChatResponse(BaseModel):
    reply: str


class AdminStats(BaseModel):
    total_users: int
    total_predictions: int
    predictions_today: int
    disease_distribution: Dict[str, int]
