import typing

from mutwo import breath_parameters
from mutwo import core_converters
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters


class MelodyPitchToScalePitch(core_converters.abc.Converter):
    scale = music_parameters.Scale(
        music_parameters.WesternPitch("g"),
        music_parameters.RepeatingScaleFamily(
            [
                music_parameters.WesternPitchInterval(i)
                for i in "p1 M2 M3 p4 p5 M6 m7".split(" ")
            ]
        ),
    )

    def convert(
        self, melody_pitch: music_parameters.WesternPitch
    ) -> music_parameters.ScalePitch:
        scale_index, octave = self.scale.pitch_to_scale_position(melody_pitch)
        return music_parameters.ScalePitch(scale_index, octave=octave)


mp2sp = MelodyPitchToScalePitch()


class MelodyAndBreathSequenceToVoice(core_converters.abc.Converter):
    # data_to_wait_count: With this function we can set how
    # long the rests are between two notes: are they as short as possible?
    # In this case just return 0. But for any number higher than 0 the
    # algorithm must wait X times until it finds a suitable solution again.
    def convert(
        self,
        melody: core_events.SequentialEvent,
        breath_sequence: core_events.SequentialEvent,
        data_to_wait_count=lambda is_first_note, trial_counter, missed_change_counter: 0,
    ):
        melody = melody.copy().set_parameter(
            "pitch_list", lambda pitch_list: [mp2sp(p) for p in pitch_list]
        )
        position_tuple = MelodyToPositionTuple()(melody)

        voice = core_events.TaggedSequentialEvent([], tag="v")
        b_iter = iter(breath_sequence)
        is_first_note = True
        for note, position in zip(melody, position_tuple):
            trial_counter = 0
            missed_change_counter = 0
            while 1:
                wait_count = data_to_wait_count(
                    is_first_note, trial_counter, missed_change_counter
                )
                try:
                    b = next(b_iter)
                except StopIteration:
                    return voice

                vnote = music_events.NoteLike([], duration="1/1")
                voice.append(vnote)

                if b.breath.direction == breath_parameters.BreathDirection.INHALE:
                    add_tone = position
                else:
                    add_tone = not position

                if add_tone:
                    if wait_count > missed_change_counter:
                        missed_change_counter += 1
                    else:
                        vnote.pitch_list = note.pitch_list
                        break
                trial_counter += 1

            is_first_note = False

        # If our melody is shorter than the breath duration
        while 1:
            try:
                b = next(b_iter)
            except StopIteration:
                return voice
            voice.append(music_events.NoteLike([], "1/1"))


class MelodyToPositionTuple(core_converters.abc.Converter):
    """Calculate relative pitch position (high or low) for each pitch.

    'True' means high, 'False' means low.
    Position is relative because it only depends on neighbour events
    and not on any other event.
    """

    def convert(self, melody: core_events.SequentialEvent):
        position_list = []
        for i, note in enumerate(melody):
            # Rests don't have a position
            if not note.pitch_list:
                position_list.append(None)
                continue

            previous_note = melody[i - 1] if i > 0 else None
            try:
                next_note = melody[i + 1]
            except IndexError:
                next_note = None

            p_relationship = self._t(previous_note, note)  # True: its high
            n_relationship = self._t(next_note, note)  # True: its high

            if p_relationship is not None:
                position_list.append(p_relationship)
            elif n_relationship is not None:
                position_list.append(n_relationship)
            else:
                # If no note before or after, then we
                # consider it as a raising note.
                position_list.append(True)

        return tuple(position_list)

    def _t(self, n0, n1) -> typing.Optional[bool]:
        if n0 and n1:
            return max(n0.pitch_list) < max(n1.pitch_list)
        return None
