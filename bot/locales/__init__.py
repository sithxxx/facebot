from bot.locales import ru, en


def get_locale(lang: str | None):
    """Locale module for a user language code. Defaults to Russian."""
    return en if (lang or "").lower().startswith("en") else ru
