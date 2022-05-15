from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock

from kivyx.uix.analogclock import KXAnalogClock

KV_CODE = r'''
KXAnalogClock:
    hours_hand_color: rgba("#FFFFFF44")
    minutes_hand_color: rgba("#FFFFFF44")
    seconds_hand_color: rgba("#FFFFFF44")
    labels:
        (
        {'text': '12', 'font_size': 60, 'outline_color': rgba("#FF00FF"), 'outline_width': 2, 'color': rgba("#000000"), },
        {'text': '.', 'font_size': 70, },
        {'text': '.', 'font_size': 70, },
        {'text': '3', 'font_size': 60, 'outline_color': rgba("#00FF00"), 'outline_width': 2, 'color': rgba("#000000"), },
        {'text': '.', 'font_size': 70, },
        {'text': '.', 'font_size': 70, },
        {'text': '6', 'font_size': 60, 'outline_color': rgba("#FF4400"), 'outline_width': 2, 'color': rgba("#000000"), },
        {'text': '.', 'font_size': 70, },
        {'text': '.', 'font_size': 70, },
        {'text': '9', 'font_size': 60, 'outline_color': rgba("#777777"), 'outline_width': 2, 'color': rgba("#000000"), },
        {'text': '.', 'font_size': 70, },
        {'text': '.', 'font_size': 70, },
        )
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
