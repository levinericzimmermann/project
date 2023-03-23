import functools
import operator

from mutwo import music_parameters
from mutwo import project_parameters

j = music_parameters.JustIntonationPitch
mp = project_parameters.MoonPhase
sl = project_parameters.SunLight
ml = project_parameters.MoonLight


def _moon_phase_intonation_tuple():
    j = music_parameters.JustIntonationPitch

    # The core never changes, this is the stable
    # center.
    def c():  # core
        return (j("1/1"), j("3/2"), j("4/3"))

    def py0():
        return (j("9/8"), j("16/9"))

    def py1():
        return (j("27/16"), j("32/27"))

    def ju0():
        return (j("10/9"), j("9/5"))

    def ju1():
        return (j("8/5"), j("5/4"))

    def se0():
        return (j("7/4"), j("8/7"))

    def se1():
        return (j("7/6"), j("12/7"))

    d = (
        ("r", (c(), se0(), se1())),
        ("r", (c(), py0(), se1())),
        ("r", (c(), py0(), py1())),
        ("r", (c(), py0(), ju1())),
        ("f", (c(), ju0(), ju1())),
        ("f", (c(), py0(), ju1())),
        ("f", (c(), py0(), py1())),
        ("f", (c(), py0(), se1())),
    )

    def m(direction, t):
        i_tuple = tuple(sorted(functools.reduce(operator.add, t)))
        if direction == "f":
            # XXX: Inversion doesn't make any difference here, because the
            #      scales are symmetrical. We must use a different technique
            #      to emphasise the difference between a waxing and a waning
            #      moon.
            #
            #      Maybe move everything by 3/2? But then we break with the
            #      symmetrical sun light scales, and this is arbitrary...
            i_tuple = tuple(
                sorted((i.inverse(mutate=False).normalize() for i in i_tuple))
            )
        return i_tuple

    return tuple(m(direction, t) for direction, t in d)


MOON_PHASE_TO_INTONATION = {
    p: t
    for p, t in zip(
        (
            mp.NEW,
            mp.WAXING_CRESCENT,
            mp.QUARTER_0,
            mp.WAXING_GIBBOUS,
            mp.FULL,
            mp.WANING_GIBBOUS,
            mp.QUARTER_1,
            mp.WANING_CRESCENT,
        ),
        _moon_phase_intonation_tuple(),
    )
}

REFERENCE_PITCH_TUPLE = tuple(
    j(r) for r in "1/1 9/8 32/27 4/3 3/2 27/16 16/9".split(" ")
)

SUN_LIGHT_TO_PITCH_INDEX_TUPLE = {
    # 4, 1
    sl.MORNING_TWILIGHT: (0, 1, 2, 4, 5),
    # 3, 2
    sl.DAYLIGHT: (1, 2, 4, 5, 6),
    # 2, 3
    sl.EVENING_TWILIGHT: (1, 2, 3, 5, 6),
    # 1, 4
    sl.NIGHTLIGHT: (0, 2, 3, 5, 6),
}

SUN_LIGHT_TO_PITCH_TUPLE = {
    # 4, 1
    sl.MORNING_TWILIGHT: (j("1/1"), j("9/8"), j("32/27"), j("3/2"), j("27/16")),
    # 3, 2
    sl.DAYLIGHT: (j("3/4"), j("27/32"), j("8/9"), j("9/8"), j("32/27")),
    # 2, 3
    sl.EVENING_TWILIGHT: (j("9/8"), j("32/27"), j("4/3"), j("27/16"), j("16/9")),
    # 1, 4
    sl.NIGHTLIGHT: (j("27/32"), j("8/9"), j("1/1"), j("32/27"), j("4/3")),
}


# Only 2 pitches are constantly present in all 4 pentatonics
# of the sun. Therefore we use only those two pitches here.

MOON_LIGHT_TO_PITCH_INDEX_TUPLE = {
    ml.ABSENT: (2,),
    ml.PRESENT: (5,),
}

MOON_LIGHT_TO_PITCH_TUPLE = {
    ml.ABSENT: (j("32/27"),),
    ml.PRESENT: (j("27/32"),),
}


del j, mp
