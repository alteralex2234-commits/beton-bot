from __future__ import annotations

import re


PHONE_PATTERN = re.compile(r"^[\d\+\-\(\)\s]{6,30}$")


def is_valid_phone(value: str) -> bool:
    return bool(PHONE_PATTERN.match(value.strip()))
