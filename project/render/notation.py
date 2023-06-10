import concurrent.futures
import subprocess

import abjad

from mutwo import abjad_converters
from mutwo import clock_converters
from mutwo import clock_generators
from mutwo import core_events

import project

MAX_DENOMINATOR = 100000


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

    complex_event_to_abjad_container = (
        clock_generators.make_complex_event_to_abjad_container(
            sequential_event_to_abjad_staff_kwargs=dict(
                post_process_abjad_container_routine_sequence=(
                    PostProcessClockSequentialEvent(),
                ),
                mutwo_volume_to_abjad_attachment_dynamic=None,
            ),
            duration_line=True,
        )
    )
    return clock_converters.ClockEventToAbjadStaffGroup(
        complex_event_to_abjad_container
    )


def pclock_tag_to_converter(small=True):
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
                _make_small(first_leaf, -6)
                abjad.attach(abjad.Clef("percussion"), first_leaf)
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\override Staff.StaffSymbol.line-count = #0 "
                        # Parts of PrepareForDurationLineBasedNotation which
                        # are useful here.
                        r"\override Staff.Dots.dot-count = #0 "
                        r"\omit Staff.MultiMeasureRest "
                        r"\override Staff.Dots.dot-count = #0 "
                        r"\override Staff.NoteHead.duration-log = 2 "
                        r"\hide Staff.Clef "
                        r"\hide Staff.BarLine "
                    ),
                    first_leaf,
                )
            for leaf in leaf_sequence:

                # This is a fix for a very strange bug: for reasons I don't
                # understand the code which replaces rests with skips is never
                # executed for the 'pclock'. So in order to still replace the rests
                # with the skips we add the next three lines. Of course it would be
                # much better if we would simply know what's the actual problem.
                if isinstance(leaf, abjad.Rest):
                    abjad.mutate.replace(leaf, abjad.Skip(leaf.written_duration))

    complex_event_to_abjad_container = clock_generators.make_complex_event_to_abjad_container(
        sequential_event_to_abjad_staff_kwargs=dict(
            post_process_abjad_container_routine_sequence=(
                PostProcessClockSequentialEvent(),
            ),
            mutwo_volume_to_abjad_attachment_dynamic=None,
        ),
        duration_line=True,
    )

    pclock_tag = "pclock"

    class EventPlacementToAbjadStaffGroup(
        clock_converters.EventPlacementToAbjadStaffGroup
    ):
        def convert(self, event_placement, *args, **kwargs):
            pclock_event = event_placement.event[pclock_tag]
            if isinstance(pclock_event, core_events.TaggedSimultaneousEvent):
                pass
            return super().convert(event_placement, *args, **kwargs)

    return {
        pclock_tag: EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=1,
            max_denominator=MAX_DENOMINATOR,
        ),
    }


def get_converter(tag, small=False):
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
                if small:
                    _make_small(first_leaf)
                abjad.attach(abjad.Clef("treble"), first_leaf)
                # abjad.attach(
                #     abjad.LilyPondLiteral(r'\accidentalStyle "dodecaphonic"'),
                #     first_leaf,
                # )
                abjad.attach(
                    abjad.LilyPondLiteral(r"\hide NoteHead" "\n"),
                    first_leaf,
                )
                _set_duration_line(first_leaf)

            # If we have instable pitches, they can either be a
            # minor or a major interval. We show this to others by
            # adding parenthesis to the accidental (= can be added, but
            # doesn't need to).
            if tag in ("written_instable_pitch",):
                for leaf in leaf_sequence:
                    try:
                        leaf.note_head.is_cautionary = True
                    except AttributeError:
                        pass

            for leaf in leaf_sequence:
                abjad.attach(
                    # abjad.LilyPondLiteral(r"-\tweak X-offset #1", site="absolute_after"), leaf
                    abjad.LilyPondLiteral(
                        r"\override Accidental.X-offset = 0.5"
                        "\n"
                        r"\override AccidentalCautionary.X-offset = -0.6",
                        site="before",
                    ),
                    leaf,
                )

    class EventPlacementToAbjadStaffGroup(
        clock_converters.EventPlacementToAbjadStaffGroup
    ):
        def convert(self, event_placement, *args, **kwargs):
            event = event_placement.event[tag]
            if isinstance(event, core_events.TaggedSimultaneousEvent):
                ...  # If customization is needed

            return super().convert(event_placement, *args, **kwargs)

    complex_event_to_abjad_container = clock_generators.make_complex_event_to_abjad_container(
        duration_line=True,
        sequential_event_to_abjad_staff_kwargs=dict(
            mutwo_pitch_to_abjad_pitch=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
            mutwo_volume_to_abjad_attachment_dynamic=None,
            post_process_abjad_container_routine_sequence=(
                PostProcessSequentialEvent(),
            ),
        ),
    )

    converter = {
        tag: EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=1,
            max_denominator=MAX_DENOMINATOR,
        ),
    }
    return converter


def score_converter():
    converter_dict = pclock_tag_to_converter()
    for c in (
        get_converter("tonic"),
        get_converter("partner"),
        get_converter("written_instable_pitch"),
    ):
        converter_dict.update(c)
    return converter_dict


def notation(clock_tuple, notate_item):
    # set to true if you only want score creation but not expensive notation render
    omit_notation = False

    with concurrent.futures.ThreadPoolExecutor() as executor:
        path_list = []
        if p := _notation(
            "score",
            score_converter(),
            ("pclock", "tonic", "partner", "written_instable_pitch"),
            clock_tuple,
            executor,
            omit_notation,
        ):
            path_list.append(p)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for path in path_list:
            _score(path, executor)


def _notation(
    name,
    tag_to_abjad_staff_group_converter,
    tag_tuple,
    clock_tuple,
    executor,
    omit_notation,
):
    notation_path = f"builds/notations/{project.constants.TITLE}_{name}.pdf"

    if omit_notation:
        return notation_path

    print("\n\nNotate", name)

    clock_to_abjad_score = clock_converters.ClockToAbjadScore(
        tag_to_abjad_staff_group_converter,
        clock_event_to_abjad_staff_group=clock_event_to_abjad_staff_group(),
    )

    abjad_score_to_abjad_score_block = clock_converters.AbjadScoreToAbjadScoreBlock()

    abjad_score_block_list = []
    for clock in clock_tuple:
        abjad_score = clock_to_abjad_score.convert(
            clock, tag_tuple=tag_tuple, ordered_tag_tuple=tag_tuple
        )

        abjad_score_block = abjad_score_to_abjad_score_block.convert(
            abjad_score,
            consist_timing_translator=True,
            # Setting a lower 'moment' decreases the likelihood that we catch
            # the following lilypond error:
            #   Drawing systems...lilypond: skyline.cc:100: Building::Building(Real, Real, Real, Real): Assertion `start_height == end_height' failed.
            moment=1,  # 1/16 is one second
            strict_grace_spanning=False,
            staff_staff_spacing_minimum_distance=7,
            staff_staff_spacing_basic_distance=8,
            ragged_right=False,
            ragged_last=False,
        )
        abjad_score_block_list.append(abjad_score_block)

    lilypond_file = clock_converters.AbjadScoreBlockTupleToLilyPondFile(
        system_system_basic_distance=5,
        system_system_padding=1,
        score_system_basic_distance=0,
        score_system_padding=0,
        markup_system_basic_distance=0,
        markup_system_padding=0,
        staff_height=20,
        top_margin=-1,
        foot_separation=0,
        head_separation=0,
        bottom_margin=1,
        line_width=29,
        left_margin=1,
        page_top_space=0,
        between_title_space=0,
        after_title_space=0,
        before_title_space=0,
        print_page_number=False,
    ).convert(abjad_score_block_list)

    lilypond_file.items.insert(0, r'\include "etc/lilypond/ar.ily"')
    lilypond_file.items.insert(0, r'\include "etc/lilypond/bridge.ily"')
    lilypond_file.items.insert(0, r'\include "etc/lilypond/overpressure.ily"')
    lilypond_file.items.insert(0, r'\include "etc/lilypond/sync.ily"')
    lilypond_file.items.insert(0, r'\include "etc/lilypond/ekme-heji.ily"')

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


def _make_small(leaf, magnification_size=-3):
    abjad.attach(
        abjad.LilyPondLiteral(rf"\magnifyStaff #(magstep {magnification_size})"), leaf
    )


def _set_duration_line(leaf, thickness=7):
    abjad.attach(
        abjad.LilyPondLiteral(
            rf"\override DurationLine.thickness = {thickness}"
            "\n"
            r"\override DurationLine.style = #'line"
            "\n"
            r"\override DurationLine.bound-details.right.padding = 1"
            "\n"
            r"\override DurationLine.bound-details.left.padding = 1"
        ),
        leaf,
    )
