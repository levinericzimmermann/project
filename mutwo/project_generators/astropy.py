import datetime

import astral
from astropy import coordinates
from astropy import time as astropy_time
import astropy.units as u
import ranges

__all__ = ("LunarPhaseCalculator",)


class LunarPhaseCalculator(object):
    """Human-focused lunar phase calculator :)

    This is a rounded version of the original lunar phase index.
    The idea is to adjust the index that every day has exactly one specific
    integer index of the current lunar phase (this matches how in Hawaii each
    day has a specific lunar phase based term). This is actually wrong, because
    the lunar phase takes ~29.5 days, so it doesn't really work with each day.
    But we humans round it for better understandability :)

    This algorithm works by simply calculating a reference lunar phase index
    and from this reference it's simply incrementing. The longer it increments the
    wronger it gets. So you can call '.reset()' and it should be ok again.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.location_info_to_reference = {}

    def __call__(
        self, current_time: datetime.datetime, location_info: astral.LocationInfo
    ) -> int:
        # We set to 0:00 AM so we can ensure the delta between two times is always N days
        current_time = datetime.datetime(
            current_time.year,
            current_time.month,
            current_time.day,
            tzinfo=current_time.tzinfo,
        )
        key = (location_info.longitude, location_info.latitude)
        try:
            reference = self.location_info_to_reference[key]
        except KeyError:
            reference = self.location_info_to_reference[key] = (
                current_time,
                lunar_phase(current_time, location_info),
            )
        difference = current_time - reference[0]
        return round((reference[1] + difference.days) % MAX_LUNAR_PHASE)


def lunar_phase(current_time: datetime.datetime, location_info: astral.LocationInfo):
    earth_location = astral_location_to_astropy_location(location_info)
    previous_time = current_time - datetime.timedelta(seconds=1)
    apytime, previous_apytime = (
        datetime_to_astropy_time(t) for t in (current_time, previous_time)
    )
    # Okay, here we get something from 0 - 1, where 0 is new moon and 1 is
    # full moon. So the whole movement of one lunar phase is from 0 to 1 to 0.
    # We need to map this to a linear scale: let's say from 0 - 2.
    angle_index = moon_sun_angle_index(earth_location, apytime)
    previous_angle_index = moon_sun_angle_index(earth_location, previous_apytime)
    # For this we use this simple formula, and then we have values
    # from 0 - 2 :)
    if previous_angle_index > angle_index:
        angle_index = (1 - angle_index) + 1
    # But we actually want to have values from 0 to MAX_LUNAR_PHASE (~ 29).
    # So let's make a simple multiplication :)
    return (angle_index / 2) * MAX_LUNAR_PHASE


def moon_sun_angle_index(
    earth_location: coordinates.EarthLocation, current_time: astropy_time.Time
) -> float:
    """fetch moon visibility index
    0 == moon is not visible ('new moon')
    1 == moon is fully visible ('full moon')
    """
    moon = coordinates.get_moon(current_time, earth_location)
    sun = coordinates.get_sun(current_time)
    return moon.separation(sun).deg / ANGLE_RANGE.end


def astral_location_to_astropy_location(
    astral_location: astral.LocationInfo,
) -> coordinates.EarthLocation:
    return coordinates.EarthLocation.from_geodetic(
        astral_location.longitude,
        astral_location.latitude,
        height=astral_location.elevation,
    )


def datetime_to_astropy_time(datetime_time: datetime.datetime) -> astropy_time.Time:
    return astropy_time.Time(val=datetime_time)


ANGLE_RANGE = ranges.Range(0, 180)
MAX_LUNAR_PHASE = 29.53  # wikipedia
