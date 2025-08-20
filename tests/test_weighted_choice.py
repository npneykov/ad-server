from collections import Counter
import random

from utils import weighted_choice


def test_weighted_choice_distribution():
    random.seed(123)
    items = ['A', 'B', 'C']
    weights = [1, 3, 6]  # A 10%, B 30%, C 60%
    N = 5000
    counts = Counter(weighted_choice(items, weights) for _ in range(N))
    a, b, c = counts['A'] / N, counts['B'] / N, counts['C'] / N
    # allow ~5% tolerance
    assert 0.05 <= a <= 0.15
    assert 0.25 <= b <= 0.35
    assert 0.55 <= c <= 0.65
