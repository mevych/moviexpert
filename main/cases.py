import random

from .models import Movie

TIERS = [
    {"key": "gold", "label": "Золото", "share": 0.02, "weight": 1},
    {"key": "covert", "label": "Тайное", "share": 0.05, "weight": 4},
    {"key": "classified", "label": "Засекреченное", "share": 0.13, "weight": 12},
    {"key": "restricted", "label": "Запрещённое", "share": 0.25, "weight": 28},
    {"key": "milspec", "label": "Армейское", "share": 0.55, "weight": 55},
]
TIER_BY_KEY = {t["key"]: t for t in TIERS}

STRIP_LEN = 60
WIN_INDEX = 52
CARD_W = 150
STEP = 160


def tier_pools():
    ids = list(Movie.objects.order_by("-tmdb_votes", "pk").values_list("pk", flat=True))
    total = len(ids)
    pools = {t["key"]: [] for t in TIERS}
    limits = []
    acc = 0.0
    for t in TIERS:
        acc += t["share"]
        limits.append(acc)
    for i, pk in enumerate(ids):
        p = i / total
        for t, limit in zip(TIERS, limits):
            if p < limit:
                pools[t["key"]].append(pk)
                break
    return pools


def _pick(pools):
    available = [t for t in TIERS if pools[t["key"]]]
    tier = random.choices(available, weights=[t["weight"] for t in available])[0]
    return random.choice(pools[tier["key"]]), tier["key"]


def open_case():
    pools = tier_pools()
    if not any(pools.values()):
        return None
    strip = [_pick(pools) for _ in range(STRIP_LEN)]
    winner_id, winner_tier = strip[WIN_INDEX]
    return {
        "winner": winner_id,
        "tier": winner_tier,
        "strip": [[pk, key] for pk, key in strip],
        "offset": random.randint(-55, 55),
    }


def stop_distance(offset):
    return WIN_INDEX * STEP + CARD_W // 2 + offset
