import collections
import enum
import functools
import itertools
import time
import typing

import pyo
import serial
import walkman


__all__ = ("String", "AeolianHarp", "Compressor")

BAUDRATE = 230400
READ_TIMEOUT = 0.1
MAX_FREQUENCY = 450

walkman.constants.LOGGER.handlers = walkman.constants.LOGGER.handlers[1:]


class Envelope(enum.IntEnum):
    SILENCE = 0
    BASIC = 1
    BASIC_QUIET = 2
    BASIC_LOUD = 3
    PLUCK_0 = 4
    PLUCK_1 = 5


class ReadingSerial(serial.Serial):
    """Adjusted Serial which prints received data (aka "Serial Monitor") to walkman log"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pyo_metro = pyo.Metro(1).play()
        self._pyo_reader = pyo.TrigFunc(self._pyo_metro, self._read).play()
        self.is_closed = False

    def _read(self):
        if not self.is_closed:
            if self.in_waiting:
                serial_reply = self.read(self.in_waiting).decode("Ascii")
                for line in serial_reply.splitlines():
                    walkman.constants.LOGGER.debug(f"{self.name} => C: {line}")

    def close(self, *args, **kwargs):
        if not self.is_closed:
            walkman.constants.LOGGER.info(f"Shut down board '{self}'.")
            self._pyo_metro.stop()
            self._pyo_reader.stop()
            time.sleep(READ_TIMEOUT + 0.01)
            self.is_closed = True
            return super().close()


class Protocol(object):
    """Communication between arduino and computer"""

    item_delimiter: str = " "
    msg_start_delimiter: str = "#"
    msg_end_delimiter: str = "\n"
    Data: typing.TypeAlias = tuple[int, int, int]
    frequency_factor: int = 10**6  # mikro (seconds)
    mode_frequency: int = 0
    mode_envelope: int = 1

    def __init__(self, board: ReadingSerial, pin_index: int):
        self.board = board
        self.pin_index = pin_index

    def send(self, data: Data):
        msg = "{}{}{}".format(
            self.msg_start_delimiter,
            self.item_delimiter.join(map(str, data)),
            self.msg_end_delimiter,
        )
        try:
            walkman.constants.LOGGER.debug(f"C => {self.board.name}: {msg}")
            self.board.write(msg.encode("utf-8"))
        except AttributeError:
            walkman.constants.LOGGER.warning(f"Can't write to board: {self.board}")

    def set_frequency(self, frequency: float):
        period = int((1 / frequency) * self.frequency_factor)
        self.send((self.pin_index, self.mode_frequency, period))

    def set_envelope(self, envelope: Envelope):
        self.send((self.pin_index, self.mode_envelope, envelope.value))

    def stop(self):
        self.set_envelope(Envelope.SILENCE)


class String(walkman.Module):
    ComPort: typing.TypeAlias = str
    ArduinoInstanceId: typing.TypeAlias = int
    com_port_to_board: dict[ComPort, ReadingSerial] = {}

    def __init__(
        self,
        com_port: ComPort,
        pin_index: int,
        **kwargs,
    ):
        super().__init__(**kwargs)

        try:
            board = self.com_port_to_board[com_port]
        except KeyError:
            try:
                board = self.com_port_to_board[com_port] = ReadingSerial(
                    com_port, timeout=READ_TIMEOUT, baudrate=BAUDRATE
                )
            except serial.serialutil.SerialException as e:
                walkman.constants.LOGGER.warning(f"Unusable board: {e}")
                board = None

        self.protocol = Protocol(board, pin_index)
        self.board = board
        self.pin_index = pin_index
        walkman.constants.LOGGER.info(
            f"Finished setup for String with com_port = {com_port} and pin_index = {pin_index}."
        )

    def _initialise(
        self, frequency: float = 200, envelope: str = "BASIC", *args, **kwargs
    ):
        super()._initialise(*args, **kwargs)
        if frequency > MAX_FREQUENCY:
            walkman.constants.LOGGER.warning(
                f"Catched too high frequency {frequency}. Set to {MAX_FREQUENCY}."
            )
            frequency = MAX_FREQUENCY
        self.frequency = frequency
        # For cue switch during playing
        if self.is_playing:
            self.protocol.set_frequency(self.frequency)
        self.envelope = getattr(Envelope, envelope, "BASIC")

    def _play(self, *args, **kwargs):
        super()._play(*args, **kwargs)
        self.protocol.set_envelope(self.envelope)
        if self.envelope is not Envelope.SILENCE:
            self.protocol.set_frequency(self.frequency)

    def _stop(self, wait: float = 0):
        super()._stop(wait)
        self.protocol.stop()
        super()._stop(wait=wait)

    def close(self):
        # Use _stop instead of stop: this is a safety belt to
        # really stop all strings from ringing.
        self._stop()
        super().close()


class AeolianHarp(walkman.Hub):
    E = collections.namedtuple("Event", ("duration", "kwargs", "is_rest"))

    def _setup_pyo_object(self, *args, **kwargs):
        super()._setup_pyo_object(*args, **kwargs)
        self.sequencer0 = walkman.Sequencer(
            self.audio_input_1,
        )
        self.sequencer1 = walkman.Sequencer(
            self.audio_input_2,
        )
        self.sequencer2 = walkman.Sequencer(
            self.audio_input_3,
        )
        self._reset_events()

    def _reset_events(self):
        self.sequencer0.event_iterator = itertools.cycle(
            [
                self.E(10, dict(envelope="BASIC", frequency=120), False),
                self.E(20, {}, True),
            ]
        )
        self.sequencer1.event_iterator = itertools.cycle(
            [
                self.E(10, {}, True),
                self.E(10, dict(envelope="BASIC", frequency=120), False),
                self.E(10, {}, True),
            ]
        )
        self.sequencer2.event_iterator = itertools.cycle(
            [
                self.E(20, {}, True),
                self.E(10, dict(envelope="BASIC", frequency=120), False),
            ]
        )

    def _play(self, duration: float, delay: float):
        super()._play(duration, delay)
        self.sequencer0.play(duration, delay)
        self.sequencer1.play(duration, delay)
        self.sequencer2.play(duration, delay)

    def _stop(self, wait: float = 0):
        super()._stop(wait)
        self._is_playing = False
        self.sequencer0.stop(wait)
        self.sequencer1.stop(wait)
        self.sequencer2.stop(wait)
        # The current basic sequencer implementation of walkman isn't
        # very clever and doesn't start the same event at the point where
        # it stopped, but it simply jumps to the next event.
        #
        # This means that whenever any stop is triggered all sequencers
        # won't be in sync anymore. So we simply re-initialize all sequencers
        # before playing again.
        self._reset_events()


class Compressor(
    walkman.ModuleWithDecibel,
    audio_input=walkman.Catch(walkman.constants.EMPTY_MODULE_INSTANCE_NAME),
    ratio=walkman.AutoSetup(walkman.Value, module_kwargs={"value": 3}),
    risetime=walkman.AutoSetup(walkman.Value, module_kwargs={"value": 0.01}),
    falltime=walkman.AutoSetup(walkman.Value, module_kwargs={"value": 0.1}),
):
    def _setup_pyo_object(self):
        super()._setup_pyo_object()
        self.compressor = pyo.Compress(
            self.audio_input.pyo_object,
            mul=self.amplitude_signal_to,
            ratio=self.ratio.pyo_object_or_float,
            risetime=self.risetime.pyo_object_or_float,
            falltime=self.falltime.pyo_object_or_float,
        ).stop()
        self.internal_pyo_object_list.append(self.compressor)

    @functools.cached_property
    def _pyo_object(self) -> pyo.PyoObject:
        return self.compressor
