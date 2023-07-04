import itertools

from mutwo import music_parameters

from . import week

# a' frequency
A_FREQUENCY = 442

# we tune to 'a'
music_parameters.configurations.DEFAULT_CONCERT_PITCH = A_FREQUENCY

CONCERT_PITCH_WESTERN_PITCH = music_parameters.WesternPitch("a", 4)
CONCERT_PITCH_JUST_INTONATION_PITCH = music_parameters.JustIntonationPitch("1/1")

music_parameters.configurations.EQUAL_DIVIDED_OCTAVE_PITCH_ROUND_FREQUENCY_DIGIT_COUNT = (
    7
)

# Our tonal system replicates the structure of a week.
#
# We have 7 days and those 7 days are associated with the classic planets.
# (see https://en.wikipedia.org/wiki/Week)
# (see https://en.wikipedia.org/wiki/Classical_planet)
#
# The classic planets are ordered from fast to slow moving.
# But the order of the planets in a week is more complex:
# it uses this basic order, but then always moves +3 to the
# next planet instead of +1.
#
# So the result is a heptagram.
#
# We can also do a heptagram with pitches.
#
# We assume a 3-cycle (Pythagorean tuning) as:
#
#
#                    a
#             d             e
#      g                            b
#             c             fs
#
#
# (so a == 1/1)
#
#
# So the "normal/natural" +1 order of our tones is
#
#           c   g   d   a   e   b   fs
#
# And then the week-like +3 order is
#
#           c   a   fs  d   b   g   e
#
# So instead of moving 3/2, we now move a minor third
# down or a major sixth up.
#
# But when moving thirds, Pythagorean thirds are strange.
# It's much easier to move Just thirds/sixth (e.g. 5/3)
#
# So we actually have something like
#
#   1/1     5/3     25/18       ...
#   c       a       fs          ...
#
# & some more iterations & we have something very complex
# & we are very off from our Pythagorean reference system.
#
# So we need to better find a cycle which doesn't move some
# many commas all the time. What's for instance about this:
#
#   1/1     5/3     4/3     10/9    16/9    40/27   32/27
#   c       a       f       d       bf      g       ef
#
# Okay, we don't have a 'fs' and our 'b' becomes a 'bf' and
# our 'e' is an 'ef'. But I think those alterations are
# acceptable..
#
# We need to set 'a' to 1/1, then we get:
#
#   6/5     1/1     8/5     4/3     ...
#   c       a       f       d       ...
#
# But this gives us some complicated intervals in the end.
# So maybe it's just better to simply start with 'a', although
# it's "not really" our first pitch.
#
# => Yes, but the complicated intervals in the end & at the
# start don't matter, because for MONDAY & SUNDAY we only
# plan silence anyway.
#
# => So in the end, we can actually go for a == 1/1 :)

j = music_parameters.JustIntonationPitch


def _():
    # This is our 'c': we start with the 'c' & move then to
    # 'a' by adding 8/5 to our 'c'.
    last_pitch = j("6/5")
    # We only move by a Pythagorean comma each second step,
    # because the 5ths are removing each other again :)
    interval_cycle = itertools.cycle((j("5/3"), j("8/5")))
    week_day_to_tonic = {}
    for day in week.WeekDay:
        week_day_to_tonic.update({day: last_pitch})
        last_pitch = (last_pitch + next(interval_cycle)).normalize()
    return week_day_to_tonic


WEEK_DAY_TO_TONIC = _()


# During one day, we now may have multiple movements of tonic
# pitches. The idea is to show the 'natural' neighbours of the
# current planet, which are not the real 'day' / 'week-based'
# neighbours.
#
# So we move to the Pythagorean neighbours 3/2 & 4/3.
# In order to improve the movement in the other pitch dimension -
# interval distance in cents - we add some interpolation pitches,
# so that we always move thirds up & down.
#
# But since we always have either a negative 5 comma or no
# 5 comma at all & we want to avoid two 5 commas (after all this
# piece is supposed to be rather easily tunable), we need to
# adjust our interpolation intervals according to the given
# 5 comma size. This is why we use a mapping of comma->tonic-movements.

COMMA5SIZE_TO_TONIC_MOVEMENT_TUPLE = {
    -1: (
        j("2/1"),
        j("5/3"),
        j("4/3"),
        j("10/9"),
        j("1/1"),
        j("5/4"),
        j("3/2"),
        j("15/8"),
        j("2/1"),
    ),
    0: (
        j("2/1"),
        j("5/3"),
        j("4/3"),
        j("5/4"),
        j("1/1"),
        j("6/5"),
        j("3/2"),
        j("8/5"),
        j("2/1"),
    ),
}


def _():
    direction_cycle = itertools.cycle((0, 1, 1, 0))
    week_day_to_tonic_movement_tuple = {}
    for week_day, pitch in WEEK_DAY_TO_TONIC.items():
        try:
            comma5size = pitch.exponent_tuple[2]
        except IndexError:
            comma5size = 0
        direction = next(direction_cycle)
        tonic_movement_tuple = COMMA5SIZE_TO_TONIC_MOVEMENT_TUPLE[comma5size]
        if not direction:
            tonic_movement_tuple = tuple(reversed(tonic_movement_tuple))
        week_day_to_tonic_movement_tuple.update(
            {week_day: tuple(pitch + i for i in tonic_movement_tuple)}
        )
    return week_day_to_tonic_movement_tuple


WEEK_DAY_TO_TONIC_MOVEMENT_TUPLE = _()
