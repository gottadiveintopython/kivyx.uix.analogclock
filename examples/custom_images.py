from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock

from kivyx.uix.analogclock import KXAnalogClock

KV_CODE = r'''
KXAnalogClock:
    hours_hand_color: rgba("#22222255")
    minutes_hand_color: rgba("#22222255")
    seconds_hand_color: rgba("#22222255")
    canvas.before:
        Color:
            rgba: rgba("#DDDDDD")
        Ellipse:
            pos: (-min(self.size) / 2.1, ) * 2
            size: (min(self.size) / 2.1 * 2., ) * 2
'''

class SampleApp(App):
    def build(self):
        from pathlib import PurePath
        from kivy.atlas import Atlas
        atlas_file = str(PurePath(__file__).parent.joinpath("bird.atlas"))
        clock = Builder.load_string(KV_CODE)
        clock.textures = Atlas(atlas_file).textures.values()
        return clock

    def on_start(self):
        import datetime
        t = datetime.datetime.now().time()
        self.root.time = (t.hour * 60 + t.minute) * 60 + t.second
        Clock.schedule_interval(self._progress_clock, 0)

    def _progress_clock(self, dt):
        self.root.time += dt

if __name__ == '__main__':
    SampleApp().run()
