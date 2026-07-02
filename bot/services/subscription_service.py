import logging
from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from bot.config import CHANNEL_ID

logger = logging.getLogger(__name__)

CHANNEL_USERNAME = "@twitch_s1thxxx"

async def check_subscription(bot: Bot, user_id: int) -> bool:
    """
    Checks if user is subscribed to CHANNEL_ID.
    """
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.warning(f"Failed to check subscription for user {user_id}: {e}. Bot may not be admin in {CHANNEL_ID}.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking subscription: {e}")
        return False

async def get_channel_invite_link() -> str:
    """Returns t.me/twitch_s1thxxx"""
    return "https://t.me/twitch_s1thxxx"
