"""Ett stegvis presentationsläge med samma karta och sökning som det fria läget."""
from .app import Demo
from .model import SIZES, length, number, tour_count


class Presentation(Demo):
    def __init__(self, seed=42, output='output'):
        self.history = []
        self.phase = 'audience'
        super().__init__(seed=seed, n=5, output=output, controls=False)
        self.ax.set_position([.015, .14, .70, .71])
        self.status.set_position((.04, .105))
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.begin_size(5)

    def begin_size(self, n):
        self.phase = 'audience' if n <= 10 else 'ready'
        self.generate(n)
        if n <= 10:
            self.audience_mode()
        else:
            self.algorithm = 'Datorns tur'
            self.status.set_text('Hur kort kan resan bli?')
        self.refresh()

    def refresh(self):
        super().refresh()
        distance = '—' if self.route is None else f'{number(length(self.route, self.matrix), 1)} meter'
        details = f'MÖJLIGA RUTTER\n{tour_count(self.n)}\n\nTOTAL STRÄCKA\n{distance}\n\n{self.algorithm}'
        if self.route is not None and self.initial and self.phase in ('running', 'result'):
            baseline = 'Er rutt' if self.audience_length is not None else 'Första förslaget'
            gain = max(0.0, 100 * (1 - length(self.route, self.matrix) / self.initial))
            details += f'\n\n{baseline}: {number(self.initial, 1)} m\n{number(gain, 1)} % kortare'
        self.info.set_text(details)
        self.footer.set_text(f'{SIZES.index(self.n) + 1} / {len(SIZES)}')
        self.fig.canvas.draw_idle()

    def snapshot(self):
        # Spara även publikens ordning så att ett steg bakåt inte tappar deras rutt.
        return {
            'n': self.n, 'phase': self.phase,
            'route': None if self.route is None else self.route.copy(),
            'selected': self.selected.copy(), 'manual': self.manual,
            'initial': self.initial, 'audience_length': self.audience_length,
            'elapsed': self.elapsed, 'algorithm': self.algorithm,
            'status': self.status.get_text(),
        }

    def advance(self):
        if self.phase == 'running':
            return  # En extra knapptryckning ska inte hoppa över jämförelsen.
        if self.phase == 'audience' and self.manual:
            self.status.set_text('Välj resten av städerna först. Vilken blir nästa?')
            self.fig.canvas.draw_idle()
            return
        if self.phase == 'result' and self.n == SIZES[-1]:
            self.status.set_text('Alla städer besökta. En resa med färre omvägar!')
            self.fig.canvas.draw_idle()
            return
        self.history.append(self.snapshot())
        if self.phase == 'audience':
            audience = self.audience_length
            self.phase = 'result'
            self.solve()
            self.initial = audience
            self.status.set_text('Så här kort kan resan bli! Jämför med er rutt.')
        elif self.phase == 'ready':
            self.phase = 'initial'
            self.solve()
        elif self.phase == 'initial':
            self.phase = 'running'
            self.start_improve()
        else:
            self.begin_size(SIZES[SIZES.index(self.n) + 1])
        self.refresh()

    def previous(self):
        if not self.history:
            return
        saved = self.history.pop()
        self.stop()
        self.generate(saved['n'])
        for key, value in saved.items():
            if key != 'status':
                setattr(self, key, value)
        self.status.set_text(saved['status'])
        self.refresh()

    def undo_city(self):
        if self.phase != 'audience' or not self.selected:
            return
        self.selected.pop()
        self.manual = True
        self.route = self.initial = self.audience_length = None
        self.algorithm = 'Publiken • väljer'
        self.status.set_text('Vart åker vi nu?')
        self.refresh()

    def click(self, event):
        super().click(event)
        if self.phase == 'audience' and not self.manual:
            self.status.set_text('Där är er rutt!')
            self.fig.canvas.draw_idle()

    def tick(self):
        super().tick()
        if self.phase == 'running' and self.steps is None:
            self.phase = 'result'
            self.status.set_text('Klart! Jämför sträckan före och efter.')
            self.refresh()

    def on_key(self, event):
        if event.key in (' ', 'right', 'pagedown', 'enter'):
            self.advance()
        elif event.key in ('left', 'pageup'):
            self.previous()
        elif event.key == 'backspace':
            self.undo_city()
        elif event.key == 'home':
            self.history.clear()
            self.begin_size(5)
