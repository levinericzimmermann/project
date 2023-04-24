import concurrent.futures
import subprocess

import abjad

from mutwo import abjad_converters
from mutwo import clock_converters
from mutwo import clock_generators
from mutwo import core_events
from mutwo import core_utilities
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
                abjad.attach(abjad.Clef("percussion"), first_leaf)
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\override Staff.StaffSymbol.line-count = #3"
                    ),
                    first_leaf,
                )

    complex_event_to_abjad_container = clock_generators.make_complex_event_to_abjad_container(
        sequential_event_to_abjad_staff_kwargs=dict(
            post_process_abjad_container_routine_sequence=(
                PostProcessClockSequentialEvent(),
            ),
            mutwo_volume_to_abjad_attachment_dynamic=None,
        ),
        duration_line=True,
        # duration_line=False,
    )
    return clock_converters.ClockEventToAbjadStaffGroup(
        complex_event_to_abjad_container
    )


@run
def harp_converter():
    class PostProcessHarpSequentialEvent(abjad_converters.ProcessAbjadContainerRoutine):
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
                # fill with custom code...
                pass

    complex_event_to_abjad_container = (
        clock_generators.make_complex_event_to_abjad_container(
            sequential_event_to_abjad_staff_kwargs=dict(
                post_process_abjad_container_routine_sequence=(
                    PostProcessHarpSequentialEvent(),
                ),
                mutwo_volume_to_abjad_attachment_dynamic=None,
            ),
        )
    )

    harp_tag = project.constants.ORCHESTRATION.HARP.name

    class EventPlacementToAbjadStaffGroup(
        clock_converters.EventPlacementToAbjadStaffGroup
    ):
        def convert(self, event_placement, *args, **kwargs):
            harp_event = event_placement.event[harp_tag]
            if isinstance(harp_event, core_events.TaggedSimultaneousEvent):
                # sounding -> written
                harp_event.set_parameter(
                    "pitch_list",
                    lambda pitch_list: [
                        project.constants.sounding_harp_pitch_to_written_harp_pitch(
                            pitch
                        )
                        for pitch in pitch_list
                    ]
                    if pitch_list
                    else None,
                )
                # split staves
                border = music_parameters.WesternPitch("c", 4)
                right = harp_event.set_parameter(
                    "pitch_list",
                    lambda pitch_list: [p for p in pitch_list if p >= border]
                    if pitch_list
                    else None,
                    mutate=False,
                )[0]
                left = harp_event.set_parameter(
                    "pitch_list",
                    lambda pitch_list: [p for p in pitch_list if p < border]
                    if pitch_list
                    else None,
                    mutate=False,
                )[0]
                for note_like in left:
                    if notation_indicator_collection := getattr(
                        note_like, "notation_indicator_collection", None
                    ):
                        notation_indicator_collection.clef.name = "bass"
                        break
                for seq in (right, left):
                    for e in seq:
                        if not e.pitch_list:
                            e.playing_indicator_collection = (
                                music_events.configurations.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS()
                            )
                event_placement.event[harp_tag] = core_events.TaggedSimultaneousEvent(
                    (right, left),
                    tag=harp_tag,
                )
            return super().convert(event_placement, *args, **kwargs)

    return {
        harp_tag: EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=2,
        ),
    }


@run
def v_converter():
    v_tag = project.constants.ORCHESTRATION.V.name

    class EventPlacementToAbjadStaffGroup(
        clock_converters.EventPlacementToAbjadStaffGroup
    ):
        def convert(self, event_placement, *args, **kwargs):
            # v_event = event_placement.event[v_tag]
            return super().convert(event_placement, *args, **kwargs)

    complex_event_to_abjad_container = (
        clock_generators.make_complex_event_to_abjad_container(
            duration_line=True,
            sequential_event_to_abjad_staff_kwargs=dict(
                mutwo_volume_to_abjad_attachment_dynamic=None,
            ),
        )
    )

    v_tag = project.constants.ORCHESTRATION.V.name

    return {
        v_tag: EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container, staff_count=1
        ),
    }


abjad_score_to_abjad_score_block = clock_converters.AbjadScoreToAbjadScoreBlock()
instrument_note_like_to_pitched_note_like = (
    project_converters.InstrumentNoteLikeToPitchedNoteLike(
        project.constants.CLOCK_INSTRUMENT_TO_PITCH_DICT
    )
)


def notation(clock_tuple):
    # set to true if you only want score creation but not expensive notation render
    omit_notation = False

    with concurrent.futures.ThreadPoolExecutor() as executor:
        path_list = []
        for instrument in project.constants.ORCHESTRATION:
            if p := _notation(instrument, clock_tuple, executor, omit_notation):
                path_list.append(p)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for path in path_list:
            _score(path, executor)


def _notation(instrument, clock_tuple, executor, omit_notation):
    notation_path = f"builds/notations/{project.constants.TITLE}_{instrument.name}.pdf"

    print("Notate", instrument.name)

    if omit_notation:
        return notation_path

    converter_name = f"{instrument.name}_converter"
    try:
        tag_to_abjad_staff_group_converter = globals()[converter_name]
    except KeyError:
        return
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
                clock_line._clock_event = (
                    project.constants.INSTRUMENT_CLOCK_EVENT_TO_PITCHED_CLOCK_EVENT(
                        clock_line.clock_event
                    )
                )
        abjad_score = clock_to_abjad_score.convert(
            clock,
            tag_tuple=(
                project.constants.ORCHESTRATION.HARP.name,
                project.constants.ORCHESTRATION.V.name,
            ),
        )

        # We get lilypond error for harp:
        #   Interpreting music...[8][16][24]ERROR: Wrong type (expecting exact integer): ()
        consist_timing_translator = True
        # We get lilypond error for v:
        #   Drawing systems...lilypond: skyline.cc:100: Building::Building(Real, Real, Real, Real): Assertion `start_height == end_height' failed.
        if instrument.name == "v":
            consist_timing_translator = False

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
        system_system_padding=3,
        system_system_basic_distance=12,
        score_system_padding=3,
        markup_system_padding=1,
        staff_height=20,
    ).convert(abjad_score_block_list)

    executor.submit(abjad.persist.as_pdf, lilypond_file, notation_path)
    return notation_path


def _score(path, executor):
    path_rotated = f"{path}_rotated.pdf"
    _rotate(path, path_rotated)
    path_merged = f"{path}_merged.pdf"
    _interleave(path_rotated, path_merged)
    path_with_intro = f"{path}_with_intro.pdf"
    _add_intro(path_merged, path_with_intro)


def _rotate(path_notation, path_rotated):
    subprocess.call(
        ["pdftk", path_notation, "cat", "1-endeast", "output", path_rotated]
    )


def _interleave(path_notation, path_merged):
    subprocess.call(
        [
            "pdftk",
            f"A={path_notation}",
            "B=builds/illustrations/poem.pdf",
            "shuffle",
            "A",
            "B",
            "output",
            path_merged,
        ]
    )


def _add_intro(path_notation, path_with_intro):
    subprocess.call(
        [
            "pdftk",
            "builds/illustrations/intro.pdf",
            path_notation,
            "output",
            path_with_intro,
        ]
    )
