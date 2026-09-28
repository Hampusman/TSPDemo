"""Reproducible cities and readable search-space sizes."""
import math
import numpy as np

SIZES = (5, 10, 20, 100, 1000)
SEEDS = (42, 7, 2026)


def cities(n, seed=42):
    return np.random.default_rng(seed).uniform([4, 4], [96, 66], (n, 2))


def distances(points):
    return np.linalg.norm(points[:, None] - points[None, :], axis=2)


def length(route, matrix):
    route = np.asarray(route, dtype=int)
    return float(matrix[route, np.roll(route, -1)].sum()) if len(route) else 0.0


def number(value, decimals=0):
    """Svensk talformatering med decimalcomma och mellanslag."""
    return f"{value:,.{decimals}f}".replace(",", " ").replace(".", ",")


def tour_count(n):
    if n <= 10:
        return number(math.factorial(n - 1) // 2)
    exponent = math.lgamma(n) / math.log(10) - math.log10(2)
    power = math.floor(exponent)
    mantissa = number(10 ** (exponent - power), 2).replace(',', '{,}')
    return rf'≈ ${mantissa} \times 10^{{{power}}}$'
