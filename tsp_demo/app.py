"""Timer-driven desktop UI: bounded computation leaves the event loop responsive."""
from pathlib import Path
from time import perf_counter
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
from .algorithms import held_karp, nearest_neighbour, two_opt_steps
from .model import SIZES, cities, distances, length, tour_count, number
from .plotting import BG, PANEL, TEXT, MUTED, CYAN, GOLD, style, draw_map, save_slide


class Demo:
    def __init__(self, seed=42, n=5, output='output', controls=True):
        style()
        self.seed, self.n, self.output = seed, n, Path(output)
        self.fig = plt.figure(figsize=(16, 9))
        self.fig.canvas.manager.set_window_title('Alla städer • Hitta den kortaste rutten')
        self.fig.text(.04, .94, 'EN RESA. ALLA STÄDER.', fontsize=27, weight='bold')
        self.subtitle = self.fig.text(.04, .892, '', fontsize=15, color=MUTED)
        self.ax = self.fig.add_axes([.015, .205, .70, .66])
        self.info = self.fig.text(.735, .81, '', va='top', fontsize=18, linespacing=1.6)
        self.status = self.fig.text(.04, .185, '', fontsize=14, color=GOLD)
        self.footer = self.fig.text(.04, .025, 'Prova alla möjligheter? Eller välja smartare?     •     Gul ring = start     •     F = helskärm', fontsize=12, color=MUTED)
        self.buttons = []
        if controls:
            for i, count in enumerate(SIZES):
                self.button([.04 + i * .135, .105, .122, .05], f'{number(count)} städer', lambda e, c=count: self.generate(c))
            self.button([.735, .105, .22, .05], 'Slumpa nya städer', lambda e: self.generate(self.n, True))
            actions = [('Lös', self.solve), ('Förbättra', self.start_improve), ('Nollställ rutt', self.reset),
                       ('Kör demo', self.run_demo), ('Publiken', self.audience_mode), ('Spara PNG', self.export)]
            for i, (label, action) in enumerate(actions):
                self.button([.04 + i * .155, .047, .145, .045], label, lambda e, fn=action: fn())
        self.timer = self.fig.canvas.new_timer(interval=60)
        self.timer.add_callback(self.tick)
        self.fig.canvas.mpl_connect('button_press_event', self.click)
        self.fig.canvas.mpl_connect('close_event', lambda e: self.stop())
        self.generate(n)

    def button(self, rect, label, callback):
        button = Button(self.fig.add_axes(rect), label, color=PANEL, hovercolor='#31506e')
        button.label.set_color(TEXT)
        button.label.set_fontsize(13)
        button.on_clicked(callback)
        self.buttons.append(button)

    def stop(self):
        self.timer.stop()
        self.steps = None

    def generate(self, n, fresh=False):
        self.stop()
        self.n = n
        if fresh:
            self.seed += 1
        self.points = cities(n, self.seed)
        self.matrix = distances(self.points)
        self.reset()

    def reset(self):
        self.stop()
        self.route, self.initial, self.audience_length = None, None, None
        self.manual, self.selected = False, []
        self.elapsed = 0.0
        self.algorithm = 'Vad tror ni?'
        self.status.set_text('Vilken väg skulle ni välja?')
        self.refresh()

    def refresh(self):
        shown = self.selected if self.manual else self.route
        draw_map(self.ax, self.points, shown, partial=self.manual)
        self.subtitle.set_text(f'{number(self.n)} städer   •   Besök varje stad en gång. Återvänd till starten.')
        distance = '—' if self.route is None else f'{number(length(self.route, self.matrix), 1)} meter'
        details = f'MÖJLIGA RUTTER\n{tour_count(self.n)}\n\nTOTAL STRÄCKA\n{distance}\n\n{self.algorithm}\nBeräkning: {number(self.elapsed, 3)} s'
        if self.initial and self.route is not None:
            gain = 100 * (1 - length(self.route, self.matrix) / self.initial)
            details += f'\n\nFrån början: {number(self.initial, 1)} m\n{number(gain, 1)} % kortare'
        if self.audience_length is not None:
            details += f'\n\nPubliken: {number(self.audience_length, 1)}'
        self.info.set_text(details)
        self.fig.canvas.draw_idle()

    def solve(self):
        self.stop()
        self.manual = False
        start = perf_counter()
        self.route = held_karp(self.matrix) if self.n <= 10 else nearest_neighbour(self.matrix)
        self.elapsed = perf_counter() - start
        self.initial = length(self.route, self.matrix)
        self.algorithm = 'Kortaste rutten' if self.n <= 10 else 'Första förslaget'
        self.status.set_text('Så här kort kan resan bli!' if self.n <= 10 else 'Här är ett första förslag. Kan resan bli kortare?')
        self.refresh()

    def start_improve(self):
        if self.steps is not None:
            return
        if self.route is None:
            self.solve()
        self.manual = False
        self.steps = two_opt_steps(self.route, self.matrix)
        self.search_seconds = 0.0
        self.algorithm = 'Förbättrar rutten…'
        self.status.set_text('Vi ser om det finns en kortare väg.')
        # Hold the initial route briefly so the audience can see the baseline.
        self.timer.interval = 800
        self.timer.start()
        self.refresh()

    def tick(self):
        if self.steps is None:
            return
        self.timer.interval = 180 if self.n <= 100 else 60
        start = perf_counter()
        finished = False
        # At most 12 ms of search per frame; pause after a few visible changes.
        changes = 0
        while perf_counter() - start < .012 and changes < (1 if self.n <= 100 else 3):
            try:
                route, changed = next(self.steps)
            except StopIteration:
                finished = True
                break
            if changed:
                self.route = route.tolist()
                changes += 1
        spent = perf_counter() - start
        self.elapsed += spent
        self.search_seconds += spent
        if finished or self.search_seconds >= 3.0:
            self.stop()
            self.algorithm = 'Färdig rutt'
            self.status.set_text('Klart! Jämför sträckan före och efter.')
        self.refresh()

    def run_demo(self):
        self.stop()
        self.manual = False
        start = perf_counter()
        self.route = nearest_neighbour(self.matrix)
        self.elapsed = perf_counter() - start
        self.initial = length(self.route, self.matrix)
        self.start_improve()

    def audience_mode(self):
        if self.n > 10:
            self.status.set_text('Välj 5 eller 10 städer för att prova själva.')
            self.fig.canvas.draw_idle()
            return
        self.reset()
        self.manual = True
        self.algorithm = 'Publiken • väljer'
        self.status.set_text('Ni bestämmer! Klicka på städerna i den ordning ni vill besöka dem.')
        self.refresh()

    def click(self, event):
        if not self.manual or event.inaxes != self.ax or event.xdata is None:
            return
        pixels = self.ax.transData.transform(self.points)
        distances_px = np.linalg.norm(pixels - [event.x, event.y], axis=1)
        city = int(np.argmin(distances_px))
        if distances_px[city] > 22 or city in self.selected:
            return
        self.selected.append(city)
        if len(self.selected) == self.n:
            self.route = self.selected.copy()
            self.manual = False
            self.initial = self.audience_length = length(self.route, self.matrix)
            self.algorithm = 'Publikens rutt'
            self.status.set_text('Där är er rutt! Tryck på Lös för att jämföra.')
        else:
            self.status.set_text(f'{len(self.selected)} av {self.n} städer valda. Vart åker vi nu?')
        self.refresh()

    def export(self):
        if self.manual:
            self.status.set_text('Välj alla städer innan ni sparar bilden.')
            self.fig.canvas.draw_idle()
            return
        try:
            self.output.mkdir(parents=True, exist_ok=True)
            stage = 'städer' if self.route is None else self.algorithm.split(' •')[0].lower().replace(' ', '_')
            path = self.output / f'tsp_{self.n:04d}_{stage}_{datetime.now():%Y%m%d_%H%M%S_%f}.png'
            save_slide(self.points, self.matrix, self.route, path, self.algorithm, self.initial, self.elapsed)
            self.status.set_text(f'Bilden är sparad i {self.output}')
        except OSError as error:
            self.status.set_text(f'Kunde inte spara bilden: {error}')
        self.fig.canvas.draw_idle()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Alla städer: handelsresandeproblemet i klassrummet', add_help=False)
    parser._positionals.title = 'Argument'
    parser._optionals.title = 'Alternativ'
    parser.add_argument('-h', '--help', action='help', help='Visa hjälp och avsluta')
    parser.add_argument('--seed', type=int, default=42, help='Slumpfrö för reproducerbara exempel (standard: 42)')
    parser.add_argument('--cities', type=int, choices=SIZES, default=5, help='Antal städer i fritt läge (standard: 5)')
    parser.add_argument('--output', default='output', help='Mapp för sparade bilder (standard: output)')
    parser.add_argument('--mode', choices=('interactive', 'presentation'), default='interactive', help='Fritt läge med knappar eller stegvis presentation (standard: interactive)')
    parser.add_argument('--fullscreen', action='store_true', help='Starta i helskärm')
    args = parser.parse_args()
    if args.mode == 'presentation':
        from .presentation import Presentation
        demo = Presentation(args.seed, args.output)
    else:
        demo = Demo(args.seed, args.cities, args.output)
    if args.fullscreen:
        demo.fig.canvas.manager.full_screen_toggle()
    plt.show()
    return demo
