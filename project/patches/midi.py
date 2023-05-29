import mido

from mutwo import midi_converters

# This fixes bad parameters:
# so if an extraction_function seems to works
# (doesn't return an attribute error), but its output
# is bad (so here we assume bad == None), then the converter
# breaks. it would be better to raise a warning and continue.
if 1:

    def EventToMidiFile__simple_event_to_midi_message_tuple(
        self,
        simple_event,
        absolute_time,
        available_midi_channel_tuple_cycle,
    ):
        extracted_data_list = []

        # try to extract the relevant data
        is_rest = False
        for extraction_function in (
            self._simple_event_to_pitch_list,
            self._simple_event_to_volume,
            self._simple_event_to_control_message_tuple,
        ):
            try:
                extracted_data = extraction_function(simple_event)
            except AttributeError:
                is_rest = True
            else:
                if extracted_data is None:
                    # TODO(Raise warning)!
                    is_rest = True
            if is_rest:
                break
            extracted_data_list.append(extracted_data)

        # if not all relevant data could be extracted, simply ignore the
        # event
        if is_rest:
            return tuple([])

        # otherwise generate midi messages from the extracted data
        midi_message_tuple = self._extracted_data_to_midi_message_tuple(
            absolute_time,
            simple_event.duration,
            available_midi_channel_tuple_cycle,
            *extracted_data_list,  # type: ignore
        )
        return midi_message_tuple

    midi_converters.EventToMidiFile._simple_event_to_midi_message_tuple = (
        EventToMidiFile__simple_event_to_midi_message_tuple
    )

# this fixes
#
#  Traceback (most recent call last):
#   File "/home/levinericzimmermann/Projects/Music/10.2/project/main.py", line 371, in <module>
#     project.render.midi(clock_tuple)
#   File "/home/levinericzimmermann/Projects/Music/10.2/project/project/render/midi.py", line 72, in midi
#     task.result()
#   File "/nix/store/zdba9frlxj2ba8ca095win3nphsiiqhb-python3-3.10.8/lib/python3.10/concurrent/futures/_base.py", line 451, in result
#     return self.__get_result()
#   File "/nix/store/zdba9frlxj2ba8ca095win3nphsiiqhb-python3-3.10.8/lib/python3.10/concurrent/futures/_base.py", line 403, in __get_result
#     raise self._exception
#   File "/nix/store/zdba9frlxj2ba8ca095win3nphsiiqhb-python3-3.10.8/lib/python3.10/concurrent/futures/thread.py", line 58, in run
#     result = self.fn(*self.args, **self.kwargs)
#   File "/nix/store/j0d2hcr4cfcd4a5677zk5ahs463q9mha-python3-3.10.8-env/lib/python3.10/site-packages/mutwo/midi_converters/frontends.py", line 949, in convert
#     midi_file = self._event_to_midi_file(event_to_convert)
#   File "/nix/store/j0d2hcr4cfcd4a5677zk5ahs463q9mha-python3-3.10.8-env/lib/python3.10/site-packages/mutwo/midi_converters/frontends.py", line 881, in _event_to_midi_file
#     self._add_simultaneous_event_to_midi_file(event_to_convert, midi_file)
#   File "/nix/store/j0d2hcr4cfcd4a5677zk5ahs463q9mha-python3-3.10.8-env/lib/python3.10/site-packages/mutwo/midi_converters/frontends.py", line 868, in _add_simultaneous_event_to_midi_file
#     midi_file.tracks.extend(midi_track_iterator)
#   File "/nix/store/j0d2hcr4cfcd4a5677zk5ahs463q9mha-python3-3.10.8-env/lib/python3.10/site-packages/mutwo/midi_converters/frontends.py", line 861, in <genexpr>
#     self._midi_message_tuple_to_midi_track(
#   File "/nix/store/j0d2hcr4cfcd4a5677zk5ahs463q9mha-python3-3.10.8-env/lib/python3.10/site-packages/mutwo/midi_converters/frontends.py", line 771, in _midi_message_tuple_to_midi_track
#     time=max((sorted_midi_message_list[-1].time, duration_in_ticks)),
# IndexError: list index out of range
#
#
#
# so basically an exception which is raised if no midi messages are created
# (because sorted_midi_message_list[-1] raises IndexError)
#
if 1:

    def _midi_message_tuple_to_midi_track(
        self,
        midi_message_tuple,
        duration,
        is_first_track: bool = False,
    ):
        """Convert unsorted midi message with absolute timing to a midi track.

        In the resulting midi track the timing of the messages is relative.
        """

        # initialise midi track
        track = mido.MidiTrack([])
        track.append(mido.MetaMessage("instrument_name", name=self._instrument_name))

        if is_first_track:
            # standard time signature 4/4
            track.append(mido.MetaMessage("time_signature", numerator=4, denominator=4))
            midi_message_tuple += self._tempo_envelope_to_midi_message_tuple(
                self._tempo_envelope
            )

        # sort midi data
        sorted_midi_message_list = sorted(
            midi_message_tuple, key=lambda message: message.time
        )

        # add end of track message
        if sorted_midi_message_list:
            duration_in_ticks = self._beats_to_ticks(duration)
            sorted_midi_message_list.append(
                mido.MetaMessage(
                    "end_of_track",
                    time=max((sorted_midi_message_list[-1].time, duration_in_ticks)),
                )
            )
            # convert from absolute to relative time
            delta_tick_per_message_tuple = tuple(
                message1.time - message0.time
                for message0, message1 in zip(
                    sorted_midi_message_list, sorted_midi_message_list[1:]
                )
            )
            delta_tick_per_message_tuple = (
                sorted_midi_message_list[0].time,
            ) + delta_tick_per_message_tuple
            for dt, message in zip(
                delta_tick_per_message_tuple, sorted_midi_message_list
            ):
                message.time = dt

        # add midi data to midi track
        track.extend(sorted_midi_message_list)

        return track

    midi_converters.EventToMidiFile._midi_message_tuple_to_midi_track = (
        _midi_message_tuple_to_midi_track
    )
