import unittest
from types import SimpleNamespace
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tsp_demo.presentation import Presentation
from tsp_demo.model import length


class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.app = Presentation()

    def tearDown(self):
        self.app.stop()
        plt.close('all')

    def choose_cities(self):
        self.app.fig.canvas.draw()
        for point in self.app.points:
            pixel = self.app.ax.transData.transform(point)
            self.app.click(SimpleNamespace(inaxes=self.app.ax, xdata=point[0], x=pixel[0], y=pixel[1]))

    def finish_animation(self):
        refresh = self.app.refresh
        self.app.refresh = lambda: None
        try:
            for _ in range(10000):
                if self.app.steps is None:
                    break
                self.app.tick()
            self.assertIsNone(self.app.steps)
        finally:
            self.app.refresh = refresh
        self.app.refresh()

    def test_whole_presentation_and_final_slide(self):
        self.assertEqual(self.app.buttons, [])
        self.assertEqual(len(self.app.fig.axes), 1)
        self.app.advance()
        self.assertEqual(self.app.phase, 'audience')
        self.assertEqual(self.app.history, [])
        for n in (5, 10):
            self.assertEqual(self.app.n, n)
            self.choose_cities()
            audience = self.app.audience_length
            self.app.advance()
            self.assertEqual(self.app.phase, 'result')
            self.assertEqual(self.app.initial, audience)
            self.assertLessEqual(length(self.app.route, self.app.matrix), audience + 1e-8)
            self.app.advance()
        for n in (20, 100, 1000):
            self.assertEqual(self.app.n, n)
            self.assertEqual(self.app.phase, 'ready')
            self.assertFalse(self.app.manual)
            self.app.advance()
            self.assertEqual(self.app.phase, 'initial')
            self.assertIsNone(self.app.steps)
            first_route = self.app.route.copy()
            self.app.tick()
            self.assertEqual(self.app.route, first_route)
            self.assertEqual(self.app.phase, 'initial')
            self.app.advance()
            self.assertEqual(self.app.phase, 'running')
            self.app.advance()
            self.assertEqual(self.app.n, n)
            self.finish_animation()
            self.assertEqual(self.app.phase, 'result')
            self.assertLessEqual(length(self.app.route, self.app.matrix), self.app.initial + 1e-8)
            self.app.advance()
        self.assertEqual(self.app.n, 1000)
        self.assertEqual(self.app.phase, 'result')

    def test_back_preserves_audience_and_undo_reopens_route(self):
        self.choose_cities()
        original = self.app.route.copy()
        self.app.on_key(SimpleNamespace(key='right'))
        self.app.on_key(SimpleNamespace(key='left'))
        self.assertEqual(self.app.route, original)
        self.assertEqual(self.app.phase, 'audience')
        self.app.on_key(SimpleNamespace(key='backspace'))
        self.assertTrue(self.app.manual)
        self.assertEqual(self.app.selected, original[:-1])
        self.assertIsNone(self.app.route)
        self.app.on_key(SimpleNamespace(key='home'))
        self.assertEqual(self.app.selected, [])
        self.assertEqual(self.app.history, [])
        self.assertEqual(self.app.n, 5)

    def test_back_cancels_running_animation(self):
        self.app.begin_size(1000)
        self.app.advance()
        first_route = self.app.route.copy()
        baseline = self.app.initial
        self.app.advance()
        self.app.tick()
        self.app.previous()
        self.assertIsNone(self.app.steps)
        self.assertEqual(self.app.route, first_route)
        self.assertEqual(self.app.initial, baseline)
        self.assertEqual(self.app.phase, 'initial')
        self.app.previous()
        self.assertIsNone(self.app.route)
        self.assertEqual(self.app.phase, 'ready')


if __name__ == '__main__':
    unittest.main()
