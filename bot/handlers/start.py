import os

from aiogram import Router
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, FSInputFile
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from bot.states.user_states import AnalysisFlow
from bot.database import repository
from bot.locales import ru
from bot.config import (
    MINIAPP_URL, PRICE_STARS, CARD_PRICE_RUB, CRYPTO_PRICE_USDT,
    CARD_PROVIDER_TOKEN, CRYPTOBOT_TOKEN,
)

router = Router()

# Example selfie shown after the welcome (correct face framing).
EXAMPLE_PHOTO = "example_photo.jpg"


def _prices_message() -> str:
    """Price list mirroring the payment keyboard: only enabled methods shown."""
    lines = [f"⭐ {PRICE_STARS} Telegram Stars"]
    if CARD_PROVIDER_TOKEN:
        lines.append(f"💳 {CARD_PRICE_RUB} ₽ картой")
    if CRYPTOBOT_TOKEN:
        lines.append(f"₿ {CRYPTO_PRICE_USDT} USDT криптовалютой")
    return ru.PRICES_INFO.format(methods="\n".join(lines))


def _leaderboard_keyboard() -> InlineKeyboardMarkup | None:
    """Inline keyboard with the Mini App button — only if a HTTPS URL is set."""
    if not MINIAPP_URL:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🏆 Открыть рейтинг", web_app=WebAppInfo(url=MINIAPP_URL))
    ]])


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # 1. Upsert user in DB
    await repository.upsert_user(user_id, username, first_name)

    # 2. Send the detailed welcome (bot capabilities + rating system) with the
    #    Mini App button. Sent as text (not a photo caption) so the full
    #    description isn't truncated by the 1024-char caption limit.
    await message.answer(ru.WELCOME, reply_markup=_leaderboard_keyboard())

    # 3. Follow up with the price list + photo call-to-action.
    await message.answer(_prices_message())

    # 4. Example photo showing the expected face framing.
    if os.path.exists(EXAMPLE_PHOTO):
        await message.answer_photo(
            photo=FSInputFile(EXAMPLE_PHOTO),
            caption=ru.PHOTO_EXAMPLE_CAPTION,
        )

    # 5. Set state
    await state.set_state(AnalysisFlow.waiting_for_photo)


@router.message(Command("leaderboard_optout"))
async def cmd_optout(message: Message):
    await repository.set_leaderboard_visibility(message.from_user.id, False)
    await message.answer(ru.LEADERBOARD_OPTOUT_DONE)


@router.message(Command("leaderboard_optin"))
async def cmd_optin(message: Message):
    await repository.set_leaderboard_visibility(message.from_user.id, True)
    await message.answer(ru.LEADERBOARD_OPTIN_DONE)
