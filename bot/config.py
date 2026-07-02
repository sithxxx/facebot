from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL") or "https://api.deepseek.com"
OPENAI_MODEL = os.getenv("OPENAI_MODEL") or "deepseek-v4-flash"
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", 400))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
PRICE_STARS = int(os.getenv("PRICE_STARS", 250))
MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", 100))
TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/facebot")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8080))

# Public HTTPS URL of the Mini App leaderboard (the web/ service). Must be
# HTTPS for Telegram to open it as a Web App. In dev, point at a tunnel
# (cloudflared/ngrok). If unset, the /start button is omitted.
MINIAPP_URL = os.getenv("MINIAPP_URL")

# Card payment (Telegram Payments 2.0)
CARD_PROVIDER_TOKEN = os.getenv("CARD_PROVIDER_TOKEN")
CARD_PRICE_RUB = int(os.getenv("CARD_PRICE_RUB", 299))

# Crypto (CryptoBot)
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")
CRYPTO_PRICE_USDT = float(os.getenv("CRYPTO_PRICE_USDT", 3.5))

# Channel subscription
CHANNEL_ID = os.getenv("CHANNEL_ID", "@twitch_s1thxxx")

# Free-analysis whitelist: comma-separated @usernames and/or numeric user ids,
# e.g. FREE_USERS=@friend1,@friend2,123456789
# Usernames are case-insensitive; numeric ids are more reliable (usernames can
# be changed or re-taken by someone else).
_free_raw = [x.strip() for x in os.getenv("FREE_USERS", "").split(",") if x.strip()]
FREE_USER_IDS = {int(x) for x in _free_raw if x.isdigit()}
FREE_USERNAMES = {x.lstrip("@").strip().lower() for x in _free_raw if not x.isdigit()}


def is_free_user(user_id: int, username: str | None) -> bool:
    """True if this user gets analyses for free (whitelisted by id or username)."""
    if user_id in FREE_USER_IDS:
        return True
    return bool(username) and username.lower() in FREE_USERNAMES

# Validate required vars on startup
for _var, _val in [
    ("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN),
    ("DATABASE_URL", DATABASE_URL),
]:
    if not _val:
        raise RuntimeError(f"{_var} is not set in .env file")
