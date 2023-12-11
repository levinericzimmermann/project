from mutwo import music_events
from mutwo import music_parameters

def _string_to_pitch(pitch_indication: str) -> music_parameters.abc.Pitch:
    # assumes it is a ratio
    if "/" in pitch_indication:
        return music_parameters.JustIntonationPitch(pitch_indication)

    # assumes it is a WesternPitch name
    elif (
        pitch_indication[0] in music_parameters.constants.DIATONIC_PITCH_CLASS_CONTAINER
    ):
        if pitch_indication[-1].isdigit():
            pitch_name, octave = pitch_indication[:-1], int(pitch_indication[-1])
            pitch = music_parameters.WesternPitch(pitch_name, octave)
        else:
            pitch = music_parameters.WesternPitch(pitch_indication)

        return pitch

    else:
        index = int(pitch_indication)
        return music_parameters.ScalePitch(index - 1)



music_events.configurations._string_to_pitch = _string_to_pitch
