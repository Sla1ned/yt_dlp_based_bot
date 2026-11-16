from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from handlers.main_handler import rt as main_rt
from handlers.payment_handler import rt as payment_rt

from database.db import create_engine_and_session
from database.models import Base

from middleware.main_middleware import MainMiddlewareChecker
from middleware.session_middleware import SessionMiddleware

from settings import settings
from redis.asyncio import Redis
from loguru import logger
import asyncio

TOKEN: str = settings.bot_token.get_secret_value() #type: ignore
db_url: str = settings.db_url #type: ignore
redis_url: str = settings.redis_url #type: ignore

redis = Redis.from_url(redis_url)
storage = RedisStorage(redis)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
engine, session_pool = create_engine_and_session(db_url=db_url)

dp = Dispatcher(storage=storage)
dp.include_routers(main_rt, payment_rt)
dp.message.outer_middleware(SessionMiddleware(session_pool))
dp.message.outer_middleware(MainMiddlewareChecker())

async def main():
    logger.info('Starting bot...')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await dp.start_polling(bot)
    await redis.aclose()
    await engine.dispose()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        logger.warning('Closing down bot...')