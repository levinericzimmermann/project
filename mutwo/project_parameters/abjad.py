from mutwo import abjad_parameters
from mutwo import project_parameters

import abjad


class BreathIndicator(abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf):
        breath_or_hold_breath = self.indicator.breath
        match breath_or_hold_breath:
            case project_parameters.HoldBreath():
                a = abjad.Fermata()
            case project_parameters.Breath():
                a = abjad.Markup(rf"\markup {{ {breath_or_hold_breath.symbol} }}")
            case _:
                raise NotImplementedError(breath_or_hold_breath)
        abjad.attach(a, leaf, direction=abjad.DOWN)
        return leaf
