from dataclasses import dataclass
from typing import List
from bot.locales import get_locale

@dataclass
class TierInfo:
    slug: str            # stable id used in API urls and photo filenames
    name: str            # display name (latin, as in the lookmaxxing table)
    name_ru: str
    name_en: str
    psl_range: str
    score_min: float
    score_max: float
    emoji: str           # still used in the bot text message after analysis
    color_hex: str
    description_ru: str
    description_en: str
    how_to_improve_ru: str
    how_to_improve_en: str
    percentile_ru: str
    percentile_en: str


# Score bands are identical for both genders — only naming differs.
_BANDS = [
    ("sub3", 1.0, 3.0,  "😞", "#8E44AD", "Нижние 2% популяции",  "Bottom 2% of the population"),
    ("sub5", 3.0, 4.0,  "😔", "#E74C3C", "Нижние 10% популяции", "Bottom 10% of the population"),
    ("lt",   4.0, 4.75, "😐", "#E67E22", "Нижние 30% популяции", "Bottom 30% of the population"),
    ("mt",   4.75, 5.5, "🙂", "#F1C40F", "Средние 50% популяции","Middle 50% of the population"),
    ("ht",   5.5, 6.5,  "😎", "#2ECC71", "Топ 20% популяции",    "Top 20% of the population"),
    ("chad", 6.5, 8.5,  "👑", "#3498DB", "Топ 5% популяции",     "Top 5% of the population"),
    ("true", 8.5, 10.0, "⚡", "#F5A623", "Топ 0.1% популяции",   "Top 0.1% of the population"),
]

_MALE_NAMES = {
    "sub3": ("Sub3", "Глубоко ниже среднего", "Deep below average"),
    "sub5": ("Sub5", "Ниже среднего", "Below average"),
    "lt":   ("LTN", "Низкий нормис", "Low Tier Normie"),
    "mt":   ("MTN", "Средний нормис", "Mid Tier Normie"),
    "ht":   ("HTN", "Высокий нормис", "High Tier Normie"),
    "chad": ("Chad", "Чад", "Chad"),
    "true": ("True Adam", "Тру Адам", "True Adam"),
}

_FEMALE_NAMES = {
    "sub3": ("Sub3", "Глубоко ниже среднего", "Deep below average"),
    "sub5": ("Sub5", "Ниже среднего", "Below average"),
    "lt":   ("LTB", "Низкая Бекки", "Low Tier Becky"),
    "mt":   ("MTB", "Средняя Бекки", "Mid Tier Becky"),
    "ht":   ("HTB", "Высокая Бекки", "High Tier Becky"),
    "chad": ("Stacy", "Стейси", "Stacy"),
    "true": ("True Eve", "Тру Ева", "True Eve"),
}

_DESCRIPTIONS = {
    "sub3": (
        "Выраженные структурные особенности лица: сильная асимметрия, "
        "ортодонтические проблемы или последствия образа жизни.",
        "Pronounced structural features: strong asymmetry, orthodontic issues "
        "or lifestyle consequences.",
        "Начни с фундамента: консультация ортодонта, дерматолог, нормализация "
        "сна и питания, снижение процента жира. Каждый шаг здесь даёт заметный результат.",
        "Start with the foundation: an orthodontist consultation, a dermatologist, "
        "normalized sleep and diet, lower body fat. Every step here yields a visible result."
    ),
    "sub5": (
        "Внешность ниже среднего уровня. Чаще всего это связано с выраженной "
        "асимметрией, ортодонтическими проблемами или другими структурными особенностями.",
        "Below-average appearance. Most often linked to pronounced asymmetry, "
        "orthodontic problems or other structural features.",
        "Для существенного улучшения рекомендуется hardmaxxing: консультация ортодонта, "
        "работа с дерматологом, снижение процента жира. Базовый уход за собой — обязателен.",
        "Substantial improvement calls for hardmaxxing: an orthodontist consultation, "
        "dermatology work, lower body fat. Basic self-care is mandatory."
    ),
    "lt": (
        "Обычный человек низшего уровня. Большинство черт лица нормальны, "
        "но есть один-два существенных недостатка (неухоженная кожа, "
        "лишний вес на лице, неудачная стрижка).",
        "A regular person at the lower tier. Most facial features are normal, "
        "but there are one or two significant flaws (unkempt skin, facial fat, "
        "an unflattering haircut).",
        "Softmaxxing творит чудеса: барбершоп, спортзал, базовый skincare. "
        "Эти три шага гарантированно переведут в следующую категорию.",
        "Softmaxxing works wonders: a barbershop, the gym, basic skincare. "
        "These three steps reliably move you up a tier."
    ),
    "mt": (
        "Золотая середина. Большинство здоровых ухоженных людей — это средний уровень. "
        "Лицо без отталкивающих черт, но и без выдающегося магнетизма. "
        "Статус и харизма легко компенсируют.",
        "The golden middle. Most healthy, well-groomed people are mid tier. "
        "No off-putting features, but no outstanding magnetism either. "
        "Status and charisma easily compensate.",
        "Оцени пропорции лица, сбрось лишний вес, подбери правильный стиль. "
        "В 80% случаев этого достаточно для перехода на уровень выше.",
        "Assess your facial proportions, lose excess weight, find the right style. "
        "In 80% of cases that is enough to move up a tier."
    ),
    "ht": (
        "«Красавчик» в рамках обычной жизни. Самый привлекательный человек "
        "в офисе или университете. Есть выраженные позитивные черты: "
        "сильная линия челюсти, выразительный взгляд, хорошая симметрия.",
        "The \"good-looking one\" of everyday life. The most attractive person "
        "in the office or at university. Clear positive features: a strong "
        "jawline, expressive eyes, good symmetry.",
        "Для большинства это естественный потолок. Дальнейший рост: минимальный "
        "процент жира, идеальный skincare, стиль и постановка тела.",
        "For most people this is the natural ceiling. Further growth: minimal "
        "body fat, flawless skincare, style and posture."
    ),
    "chad": (
        "Генетическая элита. Ты выигрываешь у 95% популяции просто зайдя в комнату. "
        "Лицо приближается к математическим идеалам — уровень актёров и моделей.",
        "Genetic elite. You beat 95% of the population just by entering the room. "
        "The face approaches mathematical ideals — actor and model territory.",
        "Ты уже почти на вершине. Леан, осанка, стиль и поддержание — "
        "не растрать генетику.",
        "You are almost at the top. Stay lean, mind your posture and style — "
        "do not waste the genetics."
    ),
    "true": (
        "Недостижимый предел. Математически совершенное лицо. "
        "Встречается у единиц на всю планету.",
        "The unreachable limit. A mathematically perfect face. "
        "Found in a handful of people on the planet.",
        "Улучшать нечего. Ты — эталон.",
        "Nothing to improve. You are the benchmark."
    ),
}


def _build_tiers(names: dict) -> List[TierInfo]:
    tiers = []
    for slug, lo, hi, emoji, color, perc_ru, perc_en in _BANDS:
        name, name_ru, name_en = names[slug]
        desc_ru, desc_en, improve_ru, improve_en = _DESCRIPTIONS[slug]
        tiers.append(TierInfo(
            slug=name.lower().replace(" ", "_"),
            name=name,
            name_ru=name_ru,
            name_en=name_en,
            psl_range=f"{lo:g} – {hi:g}",
            score_min=lo,
            score_max=hi,
            emoji=emoji,
            color_hex=color,
            description_ru=desc_ru,
            description_en=desc_en,
            how_to_improve_ru=improve_ru,
            how_to_improve_en=improve_en,
            percentile_ru=perc_ru,
            percentile_en=perc_en,
        ))
    return tiers


TIERS_MALE: List[TierInfo] = _build_tiers(_MALE_NAMES)
TIERS_FEMALE: List[TierInfo] = _build_tiers(_FEMALE_NAMES)

# Backwards-compatible alias (male taxonomy) for any legacy import.
TIERS = TIERS_MALE


def get_tiers(gender: str) -> List[TierInfo]:
    return TIERS_FEMALE if (gender or "").lower() == "female" else TIERS_MALE


def get_tier(overall_score: float, gender: str = "male") -> TierInfo:
    """Returns TierInfo for a score. Scores below the first band fall into it."""
    tiers = get_tiers(gender)
    for tier in reversed(tiers):
        if overall_score >= tier.score_min:
            return tier
    return tiers[0]


def get_tier_position_message(score: float, gender: str, lang: str = "ru") -> str:
    """Generates the full tier result message sent to user after PDF."""
    tier = get_tier(score, gender)
    L = get_locale(lang)
    is_en = (lang or "").startswith("en")
    return L.TIER_MESSAGE_TEMPLATE.format(
        emoji=tier.emoji,
        name=tier.name,
        name_local=tier.name_en if is_en else tier.name_ru,
        psl_range=tier.psl_range,
        percentile=tier.percentile_en if is_en else tier.percentile_ru,
        description=tier.description_en if is_en else tier.description_ru,
        how_to_improve=tier.how_to_improve_en if is_en else tier.how_to_improve_ru,
        score=round(score, 2),
    )
