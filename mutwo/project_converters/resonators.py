from mutwo import core_converters
from mutwo import core_events
from mutwo import music_events
from mutwo import project_events
from mutwo import project_interfaces


class ResonatorTupleAndEventToResonances(core_converters.abc.Converter):
    def convert(
        self,
        resonator_tuple: project_interfaces.ResonatorTuple,
        event: core_events.SimultaneousEvent[
            core_events.TaggedSequentialEvent[project_events.BreathEvent],
            core_events.TaggedSequentialEvent[music_events.NoteLike],
        ],
    ) -> core_events.TaggedSimultaneousEvent[core_events.SequentialEvent]:
        n, seq = music_events.NoteLike, core_events.SequentialEvent
        dur = event.duration
        r = core_events.TaggedSimultaneousEvent(
            [seq([n([], dur)]) for _ in resonator_tuple], tag="r"
        )
        for s, resonator in zip(r, resonator_tuple):
            for t, w in zip(event[1].absolute_time_tuple, event[1]):
                if w.pitch_list:
                    proceed_note_like(t, w, resonator, s, event[0])
        # Don't allow resonators that overlap to the next entry, to
        # make everything simpler. Otherwise the rhythm duration of these
        # resonators may not be correct, because it depend on the breath
        # speed of the next entry, and if this isn't known yet it can't
        # be calculated, but only guessed.
        assert r.duration == dur, "overlapping resonances are prohibited"
        return r


def proceed_note_like(t, n, resonator, seq, b):
    resonating_pitch_list = [
        p for p in n.pitch_list if p in resonator.resonating_pitch_tuple
    ]
    if not resonating_pitch_list:
        return

    resonance_pitch_list = []
    for p in resonating_pitch_list:
        for transp in resonator.pitch_transposition_tuple:
            resonance_pitch_list.append(p + transp)

    n = music_events.NoteLike(p, n.duration, n.volume)

    # Applying delay of resonator is a bit difficult, because
    # the resonators delay is in the unit of seconds, while
    # the duration of the events is in breath-parts. So we need
    # to convert this according to the current breath style (fast
    # or slow or whatever).
    if delay := resonator.delay:
        if t > 0:
            _, b = b.split_at(t)
        while delay > 0:
            b0 = b[0]
            d = b0.breath_or_hold_breath.duration * b0.duration
            if delay >= d:
                delay -= d
                t += b0.duration
            else:
                percentage = delay / d
                delay = 0
                t += b0.duration * percentage

    seq.squash_in(t, n)


# Serialize resonator tuple information into a dict, so
# that it can be written to disk as a json file.
class ResonatorTupleToSerializable(core_converters.abc.Converter):
    def convert(self, resonator_tuple: project_interfaces.ResonatorTuple) -> dict:
        d = {}
        for i, r in enumerate(resonator_tuple):
            d[i] = {
                "delay": float(r.delay),
                "pitch_transposition_list": [
                    i.interval / 1200 for i in r.pitch_transposition_tuple
                ],
                "resonance_filter_list": [
                    {
                        "frequency": f.frequency,
                        "amplitude": f.amplitude,
                        "decay": f.decay,
                    }
                    for f in r.resonance_filter_tuple
                ],
            }
        return d
