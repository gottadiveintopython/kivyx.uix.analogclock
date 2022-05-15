from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock

from kivyx.uix.analogclock import KXAnalogClock

KV_CODE = r'''
KXAnalogClock:
    labels:
        (
        {'text': text, 'font_size': 30, }
        for text in "12 1 2 3 4 5 6 7 8 9 10 11".split()
        )
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Line:
            width: 2.
            circle: 0, 0, min(self.size) * 0.49
'''

class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        import datetime
        t = datetime.datetime.now().time()
        self.root.time = (t.hour * 60 + t.minute) * 60 + t.second
        Clock.schedule_interval(self._progress_clock, 0)

    def _progress_clock(self, dt):
        self.root.time += dt

if __name__ == '__main__':
    SampleApp().run()
