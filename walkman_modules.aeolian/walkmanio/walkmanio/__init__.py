import collections
import datetime
import os
import pickle
import typing


class WalkmanEvent(
    collections.namedtuple("WalkmanEvent", ("duration", "kwargs", "is_rest"))
):
    pass


WalkmanEventTuple: typing.TypeAlias = tuple[WalkmanEvent, ...]
SequenceTuple: typing.TypeAlias = tuple[
    # Exactly 12 event sequences: each string has a sequencer and
    # each box/audio-input has a sequencer.
    # We have 9 strings on 3 boxes.
    WalkmanEventTuple,
    WalkmanEventTuple,
    WalkmanEventTuple,
    WalkmanEventTuple,
    WalkmanEventTuple,
    WalkmanEventTuple,
    WalkmanEventTuple,
    WalkmanEventTuple,
    WalkmanEventTuple,
    WalkmanEventTuple,
    WalkmanEventTuple,
    WalkmanEventTuple,
]
AstralPart: typing.TypeAlias = tuple[datetime.datetime, SequenceTuple]
AstralPartTuple = typing.TypeAlias = tuple[AstralPart, ...]


def export(path: str, d: datetime.datetime, sequence_tuple: SequenceTuple):
    path = f"{path}/{d.year}-{d.month}-{d.day}-{d.hour}-{d.minute}.pickled"
    astral_part = (d, sequence_tuple)
    with open(path, "wb") as f:
        f.write(pickle.dumps(astral_part))


def import_astral_part_tuple(path: str) -> AstralPartTuple:
    astral_part_list = []
    for fname in os.listdir(path):
        with open(f"{path}/{fname}", "rb") as f:
            try:
                astral_part = pickle.load(f)
            except Exception:
                continue
            astral_part_list.append(astral_part)
    return tuple(astral_part_list)
