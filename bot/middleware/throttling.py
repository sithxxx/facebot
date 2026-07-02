from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache
import time

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: int = 60):
        super().__init__()
        self.rate_limit = rate_limit
        self.cache = TTLCache(maxsize=10000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Only limit messages with photo to prevent spamming the queue
        if not event.photo:
            return await handler(event, data)
            
        user_id = event.from_user.id
        if user_id in self.cache:
            await event.answer("⏱ Подожди немного перед отправкой следующего фото.")
            return
            
        self.cache[user_id] = time.time()
        return await handler(event, data)
