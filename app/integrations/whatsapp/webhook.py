from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WhatsAppInboundMessage:
    sender_id: str
    text: str


def parse_whatsapp_webhook(payload: dict) -> WhatsAppInboundMessage | None:
    # TODO: Implement real payload parsing from WhatsApp webhooks.
    if not payload:
        return None
    return WhatsAppInboundMessage(sender_id="unknown", text="stub")
