"""Shared presentation styling for the desktop and slide exports."""
import matplotlib.pyplot as plt
import numpy as np
from .model import length, tour_count, number

BG = '#101b2d'
PANEL = '#192940'
TEXT = '#f1f5fb'
MUTED = '#aabbd0'
CYAN = '#49dfd1'
GOLD = '#ffcf70'


def style():
    plt.rcParams.update({'toolbar': 'None', 'font.family': 'DejaVu Sans', 'font.size': 14,
                         'text.color': TEXT, 'axes.facecolor': BG,
                         'figure.facecolor': BG, 'savefig.facecolor': BG})


def draw_map(ax, points, route=None, partial=False):
    ax.clear()
    ax.set(xlim=(0, 100), ylim=(0, 70), aspect='equal')
    ax.axis('off')
    n = len(points)
    if route is not None and len(route):
        order = list(route)
        if not partial:
            order.append(order[0])
        path = points[order]
        ax.plot(*path.T, color=CYAN, lw=2.6 if n <= 100 else 1.0, alpha=.9, zorder=1)
        start = points[order[0]]
        ax.scatter(*start, s=240 if n <= 20 else 100, facecolors='none',
                   edgecolors=GOLD, linewidths=2.5, zorder=4)
    ax.scatter(*points.T, s=100 if n <= 20 else (30 if n <= 100 else 8),
               color=TEXT, edgecolors=BG, linewidths=.5, zorder=3)
    if n <= 20:
        for i, (x, y) in enumerate(points):
            ax.annotate(str(i + 1), (x, y), xytext=(7, 7),
                        textcoords='offset points', color=GOLD, fontsize=15)


def save_slide(points, matrix, route, path, algorithm, initial=None, elapsed=None):
    style()
    fig = plt.figure(figsize=(16, 9))
    fig.text(.055, .91, 'EN RESA. ALLA STÄDER.', fontsize=28, weight='bold')
    fig.text(.055, .85, f'{number(len(points))} städer  •  Besök varje stad en gång. Återvänd till starten.', color=MUTED, fontsize=18)
    ax = fig.add_axes([.025, .09, .69, .71])
    draw_map(ax, points, route)
    fig.text(.74, .73, 'MÖJLIGA RUTTER', color=MUTED, fontsize=14)
    fig.text(.74, .67, tour_count(len(points)), fontsize=23, color=GOLD)
    fig.text(.74, .55, 'TOTAL STRÄCKA', color=MUTED, fontsize=14)
    fig.text(.74, .49, 'Vad tror ni?' if route is None else f'{number(length(route, matrix), 1)} enheter', fontsize=22)
    fig.text(.74, .37, algorithm, fontsize=16, color=CYAN, wrap=True)
    if route is not None and initial:
        gain = 100 * (1 - length(route, matrix) / initial)
        fig.text(.74, .28, f'{number(gain, 1)} % kortare\nän den första rutten', fontsize=19, linespacing=1.5)
    if elapsed is not None:
        fig.text(.74, .15, f'Beräkning: {number(elapsed, 3)} s', fontsize=14, color=MUTED)
    fig.text(.055, .045, 'Avstånd fågelvägen  •  Gul ring = startstad  •  En rutt räknas bara en gång, oavsett riktning', fontsize=13, color=MUTED)
    fig.savefig(path, dpi=180)
    plt.close(fig)
