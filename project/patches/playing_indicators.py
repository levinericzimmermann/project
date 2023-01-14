import dataclasses
import enum

from mutwo import music_parameters

music_parameters_Tremolo = music_parameters.Tremolo


@dataclasses.dataclass()
class Tremolo(music_parameters_Tremolo):
    class D(enum.Enum):
        Stable = ""
        Acc = "tr. acc."
        Rit = "tr. rit."
        AccRit = "tr. acc. <> rit."
        RitAcc = "tr. rit. <> acc."

    # Can be
    #   - None
    #   - 'tremolo acc.'
    #   - 'tremolo rit.'
    #   - 'tremolo acc. + rit.'
    #   - 'tremolo rit. + acc.'
    dynamic: D = D.Stable


music_parameters.Tremolo = Tremolo
