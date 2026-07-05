import os

from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, FSInputFile, ReplyKeyboardMarkup, KeyboardButton,
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from bot.states.user_states import AnalysisFlow
from bot.database import repository
from bot.locales import ru, en, get_locale
from bot.config import (
    MINIAPP_URL, PRICE_STARS, CARD_PRICE_RUB, CRYPTO_PRICE_USDT,
    CARD_PROVIDER_TOKEN, CRYPTOBOT_TOKEN,
)

router = Router()

# Example selfie shown after the welcome (correct face framing).
EXAMPLE_PHOTO = "example_photo.jpg"

BTN_LEADERBOARD = {"ru": "🏆 Открыть рейтинг", "en": "🏆 Open rating"}


def _language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
    ]])


def _restart_keyboard(L) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=L.BTN_RESTART)]],
        resize_keyboard=True,
        is_persistent=True,
    )


def _leaderboard_keyboard(lang: str) -> InlineKeyboardMarkup | None:
    """Inline keyboard with the Mini App button — only if a HTTPS URL is set."""
    if not MINIAPP_URL:
        return None
    label = BTN_LEADERBOARD.get(lang, BTN_LEADERBOARD["ru"])
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=label, web_app=WebAppInfo(url=MINIAPP_URL))
    ]])


def _prices_message(L) -> str:
    """Price list mirroring the payment keyboard: only enabled methods shown."""
    lines = [L.PRICES_METHOD_STARS.format(price=PRICE_STARS)]
    if CARD_PROVIDER_TOKEN:
        lines.append(L.PRICES_METHOD_CARD.format(price=CARD_PRICE_RUB))
    if CRYPTOBOT_TOKEN:
        lines.append(L.PRICES_METHOD_CRYPTO.format(price=CRYPTO_PRICE_USDT))
    return L.PRICES_INFO.format(methods="\n".join(lines))


async def _send_welcome_flow(message: Message, state: FSMContext, lang: str):
    """Welcome + prices + photo example, in the user's language."""
    L = get_locale(lang)
    await message.answer(L.WELCOME, reply_markup=_leaderboard_keyboard(lang))
    await message.answer(_prices_message(L), reply_markup=_restart_keyboard(L))
    if os.path.exists(EXAMPLE_PHOTO):
        await message.answer_photo(
            photo=FSInputFile(EXAMPLE_PHOTO),
            caption=L.PHOTO_EXAMPLE_CAPTION,
        )
    await state.set_state(AnalysisFlow.waiting_for_photo)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await repository.upsert_user(
        user_id, message.from_user.username, message.from_user.first_name
    )

    # New users (or anyone without a language yet) pick a language first.
    if not user.lang:
        await message.answer(ru.LANGUAGE_PROMPT, reply_markup=_language_keyboard())
        return

    await _send_welcome_flow(message, state, user.lang)


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]
    if lang not in ("ru", "en"):
        lang = "ru"
    await repository.set_user_lang(callback.from_user.id, lang)
    L = get_locale(lang)
    await callback.answer()
    await callback.message.edit_text(L.LANGUAGE_SET)
    await _send_welcome_flow(callback.message, state, lang)


@router.message(Command("language"))
async def cmd_language(message: Message):
    """Change language at any time."""
    await message.answer(ru.LANGUAGE_PROMPT, reply_markup=_language_keyboard())


@router.message(F.text.in_({ru.BTN_RESTART, en.BTN_RESTART}))
async def btn_restart(message: Message, state: FSMContext):
    """The persistent keyboard button behaves exactly like /start."""
    await cmd_start(message, state)


@router.message(Command("leaderboard_optout"))
async def cmd_optout(message: Message):
    L = get_locale(await repository.get_user_lang(message.from_user.id))
    await repository.set_leaderboard_visibility(message.from_user.id, False)
    await message.answer(L.LEADERBOARD_OPTOUT_DONE)


@router.message(Command("leaderboard_optin"))
async def cmd_optin(message: Message):
    L = get_locale(await repository.get_user_lang(message.from_user.id))
    await repository.set_leaderboard_visibility(message.from_user.id, True)
    await message.answer(L.LEADERBOARD_OPTIN_DONE)
