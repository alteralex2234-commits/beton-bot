from __future__ import annotations

import asyncio
import logging

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.api.app import create_api_app
from app.bot.handlers.router import get_main_router
from app.bot.middlewares.error_middleware import ErrorLoggingMiddleware
from app.bot.middlewares.services_middleware import ServicesMiddleware
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.container import ServiceContainer, build_service_container


logger = logging.getLogger(__name__)


async def run_telegram_bot(container: ServiceContainer) -> None:
    settings = container.settings
    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.update.middleware(ErrorLoggingMiddleware())
    dispatcher.message.middleware(ServicesMiddleware(container))
    dispatcher.include_router(get_main_router())

    logger.info("Telegram bot started")
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


async def run_fastapi(container: ServiceContainer) -> None:
    api_app = create_api_app(container)
    config = uvicorn.Config(
        app=api_app,
        host=container.settings.app_host,
        port=container.settings.app_port,
        log_level="info",
    )
    server = uvicorn.Server(config=config)
    logger.info("FastAPI server started on %s:%s", container.settings.app_host, container.settings.app_port)
    await server.serve()


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.app_env)
    container = build_service_container(settings)

    await asyncio.gather(
        run_telegram_bot(container),
        run_fastapi(container),
    )


if __name__ == "__main__":
    asyncio.run(main())
