"""
FastAPI backend for the Telegram Mini App leaderboard.

Auth: every /api request must carry the Telegram initData in the
`Authorization: tma <initData>` header; it is HMAC-verified (web/auth.py).
Data comes from the same DB the bot writes to (bot.database.repository).
The leaderboard is fully gender-split: every listing endpoint takes
?gender=male|female, and tier taxonomies differ per gender
(bot.services.tier_service.TIERS_MALE / TIERS_FEMALE).
"""

from pathlib import Path

from fastapi import FastAPI, Depends, Header, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from bot.database import repository as repo
from bot.services.tier_service import get_tiers, get_tier
from web.auth import validate_init_data, InitDataError

app = FastAPI(title="Facebot Leaderboard", docs_url=None, redoc_url=None)

STATIC_DIR = Path(__file__).parent / "static"


def _norm_gender(gender: str) -> str:
    g = (gender or "").lower()
    if g not in ("male", "female"):
        raise HTTPException(status_code=422, detail="gender must be male or female")
    return g


def _tier_band(tier, tiers) -> tuple[float, float]:
    """[min, max) band; the top tier's bound is bumped so a perfect 10 fits."""
    top = max(t.score_max for t in tiers)
    upper = tier.score_max + 0.0001 if tier.score_max == top else tier.score_max
    return tier.score_min, upper


async def current_user(authorization: str = Header(default="")) -> dict:
    """Auth dependency: parse + verify Telegram initData from the header."""
    if not authorization.lower().startswith("tma "):
        raise HTTPException(status_code=401, detail="missing tma authorization")
    init_data = authorization[4:].strip()
    try:
        return validate_init_data(init_data)
    except InitDataError as e:
        raise HTTPException(status_code=401, detail=f"invalid init_data: {e}")


def _tier_public(tier, gender: str) -> dict:
    return {
        "slug": tier.slug,
        "name": tier.name,
        "name_full": tier.name_en,
        "photo": f"/tiers/{gender}/{tier.slug}.jpg",
        "color": tier.color_hex,
        "psl_range": tier.psl_range,
        "score_min": tier.score_min,
        "score_max": tier.score_max,
        "percentile": tier.percentile_en,
    }


@app.get("/api/leaderboard/global")
async def leaderboard_global(gender: str = Query("male"), user: dict = Depends(current_user)):
    g = _norm_gender(gender)
    rows = await repo.get_global_leaderboard(g, limit=50)
    me = await repo.get_user_rank(int(user["id"]))
    return {"gender": g, "entries": rows, "me": me}


@app.get("/api/leaderboard/tiers")
async def leaderboard_tiers(gender: str = Query("male"), user: dict = Depends(current_user)):
    g = _norm_gender(gender)
    # Highest tier first, to mirror the ranking order.
    tiers = sorted(get_tiers(g), key=lambda t: -t.score_min)
    return {"gender": g, "tiers": [_tier_public(t, g) for t in tiers]}


@app.get("/api/leaderboard/tier/{tier_slug}")
async def leaderboard_tier(tier_slug: str, gender: str = Query("male"), user: dict = Depends(current_user)):
    g = _norm_gender(gender)
    tiers = get_tiers(g)
    tier = next((t for t in tiers if t.slug == tier_slug.lower()), None)
    if tier is None:
        raise HTTPException(status_code=404, detail="unknown tier")
    lo, hi = _tier_band(tier, tiers)
    rows = await repo.get_tier_leaderboard(g, lo, hi, limit=50)
    return {"gender": g, "tier": _tier_public(tier, g), "entries": rows}


@app.get("/api/me")
async def me(user: dict = Depends(current_user)):
    rank = await repo.get_user_rank(int(user["id"]))
    if rank is None:
        return {"ranked": False}
    g = rank.get("gender") or "male"
    tier = get_tier(rank["score"], g)
    return {"ranked": True, **rank, "tier": _tier_public(tier, g)}


# Serve the Mini App frontend. Mount last so /api routes win.
if STATIC_DIR.exists():
    @app.get("/")
    async def index():
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/", StaticFiles(directory=str(STATIC_DIR)), name="static")
