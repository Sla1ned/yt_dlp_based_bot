from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from aiogram.enums import ChatType
from typing import Any, Awaitable, Callable, Dict

from database.requests import subscription_check
from database.models import User, Group
from filter.pydantic_filter import StrictURLFilter

url_filter = StrictURLFilter()

class MainMiddlewareChecker(BaseMiddleware):

    async def __call__(self,
                 handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                 event: TelegramObject,
                 data: Dict[str, Any]
                 ):

        session = data['session']
        msg: Message | None = event if isinstance(event, Message) else None

        if msg is None: return None
        if msg.text and msg.text.startswith("/"): return await handler(event, data)
        if not msg.from_user: return None

        model_type = Group if msg.chat and msg.chat.type in (ChatType.SUPERGROUP, ChatType.GROUP) else User
        model_id = msg.chat.id if msg.chat and msg.chat.type in (ChatType.SUPERGROUP, ChatType.GROUP) else msg.from_user.id

        is_subscription = await subscription_check(
            model_type= model_type,
            session = session,
            id = model_id
        )

        if not is_subscription:
            return None

        return await handler(event, data)