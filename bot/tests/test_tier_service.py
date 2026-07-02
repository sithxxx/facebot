import pytest
from bot.services.tier_service import get_tier

def test_get_tier_boundaries():
    # Sub5
    assert get_tier(1.0).name == "Sub5"
    assert get_tier(3.99).name == "Sub5"

    # LTN
    assert get_tier(4.0).name == "LTN"
    assert get_tier(4.5).name == "LTN"
    assert get_tier(4.74).name == "LTN"

    # MTN
    assert get_tier(4.75).name == "MTN"
    assert get_tier(5.0).name == "MTN"
    assert get_tier(5.49).name == "MTN"

    # HTN
    assert get_tier(5.5).name == "HTN"
    assert get_tier(6.0).name == "HTN"
    assert get_tier(6.49).name == "HTN"

    # Chadlite
    assert get_tier(6.5).name == "Chadlite"
    assert get_tier(7.0).name == "Chadlite"
    assert get_tier(7.24).name == "Chadlite"

    # Chad
    assert get_tier(7.25).name == "Chad"
    assert get_tier(8.0).name == "Chad"
    assert get_tier(8.99).name == "Chad"

    # Gigachad
    assert get_tier(9.0).name == "Gigachad"
    assert get_tier(9.5).name == "Gigachad"
    assert get_tier(10.0).name == "Gigachad"
    assert get_tier(15.0).name == "Gigachad"  # Handling unexpected very high score
