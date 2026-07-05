"""
English locale — mirrors ru.py key-for-key.
Never hardcode text in handlers — always import from locales.
"""

WELCOME = """👤 Hi! I do a full mathematical analysis of your facial geometry.

<b>What I can do:</b>
• Analyze 20 facial metrics (symmetry, proportions, eyes, nose, lips, jaw) with σ-deviation from the normative base
• Combine an ML beauty model with geometry for a final score from 1 to 10
• Determine your tier in the lookmaxxing table
• Send a detailed PDF report with personalized advice

🏆 <b>Rating (Mini App):</b>
Every analysis gives you a score from 1 to 10. It places you in one of the tiers — from Sub3 to True Adam (True Eve for girls) — and puts you on the leaderboard for your gender. Get a higher score on a repeat analysis and you move up. Open "Rating" with the button below.
"""

PHOTO_EXAMPLE_CAPTION = (
    "👆 Example of a good photo: face straight to the camera, filling most of "
    "the frame, good lighting, neutral expression. Try to frame your face "
    "roughly the same way."
)

# Sent right after WELCOME; {methods} is a bullet list of currently enabled
# payment methods (built in start.py from configured tokens).
PRICES_INFO = """💰 <b>Analysis price</b>

{methods}

📸 To begin — just send a front-facing photo: good lighting, neutral expression, face straight to the camera. Payment comes after choosing your gender.
"""

PRICES_METHOD_STARS = "⭐ {price} Telegram Stars"
PRICES_METHOD_CARD = "💳 {price} ₽ by card"
PRICES_METHOD_CRYPTO = "₿ {price} USDT in crypto"

LEADERBOARD_OPTOUT_DONE = "🙈 You are hidden from the public leaderboard. Return: /leaderboard_optin"
LEADERBOARD_OPTIN_DONE = "🏆 You are back on the public leaderboard."

PHOTO_PROMPT = "📸 Send a front-facing photo..."
GENDER_PROMPT = "Choose your gender for comparison with the normative base:"
PAYMENT_PROMPT = "The analysis costs {price} ⭐ Telegram Stars."

STATUS_DETECTING   = "🔍 Detecting facial landmarks..."
STATUS_METRICS     = "📐 Computing metrics..."
STATUS_GENERATING  = "✍️ Generating the analysis text... (~20 sec)"
STATUS_PDF         = "📄 Building the PDF report..."
STATUS_DONE        = "✅ Done!"

ERROR_GENERAL      = "😔 Something went wrong. Try again — /start"
ERROR_QUEUE_FULL   = "⏳ Too many requests right now. Try again in a minute."
PAYMENT_SUCCESS    = "⏳ Payment received! Starting the analysis..."

PDF_CAPTION = "🎉 Your personal analysis is ready!"

PHOTO_ERRORS = {
    "no_face":        "😕 No face detected. Send a clear front-facing photo in good lighting.",
    "too_blurry":     "📷 The photo is too blurry. Take a new one.",
    "too_small":      "🔍 The face is too small in the frame. Move the camera closer.",
    "not_frontal":    "↩️ Face the camera directly — the current angle is too much of a profile.",
    "multiple_faces": "👥 There are several faces in the photo. Send a photo with only your face.",
}

# Subscription (legacy promo — kept for old buttons)
SUB_OFFER = (
    "🎁 <b>First analysis — free!</b>\n\n"
    "Subscribe to <b>@twitch_s1thxxx</b> and get a full "
    "PDF face analysis as a gift.\n\n"
    "After subscribing, press the button below 👇"
)
SUB_NOT_VERIFIED = "❌ Subscription not found. Subscribe and press check again."
SUB_VERIFIED = "✅ Subscription confirmed! Free analysis activated 🎉"

# Payment choice
PAYMENT_CHOICE = (
    "💳 <b>Choose a payment method</b>\n\n"
    "Full face analysis — 20 metrics, a detailed PDF report, advice."
)

PAY_BTN_STARS = "⭐ {price} Telegram Stars"
PAY_BTN_CARD = "💳 {price} ₽ by card"
PAY_BTN_CRYPTO = "₿ {price} USDT crypto"
PAY_BTN_CANCEL = "Cancel"
PAYMENT_CANCELLED = "Payment cancelled."

INVOICE_TITLE = "Face analysis — full report"
INVOICE_DESCRIPTION = "Detailed PDF with a mathematical analysis of 20 facial metrics"
INVOICE_LABEL = "Face analysis"

# Crypto
CRYPTO_INVOICE_SENT = (
    "₿ <b>Invoice created</b>\n\n"
    "Pay using the button below. The invoice is valid for <b>1 hour</b>.\n"
    "The analysis starts automatically after payment."
)
CRYPTO_PAY_BUTTON = "Pay USDT"
CRYPTO_EXPIRED = "⌛ The invoice expired. Create a new one?"
CRYPTO_PAID = "✅ Crypto payment received! Starting the analysis..."

ANALYSIS_ERROR = "😔 An error occurred during the analysis."

# Tier messages — used in get_tier_position_message()
TIER_MESSAGE_TEMPLATE = (
    "{emoji} <b>Your rank: {name}</b> — {name_local}\n"
    "<i>{psl_range} on the PSL scale</i>\n\n"
    "{percentile}\n\n"
    "{description}\n\n"
    "💡 <b>How to improve:</b>\n{how_to_improve}\n\n"
    "📊 Your final score: <b>{score}/10</b>"
)

# Language picker (shown bilingual before a language is chosen)
LANGUAGE_PROMPT = "🌐 Choose your language / Выбери язык:"
LANGUAGE_SET = "✅ Language set: English"

BTN_RESTART = "🚀 New analysis"

THROTTLE_MSG = "⏱ Too fast. Send the photo in {sec} sec."
PROMO_ENDED = "The promo has ended — the analysis is now paid"

# PDF template labels
PDF_T = {
    "cover_title": "Facial Geometry Analysis",
    "overall_score": "OVERALL SCORE",
    "out_of_10": "OUT OF 10",
    "population_distribution": "Distribution in the population",
    "key_strengths": "KEY STRENGTHS",
    "summary_title": "Summary & Overall Impression",
    "geometry_profile": "Facial geometry profile",
    "overall_impression": "OVERALL IMPRESSION",
    "metric_label": "Metric",
    "metric_score": "Metric score",
    "your_value": "YOUR VALUE",
    "norm": "NORM",
    "deviation": "Deviation in the population",
    "influence": "IMPACT",
    "advice_title": "Improvement Recommendations",
    "advice_intro": (
        "These recommendations are based on the metrics with the highest "
        "potential for visual balance. Small changes in style and angles "
        "can significantly improve overall harmony."
    ),
}

GENDER_MALE = "👨 Male"
GENDER_FEMALE = "👩 Female"
GENDER_CHOSEN = "Gender selected: {gender}"
