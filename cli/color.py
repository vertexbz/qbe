from __future__ import annotations

import random


def randomcolorpool(seed=9):
    pool = list(range(24, 230 + 1))
    random.Random(seed).shuffle(pool)
    for banned in {52, 56, 88, 118, 124, 160, 196, 92, 197, 165}:
        pool.remove(banned)
    return pool


def tokenbased_randomcolorpool(seed=9):
    pool = randomcolorpool(seed)
    known = dict()

    def inner(token: str):
        if token not in known:
            known[token] = pool.pop()

        return known[token]

    return inner

def hashbased_randomcolorpool(seed=9):
    pool = randomcolorpool(seed)

    def inner(token: str):
        h = sum(map(ord, token)) % len(pool)
        return pool[h]

    return inner


name_color = hashbased_randomcolorpool(5456)
