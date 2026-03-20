from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class LeadCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=6, max_length=30)
    volume: str = Field(min_length=1, max_length=50)
    desired_product: str = Field(min_length=2, max_length=160)
    comment: str | None = Field(default=None, max_length=500)
    source: str = Field(default="telegram", max_length=40)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LeadStored(LeadCreate):
    id: int | None = None
