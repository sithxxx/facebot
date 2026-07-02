from dataclasses import dataclass
from typing import List
from bot.locales.ru import TIER_MESSAGE_TEMPLATE

@dataclass
class TierInfo:
    slug: str            # stable id used in API urls and photo filenames
    name: str            # display name (latin, as in the lookmaxxing table)
    name_ru: str
    psl_range: str
    score_min: float
    score_max: float
    emoji: str           # still used in the bot text message after analysis
    color_hex: str
    description_ru: str
    how_to_improve_ru: str
    percentile: str


# Score bands are identical for both genders — only naming differs.
# (sub3, sub5, ltn/ltb, mtn/mtb, htn/htb, chad/stacy, true adam/true eve)
_BANDS = [
    ("sub3",      1.0, 3.0,  "😞", "#8E44AD", "Нижние 2% популяции"),
    ("sub5",      3.0, 4.0,  "😔", "#E74C3C", "Нижние 10% популяции"),
    ("lt",        4.0, 4.75, "😐", "#E67E22", "Нижние 30% популяции"),
    ("mt",        4.75, 5.5, "🙂", "#F1C40F", "Средние 50% популяции"),
    ("ht",        5.5, 6.5,  "😎", "#2ECC71", "Топ 20% популяции"),
    ("chad",      6.5, 8.5,  "👑", "#3498DB", "Топ 5% популяции"),
    ("true",      8.5, 10.0, "⚡", "#F5A623", "Топ 0.1% популяции"),
]

_MALE_NAMES = {
    "sub3": ("Sub3", "Глубоко ниже среднего"),
    "sub5": ("Sub5", "Ниже среднего"),
    "lt":   ("LTN", "Низкий нормис"),
    "mt":   ("MTN", "Средний нормис"),
    "ht":   ("HTN", "Высокий нормис"),
    "chad": ("Chad", "Чад"),
    "true": ("True Adam", "Тру Адам"),
}

_FEMALE_NAMES = {
    "sub3": ("Sub3", "Глубоко ниже среднего"),
    "sub5": ("Sub5", "Ниже среднего"),
    "lt":   ("LTB", "Низкая Бекки"),
    "mt":   ("MTB", "Средняя Бекки"),
    "ht":   ("HTB", "Высокая Бекки"),
    "chad": ("Stacy", "Стейси"),
    "true": ("True Eve", "Тру Ева"),
}

_DESCRIPTIONS = {
    "sub3": (
        "Выраженные структурные особенности лица: сильная асимметрия, "
        "ортодонтические проблемы или последствия образа жизни.",
        "Начни с фундамента: консультация ортодонта, дерматолог, нормализация "
        "сна и питания, снижение процента жира. Каждый шаг здесь даёт заметный результат."
    ),
    "sub5": (
        "Внешность ниже среднего уровня. Чаще всего это связано с выраженной "
        "асимметрией, ортодонтическими проблемами или другими структурными особенностями.",
        "Для существенного улучшения рекомендуется hardmaxxing: консультация ортодонта, "
        "работа с дерматологом, снижение процента жира. Базовый уход за собой — обязателен."
    ),
    "lt": (
        "Обычный человек низшего уровня. Большинство черт лица нормальны, "
        "но есть один-два существенных недостатка (неухоженная кожа, "
        "лишний вес на лице, неудачная стрижка).",
        "Softmaxxing творит чудеса: барбершоп, спортзал, базовый skincare. "
        "Эти три шага гарантированно переведут в следующую категорию."
    ),
    "mt": (
        "Золотая середина. Большинство здоровых ухоженных людей — это средний уровень. "
        "Лицо без отталкивающих черт, но и без выдающегося магнетизма. "
        "Статус и харизма легко компенсируют.",
        "Оцени пропорции лица, сбрось лишний вес, подбери правильный стиль. "
        "В 80% случаев этого достаточно для перехода на уровень выше."
    ),
    "ht": (
        "«Красавчик» в рамках обычной жизни. Самый привлекательный человек "
        "в офисе или университете. Есть выраженные позитивные черты: "
        "сильная линия челюсти, выразительный взгляд, хорошая симметрия.",
        "Для большинства это естественный потолок. Дальнейший рост: минимальный "
        "процент жира, идеальный skincare, стиль и постановка тела."
    ),
    "chad": (
        "Генетическая элита. Ты выигрываешь у 95% популяции просто зайдя в комнату. "
        "Лицо приближается к математическим идеалам — уровень актёров и моделей.",
        "Ты уже почти на вершине. Леан, осанка, стиль и поддержание — "
        "не растрать генетику."
    ),
    "true": (
        "Недостижимый предел. Математически совершенное лицо. "
        "Встречается у единиц на всю планету.",
        "Улучшать нечего. Ты — эталон."
    ),
}


def _build_tiers(names: dict) -> List[TierInfo]:
    tiers = []
    for slug, lo, hi, emoji, color, percentile in _BANDS:
        name, name_ru = names[slug]
        desc, improve = _DESCRIPTIONS[slug]
        tiers.append(TierInfo(
            slug=name.lower().replace(" ", "_"),
            name=name,
            name_ru=name_ru,
            psl_range=f"{lo:g} – {hi:g}",
            score_min=lo,
            score_max=hi,
            emoji=emoji,
            color_hex=color,
            description_ru=desc,
            how_to_improve_ru=improve,
            percentile=percentile,
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


def get_tier_position_message(score: float, gender: str) -> str:
    """Generates the full tier result message sent to user after PDF."""
    tier = get_tier(score, gender)
    return TIER_MESSAGE_TEMPLATE.format(
        emoji=tier.emoji,
        name=tier.name,
        name_ru=tier.name_ru,
        psl_range=tier.psl_range,
        percentile=tier.percentile,
        description_ru=tier.description_ru,
        how_to_improve_ru=tier.how_to_improve_ru,
        score=round(score, 2),
    )


def get_tier_comparison_text(score: float, gender: str) -> str:
    """
    Generates motivational comparison:
    Which tier is next and how many points away
    """
    return ""
