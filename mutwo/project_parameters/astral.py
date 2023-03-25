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
    NEW = (0, "new moon", ranges.Range(0, 3.75), "🌑")
    WAXING_CRESCENT = (1, "waxing crescent", ranges.Range(3.75, 7.5), "🌒")
    QUARTER_0 = (2, "first quarter", ranges.Range(7.5, 11.25), "🌓")
    WAXING_GIBBOUS = (3, "waxing gibbous", ranges.Range(11.25, 15), "🌔")
    FULL = (4, "full moon", ranges.Range(15, 18.75), "🌕")
    WANING_GIBBOUS = (5, "waning gibbous", ranges.Range(18.75, 22.5), "🌖")
    QUARTER_1 = (6, "second quarter", ranges.Range(22.5, 26.25), "🌗")
    WANING_CRESCENT = (7, "waning crescent", ranges.Range(26.25, 30), "🌘")


class SunLight(collections.namedtuple("SunLight", ("value", "name")), enum.Enum):
    MORNING_TWILIGHT = (0, "morning twilight")
    DAYLIGHT = (1, "daylight")
    EVENING_TWILIGHT = (2, "evening twilight")
    NIGHTLIGHT = (3, "nightlight")


class MoonLight(collections.namedtuple("MoonLight", ("value", "name")), enum.Enum):
    ABSENT = (0, "the moon is absent")
    PRESENT = (1, "the moon is present")
