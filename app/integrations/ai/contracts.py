from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AIRequest:
    user_id: str
    text: str
    source: str


@dataclass
class AIResult:
    text: str
    confidence: float
