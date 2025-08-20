from collections.abc import Sequence
import random
from typing import TypeVar

T = TypeVar('T')


def weighted_choice(items: Sequence[T], weights: Sequence[int | float]) -> T:
    total = sum(weights)
    if total <= 0:
        # fallback: equal chance if weights invalid
        return items[0]
    r = random.uniform(0, total)
    upto = 0.0
    for it, w in zip(items, weights, strict=False):
        upto += w
        if r <= upto:
            return it
    return items[-1]  # safety
