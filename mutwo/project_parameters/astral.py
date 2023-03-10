import collections
import enum

import ranges


__all__ = ("MoonPhase", "SunLight", "MoonLight")


class MoonPhase(
    collections.namedtuple("MoonPhase", ("value", "name", "range", "symbol")), enum.Enum
):
    # The specific ranges are not exactly clear, they don't have to be like
    # this. We could also say that new moon only lasts one day, and then we are
    # in the transition phase "waxing crescent". This is a bit relative.
    NEW = (0, "new moon", ranges.Range(0, 3.5), "🌑")
    WAXING_CRESCENT = (1, "waxing crescent", ranges.Range(3.5, 7), "🌒")
    QUARTER_0 = (2, "first quarter", ranges.Range(7, 10.5), "🌓")
    WAXING_GIBBOUS = (3, "waxing gibbous", ranges.Range(10.5, 14), "🌔")
    FULL = (4, "full moon", ranges.Range(14, 17.5), "🌕")
    WANING_GIBBOUS = (5, "waning gibbous", ranges.Range(17.5, 21), "🌖")
    QUARTER_1 = (6, "second quarter", ranges.Range(21, 24.5), "🌗")
    WANING_CRESCENT = (7, "waning crescent", ranges.Range(24.5, 28), "🌘")


class SunLight(collections.namedtuple("SunLight", ("value", "name")), enum.Enum):
    MORNING_TWILIGHT = (0, "morning twilight")
    DAYLIGHT = (1, "daylight")
    EVENING_TWILIGHT = (2, "evening twilight")
    NIGHTLIGHT = (3, "nightlight")


class MoonLight(collections.namedtuple("MoonLight", ("value", "name")), enum.Enum):
    ABSENT = (0, "the moon is absent")
    PRESENT = (1, "the moon is present")
