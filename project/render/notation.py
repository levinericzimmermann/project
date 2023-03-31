import copy
import hashlib
import shutil
import subprocess
import warnings

import abjad

from mutwo import abjad_converters
from mutwo import clock_converters
from mutwo import clock_generators
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_converters
from mutwo import project_parameters

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
                    if note_like.pitch_list:
                        note_like.notation_indicator_collection.duration_line.is_active = (
                            True
                        )
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
        ),
        duration_line=True,
    )

    return {
        "aeolian harp": EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=1,
            placement_mode="floating",
            max_denominator=100000,
        ),
    }


@run
def guitar_converter():
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
                    abjad.LilyPondLiteral(r'\accidentalStyle "forget"'),
                    first_leaf,
                )

    class EventPlacementToAbjadStaffGroup(
        clock_converters.EventPlacementToAbjadStaffGroup
    ):
        def convert(self, event_placement, *args, **kwargs):
            event = event_placement.event[guitar_tag]
            if isinstance(event, core_events.SimultaneousEvent) and event and event[0]:
                event.set_parameter("pitch_list", set_pitch_list)
                for e in event[0]:
                    if hasattr(e, "notation_indicator_collection"):
                        e.notation_indicator_collection.clef.name = "G_8"
                # No need to print repeating tones: The player is ALWAYS allowed
                # to repeat a sound.
                for sequential_event in event:
                    sequential_event.tie_by(
                        lambda e0, e1: hasattr(e0, "pitch_list")
                        and hasattr(e1, "pitch_list")
                        and e0.pitch_list == e1.pitch_list
                    )
            return super().convert(event_placement, *args, **kwargs)

    def set_pitch_list(pitch_list):
        new_pitch_list = []
        for pitch in pitch_list:
            fret_index = None
            for string_index, frets in enumerate(GUITAR.frets_tuple):
                if pitch in frets:
                    fret_index = frets.index(pitch)
                    break
            if fret_index is None:
                warnings.warn(
                    f"COULDN'T FIND PITCH {pitch.ratio} IN GUITAR!\n"
                    f"Available pitches are {GUITAR.pitch_tuple}."
                )
                continue
            new_pitch_list.append(
                project_parameters.Guitar.ORIGINAL_FRETS_TUPLE[string_index][fret_index]
            )
        return new_pitch_list

    complex_event_to_abjad_container = clock_generators.make_complex_event_to_abjad_container(
        sequential_event_to_abjad_staff_kwargs=dict(
            mutwo_pitch_to_abjad_pitch=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
            mutwo_volume_to_abjad_attachment_dynamic=None,
            write_multimeasure_rests=False,
            post_process_abjad_container_routine_sequence=(
                PostProcessClockSequentialEvent(),
            ),
        ),
    )

    guitar_tag = "guitar"

    return {
        guitar_tag: EventPlacementToAbjadStaffGroup(
            complex_event_to_abjad_container,
            staff_count=1,
            placement_mode="floating",
            max_denominator=100000,
        ),
    }


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

GUITAR = None


def notation(clock_tuple, d, scale, orchestration, path, executor):
    global GUITAR
    try:
        GUITAR = orchestration.GUITAR
    # This means we have an empty clock due to an
    # exception
    except AttributeError:
        return executor.submit(shutil.copyfile, 'etc/blank.pdf', path)

    global SCALE
    SCALE = scale

    abjad_score_to_abjad_score_block = clock_converters.AbjadScoreToAbjadScoreBlock()
    instrument_note_like_to_pitched_note_like = (
        project_converters.InstrumentNoteLikeToPitchedNoteLike(
            project.constants.CLOCK_INSTRUMENT_TO_PITCH_DICT
        )
    )
    tag_to_abjad_staff_group_converter = guitar_converter
    tag_to_abjad_staff_group_converter.update(aeolian_harp_converter)

    clock_to_abjad_score = clock_converters.ClockToAbjadScore(
        tag_to_abjad_staff_group_converter,
        clock_event_to_abjad_staff_group=clock_event_to_abjad_staff_group,
    )

    abjad_score_block_list = []
    for clock in clock_tuple:
        # XXX: Copy clock, to ensure the fix below with unwritable clock line
        # isn't propagated to sound generation!
        clock = copy.deepcopy(clock)
        for clock_line in (
            clock.main_clock_line,
            clock.start_clock_line,
            clock.end_clock_line,
        ):
            if clock_line:
                # Remove first + last event placement of guitar
                clock_line.sort()
                prohibited_event_placement_index_list = []
                for i, ep in enumerate(clock_line._event_placement_list):
                    try:
                        ep.event["guitar"]
                    except KeyError:
                        continue
                    prohibited_event_placement_index_list.append(i)
                    break
                for i, ep in enumerate(reversed(clock_line._event_placement_list)):
                    try:
                        ep.event["guitar"]
                    except KeyError:
                        continue
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

            # If we have an empty clock line, it's duration is the value in seconds.
            # In this case abjad won't be able to quantize it, most likely.
            # So we simplify this.
            if clock_line and clock_line.clock_event:
                if clock_line.clock_event.duration.duration.denominator > 64:
                    # XXX: old_duration = clock_line.clock_event.duration
                    # XXX: We could override the tempo now, to ensure the duration is correct.
                    # But this isn't necessary here, because we don't need to render it to sound,
                    clock_line.clock_event.duration = 1

        abjad_score = clock_to_abjad_score.convert(
            clock,
            tag_tuple=("guitar", "aeolian harp"),
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
            staff_size=20,
        )
        abjad_score_block_list.append(abjad_score_block)

    lilypond_file = clock_converters.AbjadScoreBlockTupleToLilyPondFile(
        system_system_padding=1,
        system_system_basic_distance=1,
        score_system_padding=1,
        score_system_basic_distance=1,
        markup_system_padding=1,
        markup_system_basic_distance=1,
        staff_height=12,
        top_margin=1.5,
        bottom_margin=0.1,
        left_margin=2.5,
        foot_separation=0.1,
        head_separation=0.1,
        line_width=25,
        before_title_space=0.01,
        after_title_space=0.01,
        page_top_space=0.01,
        between_title_space=0.01,
        print_page_number=False,
        page_breaking=r"#ly:minimal-breaking",
    ).convert(
        abjad_score_block_list,
    )

    lilypond_file.items.insert(0, r'\include "etc/lilypond/ekme-heji.ily"')

    return executor.submit(render_and_rotate, lilypond_file, path)

def render_and_rotate(lilypond_file, path):
    temp_path = hashlib.md5(path.encode()).hexdigest()
    temp_path = f".{temp_path}.pdf"
    abjad.persist.as_pdf(lilypond_file, temp_path)
    subprocess.call(["pdftk", temp_path, "cat", "1right", "output", path])


def merge_notation(suffix: str, path_list: list[str]):
    path = f"builds/{project.constants.TITLE}_{suffix}.pdf"
    print(f"Merge '{path_list}' to '{path}'")
    command = ["pdftk"] + path_list + ["output", path]
    subprocess.call(command)
