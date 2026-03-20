from __future__ import annotations

import logging


def setup_logging(app_env: str) -> None:
    level = logging.DEBUG if app_env.lower() in {"dev", "local"} else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
