from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Default to DeepSeek (OpenAI-compatible, cheap, not geoblocked in RU).
# Override via env for a different provider. Never leave base_url unset —
# an empty value makes the SDK fall back to api.openai.com.
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL") or "https://api.deepseek.com"
OPENAI_MODEL = os.getenv("OPENAI_MODEL") or "deepseek-v4-flash"
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", 400))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.7))

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in .env file")
