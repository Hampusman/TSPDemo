"""Skapa reproducerbara presentationsbilder utan att öppna ett fönster."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
from tsp_demo.algorithms import held_karp, nearest_neighbour, improve
from tsp_demo.model import SIZES, cities, distances, length
from tsp_demo.plotting import save_slide


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser._positionals.title = 'Argument'
    parser._optionals.title = 'Alternativ'
    parser.add_argument('-h', '--help', action='help', help='Visa hjälp och avsluta')
    parser.add_argument('--seed', type=int, default=42, help='Slumpfrö för reproducerbara exempel (standard: 42)')
    parser.add_argument('--output', type=Path, default=Path('output'), help='Mapp för bilder (standard: output)')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for n in SIZES:
        points = cities(n, args.seed)
        matrix = distances(points)
        prefix = f'tsp_{n:04d}_seed{args.seed}'
        initial = nearest_neighbour(matrix)
        baseline = length(initial, matrix)
        stages = [('cities', None, 'Vilken rutt väljer ni?'),
                  ('initial', initial, 'Närmaste granne'),
                  ('optimized', improve(initial, matrix), '2-opt-heuristik')]
        if n <= 10:
            stages.append(('exact', held_karp(matrix), 'Exakt optimum • Held–Karp'))
        for stage, route, name in stages:
            path = args.output / f'{prefix}_{stage}.png'
            save_slide(points, matrix, route, path, name, baseline if route is not None else None)
            print(path)


if __name__ == '__main__':
    main()
