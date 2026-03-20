from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.core.container import ServiceContainer


class ServicesMiddleware(BaseMiddleware):
    """
    Внедряет `services` в контекст обработки сообщений/коллбеков.

    Так обработчики могут принимать аргумент `services: ServiceContainer`
    и использовать зависимости (Supabase, lead-сервис, консультации и т.д.).
    """

    def __init__(self, services: ServiceContainer) -> None:
        self._services = services

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["services"] = self._services
        return await handler(event, data)

