from __future__ import annotations

from dataclasses import dataclass

from aiogram.types import Message


@dataclass
class UnifiedInboundMessage:
    user_id: str
    text: str
    source: str


def map_telegram_message(message: Message) -> UnifiedInboundMessage:
    return UnifiedInboundMessage(
        user_id=str(message.from_user.id if message.from_user else "unknown"),
        text=message.text or "",
        source="telegram",
    )
