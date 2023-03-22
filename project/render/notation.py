import subprocess

import abjad

from mutwo import abjad_converters
from mutwo import clock_converters
from mutwo import clock_generators
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_converters

import project


def run(f):
    return f()


@run
def clock_event_to_abjad_staff_group():
    class PostProcessClockSequentialEvent(
        abjad_converters.ProcessAbjadContainerRoutine
    ):
        def __call__(
            self,
            complex_event_to_convert: core_events.abc.ComplexEvent,
            container_to_process: abjad.Container,
        ):
            leaf_sequence = abjad.select.leaves(container_to_process)
            try:
                first_leaf = leaf_sequence[0]
            except IndexError:
                pass
            else:
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\override Staff.StaffSymbol.line-count = #0 "
                        r"\stopStaff \omit Staff.Clef \omit Staff.NoteHead "
                        r"\hide Staff.BarLine "
                    ),
                    first_leaf,
                )

    complex_event_to_abjad_container = clock_generators.make_complex_event_to_abjad_container(
        sequential_event_to_abjad_staff_kwargs=dict(
            post_process_abjad_container_routine_sequence=(
                PostProcessClockSequentialEvent(),
            ),
            mutwo_volume_to_abjad_attachment_dynamic=None,
            write_multimeasure_rests=False,
        ),
        duration_line=True,
        # duration_line=False,
    )
    return clock_converters.ClockEventToAbjadStaffGroup(
        complex_event_to_abjad_container
    )


@run
def aeolian_harp_converter():
    class PostProcessClockSequentialEvent(
        abjad_converters.ProcessAbjadContainerRoutine
    ):
        def __call__(
            self,
            complex_event_to_convert: core_events.abc.ComplexEvent,
            container_to_process: abjad.Container,
        ):
            leaf_sequence = abjad.select.leaves(container_to_process)
            try:
                first_leaf = leaf_sequence[0]
            except IndexError:
                pass
            else:
                abjad.attach(
                    abjad.LilyPondLiteral(r"\magnifyStaff #(magstep -4) "),
                    first_leaf,
                )

    atag = "aeolian harp"

    class EventPlacementToAbjadStaffGroup(
        clock_converters.EventPlacementToAbjadStaffGroup
    ):
        def convert(self, event_placement, *args, **kwargs):
            event = event_placement.event[atag]
            if isinstance(event, core_events.SimultaneousEvent):
                absolute_time_list = [event.duration]
                for e in event:
                    for t in e.absolute_time_tuple:
                        if t not in absolute_time_list:
                            absolute_time_list.append(t)
                absolute_time_tuple = tuple(sorted(absolute_time_list))
                new_sequential_event = core_events.SequentialEvent([])
                for start, stop in zip(absolute_time_tuple, absolute_time_tuple[1:]):
                    note_like = music_events.NoteLike([], stop - start, "p")
                    for s in event:
                        if hasattr((e := s.get_event_at(start)), "pitch_list"):
                            for p in e.pitch_list:
                                if p not in note_like.pitch_list:
                                    note_like.pitch_list.append(p)
                    new_sequential_event.append(note_like)
                new_sequential_event.set_parameter(
                    "pitch_list",
                    lambda pl: [
                        p - music_parameters.JustIntonationPitch("2/1") for p in pl
                    ],
                )
                for e in new_sequential_event:
                    if hasattr(e, "notation_indicator_collection"):
                        e.notation_indicator_collection.clef.name = "alto"
                event_placement.event[atag] = core_events.TaggedSimultaneousEvent(
                    [new_sequential_event], tag=atag
                )

            return super().convert(event_placement, *args, **kwargs)

    complex_event_to_abjad_container = clock_generators.make_complex_event_to_abjad_container(
        sequential_event_to_abjad_staff_kwargs=dict(
            mutwo_pitch_to_abjad_pitch=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
            mutwo_volume_to_abjad_attachment_dynamic=None,
            post_process_abjad_container_routine_sequence=(
                PostProcessClockSequentialEvent(),
            ),
            write_multimeasure_rests=False,
        )
    )

    return {
        "aeolian harp": EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=1,
            placement_mode="floating",
        ),
    }


@run
def clavichord_converter():
    class EventPlacementToAbjadStaffGroup(
        clock_converters.EventPlacementToAbjadStaffGroup
    ):
        def convert(self, event_placement, *args, **kwargs):
            event = event_placement.event[clavichord_tag]
            if isinstance(event, core_events.TaggedSimultaneousEvent):
                # sounding -> written
                event.set_parameter(
                    "pitch_list",
                    lambda pitch_list: [
                        sounding_clavichord_pitch_to_written_clavichord_pitch(pitch)
                        for pitch in pitch_list
                    ]
                    if pitch_list
                    else None,
                )
                # split staves
                border = music_parameters.WesternPitch("c", 4)
                right = event.set_parameter(
                    "pitch_list",
                    lambda pitch_list: [p for p in pitch_list if p >= border]
                    if pitch_list
                    else None,
                    mutate=False,
                )[0]
                left = event.set_parameter(
                    "pitch_list",
                    lambda pitch_list: [p for p in pitch_list if p < border]
                    if pitch_list
                    else None,
                    mutate=False,
                )[0]

                for note_like in right:
                    if notation_indicator_collection := getattr(
                        note_like, "notation_indicator_collection", None
                    ):
                        notation_indicator_collection.clef.name = "treble"

                for note_like in left:
                    if notation_indicator_collection := getattr(
                        note_like, "notation_indicator_collection", None
                    ):
                        notation_indicator_collection.clef.name = "bass"
                        break

                event_placement.event[
                    clavichord_tag
                ] = core_events.TaggedSimultaneousEvent(
                    [right, left], tag=clavichord_tag
                )

            return super().convert(event_placement, *args, **kwargs)

    complex_event_to_abjad_container = (
        clock_generators.make_complex_event_to_abjad_container(
            sequential_event_to_abjad_staff_kwargs=dict(
                mutwo_volume_to_abjad_attachment_dynamic=None,
                write_multimeasure_rests=False,
            ),
        )
    )

    clavichord_tag = "clavichord"

    return {
        clavichord_tag: EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=2,
            placement_mode="floating",
        ),
    }


def sounding_clavichord_pitch_to_written_clavichord_pitch(p):
    try:
        scale_position = SCALE.pitch_to_scale_position(p)
    except ValueError:
        print(f"Can't find pitch {p.ratio}")
        return music_parameters.WesternPitch()
    p = SCALE_TRANSPOSED.scale_position_to_pitch(scale_position)
    if p.pitch_class_name == "bs":  # stupid rounding conversion?
        p = music_parameters.WesternPitch("c", p.octave + 1)
    p = music_parameters.WesternPitch(p.pitch_class_name, p.octave - 1)
    return p


def get_clavichord_tuning():
    diff_list = []
    for scale_degree in range(7):
        sounding, written = (
            s.scale_position_to_pitch((scale_degree, 0))
            for s in (SCALE, SCALE_TRANSPOSED)
        )
        diff = round(written.get_pitch_interval(sounding).interval, 2)
        r = f"{sounding.ratio.numerator}/{sounding.ratio.denominator}"
        diff_list.append(f"{written.pitch_class_name} ({r}): {diff}")
    return ", ".join(diff_list)


def get_aeolian_harp_tuning(orchestration):
    aeolian_harp = orchestration.AEOLIAN_HARP
    tuning = []
    for box_index, string_tuple in enumerate(aeolian_harp.string_tuple_for_each_box):
        tuning_part = []
        for string in string_tuple:
            p = string.tuning
            pname = p.get_closest_pythagorean_pitch_name()
            dev = round(p.cent_deviation_from_closest_western_pitch_class, 2)
            ratio = (p + music_parameters.JustIntonationPitch("2/1")).ratio
            pitch_data = f"{pname} ({ratio}): {dev}"
            tuning_part.append(pitch_data)
        tuning_part = ", ".join(tuning_part)
        tuning.append(f"b{box_index + 1} [{tuning_part}]")
    return "; ".join(tuning)


SCALE = None
SCALE_TRANSPOSED = music_parameters.Scale(
    music_parameters.WesternPitch("a", 4),
    music_parameters.RepeatingScaleFamily(
        tuple(
            music_parameters.WesternPitchInterval(i)
            for i in "p1 M2 m3 p4 p5 m6 m7".split(" ")
        ),
        min_pitch_interval=music_parameters.WesternPitchInterval("p-22"),
        max_pitch_interval=music_parameters.WesternPitchInterval("p22"),
    ),
)


def notation(clock_tuple, d, scale, orchestration, path, executor):
    global SCALE
    SCALE = scale
    formatted_time = f"{d.year}.{d.month}.{d.day}, {d.hour}:{d.minute}"
    title = (
        r'\markup { \fontsize #-4 \medium \typewriter { "10.1, evening twilight, '
        f'{formatted_time}, essen"'
        r"} }"
    )
    aeolian_harp_tuning = get_aeolian_harp_tuning(orchestration)
    subtitle = rf'\markup {{ \fontsize #-2 \typewriter \medium {{ "{get_clavichord_tuning()}" }} }}'
    composer = rf'\markup {{ \fontsize #-2 \typewriter \medium {{ "{aeolian_harp_tuning}" }} }}'
    abjad_score_to_abjad_score_block = clock_converters.AbjadScoreToAbjadScoreBlock()
    instrument_note_like_to_pitched_note_like = (
        project_converters.InstrumentNoteLikeToPitchedNoteLike(
            project.constants.CLOCK_INSTRUMENT_TO_PITCH_DICT
        )
    )
    tag_to_abjad_staff_group_converter = clavichord_converter
    tag_to_abjad_staff_group_converter.update(aeolian_harp_converter)

    clock_to_abjad_score = clock_converters.ClockToAbjadScore(
        tag_to_abjad_staff_group_converter,
        clock_event_to_abjad_staff_group=clock_event_to_abjad_staff_group,
    )

    abjad_score_block_list = []
    for clock in clock_tuple:
        for clock_line in (
            clock.main_clock_line,
            clock.start_clock_line,
            clock.end_clock_line,
        ):
            if clock_line:
                # Remove first + last event placement of clavichord
                clock_line.sort()
                prohibited_event_placement_index_list = []
                for i, ep in enumerate(clock_line._event_placement_list):
                    if "clavichord" in ep.event:
                        prohibited_event_placement_index_list.append(i)
                        break
                for i, ep in enumerate(reversed(clock_line._event_placement_list)):
                    if "clavichord" in ep.event:
                        prohibited_event_placement_index_list.append(
                            len(clock_line._event_placement_list) - 1 - i
                        )
                        break
                clock_line._event_placement_list = [
                    ep
                    for i, ep in enumerate(clock_line._event_placement_list)
                    if i not in prohibited_event_placement_index_list
                ]

                # ####
                clock_line._clock_event = instrument_note_like_to_pitched_note_like(
                    clock_line.clock_event
                )
        abjad_score = clock_to_abjad_score.convert(
            clock,
            tag_tuple=("clavichord", "aeolian harp"),
        )

        # We get lilypond error for harp:
        #   Interpreting music...[8][16][24]ERROR: Wrong type (expecting exact integer): ()
        consist_timing_translator = True
        # We get lilypond error for violin:
        #   Drawing systems...lilypond: skyline.cc:100: Building::Building(Real, Real, Real, Real): Assertion `start_height == end_height' failed.
        # if instrument.name == "violin":
        #     consist_timing_translator = False

        abjad_score_block = abjad_score_to_abjad_score_block.convert(
            abjad_score,
            consist_timing_translator=consist_timing_translator,
            # Setting a lower 'moment' decreases the likelihood that we catch
            # the following lilypond error:
            #   Drawing systems...lilypond: skyline.cc:100: Building::Building(Real, Real, Real, Real): Assertion `start_height == end_height' failed.
            moment=4,  # 1/16 is one second
        )
        abjad_score_block_list.append(abjad_score_block)

    lilypond_file = clock_converters.AbjadScoreBlockTupleToLilyPondFile(
        system_system_padding=1,
        system_system_basic_distance=1,
        score_system_padding=1,
        score_system_basic_distance=1,
        markup_system_padding=1,
        markup_system_basic_distance=1,
        staff_height=20,
    ).convert(
        abjad_score_block_list,
        title=title,
        subtitle=subtitle,
        composer=composer,
        # tagline=rf'\markup {{ \typewriter {{ "{formatted_time}" }} }}',
    )

    lilypond_file.items.insert(0, r'\include "etc/lilypond/ekme-heji.ily"')
    return executor.submit(abjad.persist.as_pdf, lilypond_file, path)


def merge_notation(path_list: list[str]):
    command = (
        ["pdftk"] + path_list + ["output", f"builds/{project.constants.TITLE}.pdf"]
    )
    subprocess.call(command)
