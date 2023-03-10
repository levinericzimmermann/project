import abjad

from mutwo import abjad_converters
from mutwo import clock_converters
from mutwo import clock_generators
from mutwo import core_events
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
        sequential_event_to_abjad_staff_kwargs={
            "post_process_abjad_container_routine_sequence": (
                PostProcessClockSequentialEvent(),
            ),
        },
        duration_line=True,
        # duration_line=False,
    )
    return clock_converters.ClockEventToAbjadStaffGroup(
        complex_event_to_abjad_container
    )


def notation(clock_tuple):
    abjad_score_to_abjad_score_block = clock_converters.AbjadScoreToAbjadScoreBlock()
    instrument_note_like_to_pitched_note_like = (
        project_converters.InstrumentNoteLikeToPitchedNoteLike(
            project.constants.CLOCK_INSTRUMENT_TO_PITCH_DICT
        )
    )
    for instrument in []:
        converter_name = f"{instrument.name}_converter"
        try:
            tag_to_abjad_staff_group_converter = globals()[converter_name]
        except KeyError:
            continue
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
                    clock_line._clock_event = instrument_note_like_to_pitched_note_like(
                        clock_line.clock_event
                    )
            abjad_score = clock_to_abjad_score.convert(
                clock,
                tag_tuple=(
                    project.constants.ORCHESTRATION.HARP.name,
                    project.constants.ORCHESTRATION.VIOLIN.name,
                ),
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
        ).convert(abjad_score_block_list)

        abjad.persist.as_pdf(
            lilypond_file, f"builds/{project.constants.TITLE}_{instrument.name}.pdf"
        )
