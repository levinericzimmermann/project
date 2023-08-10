import unittest

from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_interfaces

j = music_parameters.JustIntonationPitch
n = music_events.NoteLike


class ReverseBaritonePitchTest(unittest.TestCase):
    def setUp(self):
        self.r = project_interfaces.reverse_baritone_pitch

    def test_center(self):
        self.assertEqual(self.r(j("1/2")), j("1/2"))

    def test_higher(self):
        self.assertEqual(self.r(j("3/5")), j("5/12"))

    def test_lower(self):
        self.assertEqual(self.r(j("5/12")), j("3/5"))


class TableCanonTest(unittest.TestCase):
    def setUp(self):
        self.table_canon = project_interfaces.TableCanon(
            core_events.SequentialEvent([n("1/2"), n("8/15"), n("3/5"), n("8/15")])
        )

    def test_simultaneous_event(self):
        self.assertTrue(self.table_canon.simultaneous_event)
