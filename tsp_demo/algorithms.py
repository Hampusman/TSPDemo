"""Exact small-instance solver and bounded, incremental heuristic search."""
import numpy as np


def nearest_neighbour(matrix):
    n = len(matrix)
    remaining = np.ones(n, dtype=bool)
    route = [0]
    remaining[0] = False
    for _ in range(n - 1):
        city = int(np.argmin(np.where(remaining, matrix[route[-1]], np.inf)))
        route.append(city)
        remaining[city] = False
    return route


def held_karp(matrix):
    """Fix city 0; store shortest paths for each visited subset and endpoint."""
    n = len(matrix)
    if n > 10:
        raise ValueError('Exact solving is limited to 10 cities.')
    dp = {(1 << j, j): (matrix[0, j], 0) for j in range(1, n)}
    for mask in range(2, 1 << n, 2):
        for j in range(1, n):
            previous = mask ^ (1 << j)
            if not mask & (1 << j) or previous == 0:
                continue
            dp[mask, j] = min(
                (dp[previous, k][0] + matrix[k, j], k)
                for k in range(1, n) if previous & (1 << k)
            )
    mask = (1 << n) - 2
    last = min(range(1, n), key=lambda j: dp[mask, j][0] + matrix[j, 0])
    reverse = []
    while mask:
        reverse.append(last)
        parent = dp[mask, last][1]
        mask ^= 1 << last
        last = parent
    return [0] + reverse[::-1]


def two_opt_steps(route, matrix, max_passes=12):
    """Yield after each row scan, keeping GUI work chunks small.

    Each row compares edges in NumPy. Accept its best improving reversal.
    Full passes stop at a local optimum or a fixed pass budget.
    """
    route = np.array(route, dtype=int, copy=True)
    n = len(route)
    for _ in range(max_passes):
        changed = False
        for i in range(n - 2):
            js = np.arange(i + 2, n)
            if i == 0:
                js = js[js != n - 1]
            if not len(js):
                continue
            a, b = route[i], route[i + 1]
            c, d = route[js], route[(js + 1) % n]
            gains = matrix[a, c] + matrix[b, d] - matrix[a, b] - matrix[c, d]
            best = int(np.argmin(gains))
            improved = gains[best] < -1e-9
            if improved:
                j = js[best]
                route[i + 1:j + 1] = route[i + 1:j + 1][::-1]
                changed = True
            yield route, improved
        if not changed:
            return


def improve(route, matrix, max_passes=12):
    result = list(route)
    for current, changed in two_opt_steps(route, matrix, max_passes):
        if changed:
            result = current.tolist()
    return result
