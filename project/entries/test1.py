"""Test entry that returns a very simple event."""

from mutwo import core_parameters
from mutwo import mmml_converters
from mutwo import music_parameters
from mutwo import project_converters
from mutwo import project_interfaces

j = music_parameters.JustIntonationPitch
R = project_interfaces.Resonator


def is_supported(context, *args, **kwargs):
    return True


def main(context, *args, **kwargs) -> project_interfaces.PEntryReturnType:
    resonator_tuple = project_interfaces.ResonatorTuple(
        [
            R(
                delay=core_parameters.DirectDuration(8),
                resonating_pitch_tuple=(j("1/1"),),
            ),
            R(
                delay=core_parameters.DirectDuration(0),
                resonating_pitch_tuple=(j("3/2"),),
            ),
        ]
    )
    e = mmml2e(mmml)
    e.append(re2res.convert(resonator_tuple, e))

    # Apply tonic
    e.set_parameter(
        "pitch_list", lambda pl: [p + context.tonic for p in pl] if pl else []
    )

    return (e, resonator_tuple)


mmml = r"""
sim

    seq b

        inh s
        exh s
        inh s
        exh s

    seq v

        n 1 1/1
        n 1 3/2
        r 1
        n 1 3/2
"""

re2res = project_converters.ResonatorTupleAndEventToResonances()
mmml2e = mmml_converters.MMMLExpressionToEvent()
