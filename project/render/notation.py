import concurrent.futures
import subprocess
import warnings

import abjad

from mutwo import abjad_converters
from mutwo import clock_converters
from mutwo import clock_generators
from mutwo import core_events
from mutwo import project_converters
from mutwo import project_utilities

import project

MAX_DENOMINATOR = 100000


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
        ),
        duration_line=True,
        # duration_line=False,
    )
    return clock_converters.ClockEventToAbjadStaffGroup(
        complex_event_to_abjad_container
    )


@run
def pclock_tag_to_converter():
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
                        r"\override Staff.StaffSymbol.line-count = #1 "
                        # Parts of PrepareForDurationLineBasedNotation which
                        # are useful here.
                        r"\override Staff.Dots.dot-count = #0 "
                        r"\omit Staff.MultiMeasureRest "
                        r"\override Staff.Dots.dot-count = #0 "
                        r"\override Staff.NoteHead.duration-log = 2 "
                    ),
                    first_leaf,
                )
            # This is a fix for a very strange bug: for reasons I don't
            # understand the code which replaces rests with skips is never
            # executed for the 'pclock'. So in order to still replace the rests
            # with the skips we add the next three lines. Of course it would be
            # much better if we would simply know what's the actual problem.
            for leaf in leaf_sequence:
                if isinstance(leaf, abjad.Rest):
                    abjad.mutate.replace(leaf, abjad.Skip(leaf.written_duration))

            # # Explicit beams are never needed here.
            # for leaf in leaf_sequence:
            #     abjad.detach(abjad.StartBeam, leaf)
            #     abjad.detach(abjad.StopBeam, leaf)

    complex_event_to_abjad_container = clock_generators.make_complex_event_to_abjad_container(
        sequential_event_to_abjad_staff_kwargs=dict(
            post_process_abjad_container_routine_sequence=(
                PostProcessClockSequentialEvent(),
            ),
            mutwo_volume_to_abjad_attachment_dynamic=None,
            # We don't want the 'omit Staff.Beam' etc. parts,
            # because they remove the beams etc. of grace notes
            # or tremolo notes, where we want to print them.
            # So we can't do this globally in the way how we did
            # it there.
            prepare_for_duration_line_based_notation=False,
        ),
        duration_line=True,
        # duration_line=False,
    )
    pclock_tag = project.constants.ORCHESTRATION.PCLOCK.name

    class EventPlacementToAbjadStaffGroup(
        clock_converters.EventPlacementToAbjadStaffGroup
    ):
        def convert(self, event_placement, *args, **kwargs):
            pclock_event = event_placement.event[pclock_tag]
            if isinstance(pclock_event, core_events.TaggedSimultaneousEvent):
                event_placement.event[
                    pclock_tag
                ] = project.constants.INSTRUMENT_CLOCK_EVENT_TO_PITCHED_CLOCK_EVENT(
                    pclock_event
                )
            return super().convert(event_placement, *args, **kwargs)

    return {
        pclock_tag: EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=1,
            max_denominator=MAX_DENOMINATOR,
        ),
    }


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

                # Split if it hasn't been split yet
                if (seq_event_count := len(harp_event)) == 1:
                    event_placement.event[harp_tag] = project_utilities.split_harp(
                        harp_event[0], harp_tag
                    )
                elif seq_event_count > 2:
                    warnings.warn("Found harp event with more than 2 SequentialEvent")

                # # We usually have a monophonic structure where both hands
                # # behave equally. So it's sufficient to print the accent in
                # # only the right hand.
                # for i, e in enumerate(right):
                #     if e.playing_indicator_collection.articulation.name == ">":
                #         left[i].playing_indicator_collection.articulation.name = None
            return super().convert(event_placement, *args, **kwargs)

    harp_converter = {
        harp_tag: EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=2,
            max_denominator=MAX_DENOMINATOR,
        )
    }
    harp_converter.update(pclock_tag_to_converter)
    return harp_converter


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

    v_converter = {
        v_tag: EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=1,
            max_denominator=MAX_DENOMINATOR,
        ),
    }
    v_converter.update(pclock_tag_to_converter)
    return v_converter


@run
def glockenspiel_converter():
    glockenspiel_tag = project.constants.ORCHESTRATION.GLOCKENSPIEL.name

    class PostProcessSequentialEvent(abjad_converters.ProcessAbjadContainerRoutine):
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
                abjad.attach(abjad.Clef("treble^15"), first_leaf)

    class EventPlacementToAbjadStaffGroup(
        clock_converters.EventPlacementToAbjadStaffGroup
    ):
        def convert(self, event_placement, *args, **kwargs):
            return super().convert(event_placement, *args, **kwargs)

    complex_event_to_abjad_container = (
        clock_generators.make_complex_event_to_abjad_container(
            duration_line=True,
            sequential_event_to_abjad_staff_kwargs=dict(
                mutwo_volume_to_abjad_attachment_dynamic=None,
                post_process_abjad_container_routine_sequence=(
                    PostProcessSequentialEvent(),
                ),
            ),
        )
    )

    glockenspiel_converter = {
        glockenspiel_tag: EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=1,
            max_denominator=MAX_DENOMINATOR,
        ),
    }
    glockenspiel_converter.update(pclock_tag_to_converter)
    return glockenspiel_converter


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

    if omit_notation:
        return notation_path

    converter_name = f"{instrument.name}_converter"
    try:
        tag_to_abjad_staff_group_converter = globals()[converter_name]
    except KeyError:
        return

    print("\n\nNotate", instrument.name)

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
                project.constants.ORCHESTRATION.PCLOCK.name,
                project.constants.ORCHESTRATION.GLOCKENSPIEL.name,
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
            moment=2,  # 1/16 is one second
        )
        abjad_score_block_list.append(abjad_score_block)

    lilypond_file = clock_converters.AbjadScoreBlockTupleToLilyPondFile(
        system_system_padding=3,
        system_system_basic_distance=12,
        score_system_padding=3,
        markup_system_padding=1,
        staff_height=20,
    ).convert(abjad_score_block_list)

    lilypond_file.items.insert(0, r'\include "etc/lilypond/ar.ily"')

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
