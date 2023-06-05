import concurrent.futures
import subprocess
import warnings

import abjad

from mutwo import abjad_converters
from mutwo import clock_converters
from mutwo import clock_generators
from mutwo import core_events
from mutwo import music_parameters
from mutwo import project_converters
from mutwo import project_utilities

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


def _pclock_tag_to_converter(small=True):
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
                if small:
                    _make_small(first_leaf)
                _make_thick_duration_line(first_leaf, 7)
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
            for leaf in leaf_sequence:

                # This is a fix for a very strange bug: for reasons I don't
                # understand the code which replaces rests with skips is never
                # executed for the 'pclock'. So in order to still replace the rests
                # with the skips we add the next three lines. Of course it would be
                # much better if we would simply know what's the actual problem.
                if isinstance(leaf, abjad.Rest):
                    abjad.mutate.replace(leaf, abjad.Skip(leaf.written_duration))

                # Fix broke tremolo (\AccRit) notation:
                # if the note has a beam (which goes to nowhere) the \AccRit
                # beam isn't printed.
                abjad.detach(abjad.StartBeam, leaf)

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


def _harp_converter(small=False):
    class PostProcessHarpSequentialEvent(abjad_converters.ProcessAbjadContainerRoutine):
        def __call__(
            self,
            complex_event_to_convert: core_events.abc.ComplexEvent,
            container_to_process: abjad.Container,
        ):
            leaf_sequence = abjad.select.leaves(container_to_process)
            try:
                first_leaf = leaf_sequence[0]
                last_leaf = leaf_sequence[-1]
            except IndexError:
                pass
            else:
                if small:
                    _make_small(first_leaf)
                # Remove potential ottava again, so it doesn't span over all rests etc.
                abjad.attach(abjad.Ottava(n=0, site="after"), last_leaf)
                _make_thick_duration_line(first_leaf)

    complex_event_to_abjad_container = (
        clock_generators.make_complex_event_to_abjad_container(
            duration_line=True,
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
                    harp_event = event_placement.event[
                        harp_tag
                    ] = project_utilities.split_harp(harp_event[0], harp_tag)
                elif seq_event_count > 2:
                    warnings.warn("Found harp event with more than 2 SequentialEvent")

                for seq in harp_event:
                    for note in seq:
                        octave_count = 0
                        if note.pitch_list:
                            if (
                                mpitch := max(note.pitch_list)
                            ) > music_parameters.JustIntonationPitch("8/1"):
                                octave_count = 2
                            elif mpitch > music_parameters.JustIntonationPitch("5/2"):
                                octave_count = 1
                        try:
                            note.notation_indicator_collection.ottava.octave_count = (
                                octave_count
                            )
                        except AttributeError:
                            pass

            return super().convert(event_placement, *args, **kwargs)

    harp_converter = {
        harp_tag: EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=2,
            max_denominator=MAX_DENOMINATOR,
        )
    }
    return harp_converter


def _v_converter(small=False):
    v_tag = project.constants.ORCHESTRATION.V.name

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
                abjad.attach(abjad.Clef("bass"), first_leaf)
                abjad.attach(
                    abjad.LilyPondLiteral(r'\accidentalStyle "dodecaphonic"'),
                    first_leaf,
                )

            for leaf in leaf_sequence:
                _make_thick_duration_line(leaf)

    class EventPlacementToAbjadStaffGroup(
        clock_converters.EventPlacementToAbjadStaffGroup
    ):
        def convert(self, event_placement, *args, **kwargs):
            event = event_placement.event[v_tag]

            if isinstance(event, core_events.TaggedSimultaneousEvent):
                pass

            return super().convert(event_placement, *args, **kwargs)

    complex_event_to_abjad_container = clock_generators.make_complex_event_to_abjad_container(
        duration_line=True,
        sequential_event_to_abjad_staff_kwargs=dict(
            mutwo_volume_to_abjad_attachment_dynamic=None,
            post_process_abjad_container_routine_sequence=(
                PostProcessSequentialEvent(),
            ),
            mutwo_pitch_to_abjad_pitch=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
        ),
    )

    v_tag = project.constants.ORCHESTRATION.V.name

    v_converter = {
        v_tag: EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=1,
            max_denominator=MAX_DENOMINATOR,
        ),
    }
    return v_converter


def _glockenspiel_converter(small=False):
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
                if small:
                    _make_small(first_leaf)
                abjad.attach(abjad.Clef("treble"), first_leaf)
                _make_thick_duration_line(first_leaf)

    class EventPlacementToAbjadStaffGroup(
        clock_converters.EventPlacementToAbjadStaffGroup
    ):
        def convert(self, event_placement, *args, **kwargs):
            event = event_placement.event[glockenspiel_tag]
            if isinstance(event, core_events.TaggedSimultaneousEvent):
                # sounding -> written
                event.set_parameter(
                    "pitch_list",
                    lambda pitch_list: [
                        project.constants.sounding_glockenspiel_pitch_to_written_glockenspiel_pitch(
                            pitch
                        )
                        for pitch in pitch_list
                    ]
                    if pitch_list
                    else None,
                )

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
    return glockenspiel_converter


def harp_converter():
    converter_dict = _harp_converter()
    for c in (
        _pclock_tag_to_converter(small=True),
        _glockenspiel_converter(small=True),
        _v_converter(small=True),
    ):
        converter_dict.update(c)
    return converter_dict


def v_converter():
    converter_dict = _v_converter()
    for c in (
        _pclock_tag_to_converter(small=True),
        _glockenspiel_converter(small=True),
        _harp_converter(small=True),
    ):
        converter_dict.update(c)
    return converter_dict


def glockenspiel_converter():
    converter_dict = _glockenspiel_converter()
    for c in (
        _pclock_tag_to_converter(small=False),
        _v_converter(small=True),
        _harp_converter(small=True),
    ):
        converter_dict.update(c)
    return converter_dict


def score_converter():
    converter_dict = _glockenspiel_converter(small=True)
    for c in (
        _pclock_tag_to_converter(small=True),
        _v_converter(small=True),
        _harp_converter(small=True),
    ):
        converter_dict.update(c)
    return converter_dict


abjad_score_to_abjad_score_block = clock_converters.AbjadScoreToAbjadScoreBlock()
instrument_note_like_to_pitched_note_like = (
    project_converters.InstrumentNoteLikeToPitchedNoteLike(
        project.constants.CLOCK_INSTRUMENT_TO_PITCH_DICT
    )
)


def notation(clock_tuple, notate_item):
    # set to true if you only want score creation but not expensive notation render
    omit_notation = False

    with concurrent.futures.ThreadPoolExecutor() as executor:
        path_list = []
        for name, tag_to_abjad_staff_group_converter, tag_tuple in (
            (
                "v",
                v_converter(),
                (
                    project.constants.ORCHESTRATION.PCLOCK.name,
                    project.constants.ORCHESTRATION.V.name,
                ),
            ),
            (
                "harp",
                harp_converter(),
                (
                    project.constants.ORCHESTRATION.PCLOCK.name,
                    project.constants.ORCHESTRATION.HARP.name,
                ),
            ),
            (
                "glockenspiel",
                glockenspiel_converter(),
                (
                    project.constants.ORCHESTRATION.PCLOCK.name,
                    project.constants.ORCHESTRATION.GLOCKENSPIEL.name,
                ),
            ),
            (
                "score",
                score_converter(),
                (
                    project.constants.ORCHESTRATION.PCLOCK.name,
                    project.constants.ORCHESTRATION.GLOCKENSPIEL.name,
                    project.constants.ORCHESTRATION.V.name,
                    project.constants.ORCHESTRATION.HARP.name,
                ),
            ),
        ):
            if notate_item not in ("all", name):
                continue
            if p := _notation(
                name,
                tag_to_abjad_staff_group_converter,
                tag_tuple,
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
            clock, tag_tuple=tag_tuple, ordered_tag_tuple=tag_tuple
        )

        # We get lilypond error for harp:
        #   Interpreting music...[8][16][24]ERROR: Wrong type (expecting exact integer): ()
        consist_timing_translator = True
        # We get lilypond error for v:
        #   Drawing systems...lilypond: skyline.cc:100: Building::Building(Real, Real, Real, Real): Assertion `start_height == end_height' failed.
        if name == "v":
            consist_timing_translator = False

        abjad_score_block = abjad_score_to_abjad_score_block.convert(
            abjad_score,
            consist_timing_translator=consist_timing_translator,
            # Setting a lower 'moment' decreases the likelihood that we catch
            # the following lilypond error:
            #   Drawing systems...lilypond: skyline.cc:100: Building::Building(Real, Real, Real, Real): Assertion `start_height == end_height' failed.
            moment=4,  # 1/16 is one second
            strict_grace_spanning=False,
            staff_staff_spacing_minimum_distance=7,
            staff_staff_spacing_basic_distance=8,
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
        bottom_margin=0.2,
        line_width=29,
        left_margin=0.5,
        page_top_space=0,
        between_title_space=0,
        after_title_space=0,
        before_title_space=0,
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


def _make_thick_duration_line(leaf, thickness=5):
    abjad.attach(
        abjad.LilyPondLiteral(rf"\override DurationLine.thickness = {thickness}"), leaf
    )
