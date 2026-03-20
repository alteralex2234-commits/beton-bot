from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MetaInboundMessage:
    sender_id: str
    text: str


def parse_meta_webhook(payload: dict) -> MetaInboundMessage | None:
    # TODO: Implement real payload parsing from Meta webhooks.
    entry = payload.get("entry")
    if not entry:
        return None
    return MetaInboundMessage(sender_id="unknown", text="stub")
