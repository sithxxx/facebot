"""
Validate Telegram Mini App initData.

The Mini App frontend sends `Telegram.WebApp.initData` (a URL-encoded query
string) with every request. We verify its HMAC signature against the bot
token so the caller's identity cannot be forged, then return the parsed user.

Reference: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from bot.config import TELEGRAM_BOT_TOKEN

# Reject initData older than this (anti-replay). Telegram auth_date is seconds.
MAX_AGE_SECONDS = 24 * 60 * 60


class InitDataError(Exception):
    pass


def validate_init_data(init_data: str, max_age: int = MAX_AGE_SECONDS) -> dict:
    """
    Verify the signature and freshness of a Telegram initData string.
    Returns the parsed Telegram user dict (id, username, first_name, ...).
    Raises InitDataError on any failure.
    """
    if not init_data:
        raise InitDataError("empty init_data")
    if not TELEGRAM_BOT_TOKEN:
        raise InitDataError("server missing TELEGRAM_BOT_TOKEN")

    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise InitDataError("missing hash")

    # data_check_string: all remaining fields, sorted, joined by '\n'.
    data_check_string = "\n".join(f"{k}={pairs[k]}" for k in sorted(pairs))

    secret_key = hmac.new(b"WebAppData", TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise InitDataError("bad signature")

    # Freshness check.
    auth_date = pairs.get("auth_date")
    if auth_date is not None:
        try:
            if max_age and (time.time() - int(auth_date)) > max_age:
                raise InitDataError("init_data expired")
        except ValueError:
            raise InitDataError("bad auth_date")

    user_raw = pairs.get("user")
    if not user_raw:
        raise InitDataError("no user in init_data")
    try:
        user = json.loads(user_raw)
    except json.JSONDecodeError:
        raise InitDataError("bad user json")
    if "id" not in user:
        raise InitDataError("user has no id")
    return user
