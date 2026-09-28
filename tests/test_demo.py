import itertools
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from tsp_demo.algorithms import held_karp, nearest_neighbour, improve, two_opt_steps
from tsp_demo.model import cities, distances, length, tour_count, SIZES
from tsp_demo.app import Demo


class SolverTests(unittest.TestCase):
    def test_exact_matches_exhaustive_small_instances(self):
        for seed in (7, 42, 2026):
            matrix = distances(cities(7, seed))
            best = min(length([0, *p], matrix) for p in itertools.permutations(range(1, 7)))
            self.assertAlmostEqual(length(held_karp(matrix), matrix), best)

    def test_all_sizes_valid_and_improving(self):
        for n in SIZES:
            matrix = distances(cities(n))
            route = nearest_neighbour(matrix)
            result = improve(route, matrix)
            self.assertEqual(sorted(result), list(range(n)))
            self.assertLessEqual(length(result, matrix), length(route, matrix) + 1e-8)
            if n <= 10:
                exact = held_karp(matrix)
                self.assertEqual(sorted(exact), list(range(n)))
                self.assertLessEqual(length(exact, matrix), length(result, matrix) + 1e-8)

    def test_crossing_removed_and_every_step_monotonic(self):
        matrix = distances(np.array([[0, 0], [1, 1], [0, 1], [1, 0]]))
        previous = length([0, 1, 2, 3], matrix)
        for route, _ in two_opt_steps([0, 1, 2, 3], matrix):
            current = length(route, matrix)
            self.assertLessEqual(current, previous + 1e-9)
            previous = current
        self.assertAlmostEqual(previous, 4)

    def test_counts_and_reproducibility(self):
        self.assertEqual(tour_count(5), '12')
        self.assertEqual(tour_count(10), '181 440')
        self.assertIn('2564', tour_count(1000))
        np.testing.assert_equal(cities(10, 42), cities(10, 42))


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = Demo(output=self.temp.name)

    def tearDown(self):
        self.app.stop()
        plt.close('all')
        self.temp.cleanup()

    def test_controls_all_sizes(self):
        for n in SIZES:
            self.app.generate(n)
            self.app.solve()
            initial = length(self.app.route, self.app.matrix)
            self.app.start_improve()
            # Avoid full raster draws on each timer tick in this logic test.
            real_refresh = self.app.refresh
            self.app.refresh = lambda: None
            ticks = 0
            while self.app.steps is not None:
                self.app.tick()
                ticks += 1
                self.assertLess(ticks, 10000)
            self.app.refresh = real_refresh
            self.assertLessEqual(length(self.app.route, self.app.matrix), initial + 1e-8)
            self.app.reset()
            self.assertIsNone(self.app.route)
            self.app.run_demo()
            self.assertIsNotNone(self.app.steps)
            self.app.generate(n, fresh=True)
            self.assertIsNone(self.app.steps)

    def test_audience_compare_and_export(self):
        for n in (5, 10):
            self.app.generate(n)
            self.app.audience_mode()
            self.app.fig.canvas.draw()
            for point in self.app.points:
                pixel = self.app.ax.transData.transform(point)
                self.app.click(SimpleNamespace(inaxes=self.app.ax, xdata=point[0], x=pixel[0], y=pixel[1]))
            self.assertFalse(self.app.manual)
            audience = self.app.audience_length
            self.app.solve()
            self.assertEqual(self.app.audience_length, audience)
            self.assertLessEqual(length(self.app.route, self.app.matrix), audience + 1e-8)
        self.app.export()
        self.assertEqual(len(list(Path(self.temp.name).glob('*.png'))), 1)


if __name__ == '__main__':
    unittest.main()
