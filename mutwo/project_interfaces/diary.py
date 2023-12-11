import dataclasses
import typing

from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_events
from mutwo import project_interfaces


@dataclasses.dataclass(frozen=True)
class ProjectContext(diary_interfaces.Context):
    tonic: music_parameters.JustIntonationPitch = music_parameters.JustIntonationPitch(
        "1/1"
    )
    previous_tonic: typing.Optional[music_parameters.JustIntonationPitch] = None
    next_tonic: typing.Optional[music_parameters.JustIntonationPitch] = None


# This type alias denotes what each project entry should return.
PEntryReturnType: typing.TypeAlias = tuple[
    # The first element in the tuple should simply be the actual music that
    # this entry creates. This is what we will finally see in the notation.
    core_events.SimultaneousEvent[
        # Breath event
        core_events.TaggedSequentialEvent[project_events.BreathEvent],
        # Whistling
        core_events.TaggedSequentialEvent[music_events.NoteLike],
        # Resonances
        #  Can be polyphon due to multiple resonators with different,
        #  maybe overlapping behaviour, therefore use a simultan event.
        core_events.TaggedSimultaneousEvent[
            core_events.SequentialEvent[music_events.NoteLike]
        ],
    ],
    # This object helps to finally create the live-electronics patch.
    # It's result is rendered in the event above in the last element
    # of the simultaneous event.
    project_interfaces.ResonatorTuple
]
