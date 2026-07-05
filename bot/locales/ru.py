"""
All user-facing strings in one file.
Never hardcode text in handlers — always import from here.
"""

WELCOME = """👤 Привет! Я делаю полный математический разбор геометрии лица.

<b>Что я умею:</b>
• Анализирую 20 метрик лица (симметрия, пропорции, глаза, нос, губы, челюсть) с σ-отклонением от нормативной базы
• Использую ML-модель красоты + геометрию для итоговой оценки от 1 до 10
• Определяю твой уровень в таблице луксмаксинга
• Присылаю подробный PDF-отчёт с персональными советами

🏆 <b>Рейтинг (мини-приложение):</b>
Каждый разбор даёт тебе балл от 1 до 10. По нему ты попадаешь в один из уровней — от Sub3 до True Adam (у девушек — до True Eve) — и встаёшь в топ пользователей своего пола. Сделаешь разбор повторно и получишь больше баллов — поднимешься выше. Открой «Рейтинг» кнопкой ниже.
"""

PHOTO_EXAMPLE_CAPTION = (
    "👆 Пример правильного фото: лицо анфас, занимает большую часть кадра, "
    "хорошее освещение, нейтральное выражение. Постарайся расположить лицо "
    "в кадре примерно так же."
)

# Sent right after WELCOME; {methods} is a bullet list of currently enabled
# payment methods (built in start.py from configured tokens).
PRICES_INFO = """💰 <b>Стоимость разбора</b>

{methods}

📸 Чтобы начать — просто пришли фото анфас: хорошее освещение, нейтральное выражение, лицо прямо в камеру. Оплата — после выбора пола.
"""

LEADERBOARD_OPTOUT_DONE = "🙈 Ты скрыт из публичного рейтинга. Вернуться: /leaderboard_optin"
LEADERBOARD_OPTIN_DONE = "🏆 Ты снова участвуешь в публичном рейтинге."

PHOTO_PROMPT = "📸 Пришли фото анфас..."
GENDER_PROMPT = "Выбери пол для сравнения с нормативной базой:"
PAYMENT_PROMPT = "Анализ стоит {price} ⭐ Telegram Stars."

STATUS_DETECTING   = "🔍 Обнаруживаю точки лица..."
STATUS_METRICS     = "📐 Считаю метрики..."
STATUS_GENERATING  = "✍️ Генерирую текст анализа... (займёт ~20 сек)"
STATUS_PDF         = "📄 Создаю PDF-отчёт..."
STATUS_DONE        = "✅ Готово!"

ERROR_GENERAL      = "😔 Что-то пошло не так. Попробуй снова — /start"
ERROR_QUEUE_FULL   = "⏳ Сейчас очень много запросов. Попробуй через минуту."
PAYMENT_SUCCESS    = "⏳ Оплата получена! Начинаю анализ..."

PHOTO_ERRORS = {
    "no_face":        "😕 Лицо не обнаружено. Пришли чёткое фото анфас при хорошем освещении.",
    "too_blurry":     "📷 Фото слишком размытое. Сделай новое фото.",
    "too_small":      "🔍 Лицо слишком маленькое в кадре. Поднеси камеру ближе.",
    "not_frontal":    "↩️ Повернись прямо к камере — сейчас слишком боковой ракурс.",
    "multiple_faces": "👥 На фото несколько лиц. Пришли фото только с твоим лицом.",
}

# Subscription
SUB_OFFER = (
    "🎁 <b>Первый анализ — бесплатно!</b>\n\n"
    "Подпишись на канал <b>@twitch_s1thxxx</b> и получи полный "
    "25-страничный PDF-разбор лица в подарок.\n\n"
    "После подписки нажми кнопку ниже 👇"
)
SUB_NOT_VERIFIED = "❌ Подписка не найдена. Подпишись и нажми проверить снова."
SUB_VERIFIED = "✅ Подписка подтверждена! Бесплатный анализ активирован 🎉"

# Payment choice
PAYMENT_CHOICE = (
    "💳 <b>Выбери способ оплаты</b>\n\n"
    "Полный анализ лица — 20 метрик, PDF на 25 страниц, советы."
)

# Crypto
CRYPTO_INVOICE_SENT = (
    "₿ <b>Счёт создан</b>\n\n"
    "Оплати по кнопке ниже. Счёт действителен <b>1 час</b>.\n"
    "После оплаты анализ запустится автоматически."
)
CRYPTO_EXPIRED = "⌛ Счёт истёк. Создать новый?"
CRYPTO_PAID = "✅ Оплата в крипте получена! Начинаю анализ..."

# Tier messages — used in get_tier_position_message()
TIER_MESSAGE_TEMPLATE = (
    "{emoji} <b>Твой ранг: {name}</b> — {name_local}\n"
    "<i>{psl_range} по шкале PSL</i>\n\n"
    "{percentile}\n\n"
    "{description}\n\n"
    "💡 <b>Как улучшить:</b>\n{how_to_improve}\n\n"
    "📊 Твой итоговый балл: <b>{score}/10</b>"
)

PRICES_METHOD_STARS = "⭐ {price} Telegram Stars"
PRICES_METHOD_CARD = "💳 {price} ₽ картой"
PRICES_METHOD_CRYPTO = "₿ {price} USDT криптовалютой"

PDF_CAPTION = "🎉 Твой персональный разбор готов!"
ANALYSIS_ERROR = "😔 Произошла ошибка при анализе."

PAY_BTN_STARS = "⭐ {price} Telegram Stars"
PAY_BTN_CARD = "💳 {price} ₽ картой"
PAY_BTN_CRYPTO = "₿ {price} USDT крипта"
PAY_BTN_CANCEL = "Отмена"
PAYMENT_CANCELLED = "Оплата отменена."

INVOICE_TITLE = "Разбор лица — полный анализ"
INVOICE_DESCRIPTION = "Подробный PDF с математическим разбором 20 метрик лица"
INVOICE_LABEL = "Анализ лица"
CRYPTO_PAY_BUTTON = "Оплатить USDT"

LANGUAGE_PROMPT = "🌐 Выбери язык / Choose your language:"
LANGUAGE_SET = "✅ Язык установлен: русский"

BTN_RESTART = "🚀 Новый разбор"

THROTTLE_MSG = "⏱ Слишком часто. Отправь фото через {sec} сек."
PROMO_ENDED = "Акция завершена — анализ теперь платный"

# PDF template labels
PDF_T = {
    "cover_title": "Анализ Геометрии Лица",
    "overall_score": "ОБЩИЙ БАЛЛ",
    "out_of_10": "ИЗ 10",
    "population_distribution": "Распределение в популяции",
    "key_strengths": "КЛЮЧЕВЫЕ СИЛЬНЫЕ СТОРОНЫ",
    "summary_title": "Сводка и Общее Впечатление",
    "geometry_profile": "Профиль геометрии лица",
    "overall_impression": "ОБЩЕЕ ВПЕЧАТЛЕНИЕ",
    "metric_label": "Метрика",
    "metric_score": "Балл метрики",
    "your_value": "ВАШ ПОКАЗАТЕЛЬ",
    "norm": "НОРМА",
    "deviation": "Отклонение в популяции",
    "influence": "ВЛИЯНИЕ",
    "advice_title": "Рекомендации по Улучшению",
    "advice_intro": (
        "Эти рекомендации основаны на метриках, показавших наибольший потенциал "
        "для визуального баланса. Небольшие изменения в стиле и ракурсах могут "
        "значительно улучшить общую гармонию."
    ),
}

GENDER_MALE = "👨 Мужской"
GENDER_FEMALE = "👩 Женский"
GENDER_CHOSEN = "Выбран пол: {gender}"
