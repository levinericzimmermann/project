import operator
import typing

import ranges

from mutwo import core_events
from mutwo import clock_events
from mutwo import music_parameters


def is_supported(context, pitch=None, **kwargs):
    orchestration = context.orchestration
    try:
        assert context.modal_event.start_pitch is not None
        assert context.modal_event.end_pitch is not None
        assert len(orchestration) == 1
        instrument = orchestration[0]
        assert instrument.is_pitched
        assert instrument.pitch_count_range.end >= 3
        assert isinstance(context.modal_event, clock_events.ModalEvent0)
        assert len(context.modal_event.scale.pitch_tuple) > 2
        if pitch is None:
            # returns 'None' if pitch isn't part of the insturment
            pitch = get_unspecified_pitch(context, instrument)
        assert pitch is not None
        assert pitch in instrument  # if pitch is user set
    except AssertionError:
        return False
    return True


def main(
    context,
    pitch=None,
    direction=None,
    prohibited_pitch_list=[],
    distance_range=ranges.Range(2, 6),
    **kwargs
) -> tuple[music_parameters.JustIntonationPitch, music_parameters.JustIntonationPitch]:
    if pitch is None:
        pitch = get_unspecified_pitch(context)

    scale = context.modal_event.scale
    return find_dyad(
        pitch,
        scale,
        direction=direction,
        distance_range=distance_range,
        prohibited_pitch_list=prohibited_pitch_list,
    )


DIRECTION_TO_OPERATION_TUPLE_DICT = {
    None: (operator.add, operator.sub),
    True: (operator.add,),
    False: (operator.sub,),
}


def get_dyad_partner_candidate_list(
    pitch, scale, direction, distance_range, prohibited_pitch_list
):
    pitch_index = scale.pitch_to_scale_index(pitch)
    # Let's find pitches in the close range
    dyad_partner_candidate_list = []
    for operation in DIRECTION_TO_OPERATION_TUPLE_DICT[direction]:
        for partner_candidate_index in range(distance_range.start, distance_range.end):
            partner_candidate_index = operation(pitch_index, partner_candidate_index)
            try:
                partner_candidate = scale.scale_index_to_pitch(partner_candidate_index)
            except IndexError:
                continue
            if partner_candidate not in prohibited_pitch_list:
                dyad_partner_candidate_list.append(partner_candidate)
    return dyad_partner_candidate_list


def find_dyad(
    pitch: music_parameters.JustIntonationPitch,
    scale: music_parameters.Scale,
    direction: typing.Optional[bool],
    distance_range,
    prohibited_pitch_list,
) -> tuple[music_parameters.JustIntonationPitch, music_parameters.JustIntonationPitch]:

    dyad_partner_candidate_list = get_dyad_partner_candidate_list(
        pitch, scale, direction, distance_range, prohibited_pitch_list
    )
    # We try to avoid octaves
    filtered_dyad_partner_candidate_tuple = tuple(
        filter(
            lambda candidate: round(abs((candidate - pitch).interval) % 1200, 2) != 0,
            dyad_partner_candidate_list,
        )
    )

    # If we only have octaves, then we'll also take octaves, okay
    if not filtered_dyad_partner_candidate_tuple:
        filtered_dyad_partner_candidate_tuple = tuple(dyad_partner_candidate_list)

    interval_tuple = tuple(
        pitch - candidate for candidate in filtered_dyad_partner_candidate_tuple
    )
    try:
        harmonicity_tuple = tuple(
            interval.harmonicity_simplified_barlow for interval in interval_tuple
        )
    except AttributeError:
        raise NotImplementedError(
            "Algorithm 'dyad' only works with just intonation pitches!"
        )

    champion_index = harmonicity_tuple.index(max(harmonicity_tuple))
    champion = filtered_dyad_partner_candidate_tuple[champion_index]
    dyad = (pitch, champion)

    return dyad


def get_unspecified_pitch(
    context, instrument
) -> typing.Optional[music_parameters.abc.Pitch]:
    pitch_variant_tuple = instrument.get_pitch_variant_tuple(
        context.modal_event.end_pitch
    )
    return pitch_variant_tuple[0] if pitch_variant_tuple else None
