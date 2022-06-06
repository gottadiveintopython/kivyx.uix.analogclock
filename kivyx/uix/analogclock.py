__all__ = ('KXAnalogClock', 'create_texture_from_text', )

from functools import partial, lru_cache

from kivy.core.text import Label as CoreLabel
from kivy.core.text.markup import MarkupLabel as CoreMarkupLabel
from kivy.properties import ColorProperty, NumericProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.lang import Builder

import asynckivy as ak


Builder.load_string('''
#:import sin math.sin
#:import cos math.cos
#:import tau math.tau
#:set tau_slash_60 tau / 60.
#:set tau_slash_3600 tau / 3600.
#:set tau_slash_43200 tau / 43200.

<KXAnalogClock>:
    canvas.before:
        PushMatrix:
        Translate:
            xy: self.center
    canvas.after:
        Color:
            rgba: self.seconds_hand_color
        Line:
            width: self.seconds_hand_width
            points: (s := min(self.size) * self.seconds_hand_length, r := self.time * tau_slash_60, ) and (0, 0, sin(r) * s, cos(r) * s)
            cap: 'none'
        Color:
            rgba: self.minutes_hand_color
        Line:
            width: self.minutes_hand_width
            points: (s := min(self.size) * self.minutes_hand_length, r := self.time * tau_slash_3600, ) and (0, 0, sin(r) * s, cos(r) * s)
            cap: 'none'
        Color:
            rgba: self.hours_hand_color
        Line:
            width: self.hours_hand_width
            points: (s := min(self.size) * self.hours_hand_length, r := self.time * tau_slash_43200, ) and (0, 0, sin(r) * s, cos(r) * s)
            cap: 'none'
        PopMatrix:
''')


class KXAnalogClock(Widget):
    time = NumericProperty()
    '''The current time of the clock (in seconds)'''

    seconds_hand_color = ColorProperty("#FFFFFFFF")
    seconds_hand_width = NumericProperty('1dp')
    seconds_hand_length = NumericProperty(0.45)  # fraction of 'min(self.size)'
    minutes_hand_color = ColorProperty("#FFFFFFFF")
    minutes_hand_width = NumericProperty('2dp')
    minutes_hand_length = NumericProperty(0.45)  # fraction of 'min(self.size)'
    hours_hand_color = ColorProperty("#FFFFFFFF")
    hours_hand_width = NumericProperty('4dp')
    hours_hand_length = NumericProperty(0.31)  # fraction of 'min(self.size)'

    labels = ObjectProperty(None, allownone=True)  # Iterable[Dict]
    '''
    The labels drawn on the clock. If you set this, `textures` needs to be None. Read the examples to see what kind
    of `Iterable[Dict]` you need to provide.
    '''

    textures = ObjectProperty(None, allownone=True)  # Iterable[Texture]
    '''The textures drawn on the clock. If you set this, `labels` needs to be None. '''

    def __init__(self, **kwargs):
        from kivy.graphics import InstructionGroup
        self._labels_task = ak.dummy_task
        super().__init__(**kwargs)
        with self.canvas:
            self._labels_ig = InstructionGroup()
        f = self.fbind
        t = Clock.schedule_once(self._reset_labels, -1)
        f('labels', t)
        f('textures', t)

    def _reset_labels(self, dt):
        self._labels_task.cancel()
        self._labels_task = ak.start(self._labels_main())

    async def _labels_main(self):
        from math import sqrt
        from kivy.graphics import Color, Rectangle

        if self.textures is None:
            if self.labels is None:
                return
            else:
                textures = tuple(create_texture_from_text(**kwargs) for kwargs in self.labels)
        else:
            if self.labels is None:
                textures = tuple(self.textures)
            else:
                raise Exception("You cannot set both 'textures' and 'labels'.")

        sizes = tuple(t.size for t in textures)
        offsets = tuple((w/2., h/2.,) for w, h in sizes)
        radius_adjustment = sqrt(max(w**2 + h**2 for w, h in sizes)) / 1.7
        rects = tuple(Rectangle(size=s, texture=t) for t, s in zip(textures, sizes))
        del textures, sizes

        ig = self._labels_ig
        try:
            ig.add(Color(1.0, 1.0, 1.0, 1.0))
            for rect in rects:
                ig.add(rect)
            layout_labels = partial(
                KXAnalogClock._layout_labels,
                self,
                offsets,
                rects,
                radius_adjustment,
                _calc_circular_layout(len(rects))
            )
            bind_uid = self.fbind('size', Clock.schedule_once(layout_labels, -1))
            await ak.sleep_forever()
        finally:
            self.unbind_uid('size', bind_uid)
            ig.clear()

    def _layout_labels(self, offsets, rects, radius_adjustment, base_pos_s, dt):
        radius = min(self.size) / 2. - radius_adjustment
        for rect, (offset_x, offset_y), (base_x, base_y) in zip(rects, offsets, base_pos_s):
            rect.pos = (
                base_x * radius - offset_x,
                base_y * radius - offset_y,
            )


@lru_cache
def _calc_circular_layout(n: int):
    '''単位円の円周上にn個の点を等間隔に置いた時の各点の座標を求める。点は座標(0, 1)から時計回りに置き始める。

    assert _calc_circular_layout(4) == ((0, 1), (1, 0), (0, -1), (-1, 0), )  # approximately
    '''
    from math import cos, sin, tau
    step = tau / n
    return tuple(
        (r := i * step, ) and (sin(r), cos(r), )
        for i in range(n)
    )


def create_texture_from_text(**label_kwargs):
    core = CoreMarkupLabel if label_kwargs.pop('markup', False) else CoreLabel
    label = core(**label_kwargs)
    label.refresh()
    return label.texture
