import concurrent.futures
import datetime
import enum
import functools
import itertools
import time
import typing

from astral import LocationInfo
import numpy as np
from apscheduler.schedulers.background import BackgroundScheduler
import time_machine
import librosa

from mutwo import core_utilities

import pyo
import serial
import walkman
import walkmanio

__all__ = ("String", "AeolianHarp", "Compressor", "Gate", "SpectralFilterInput")

BAUDRATE = 230400
READ_TIMEOUT = 0.1
MAX_FREQUENCY = 450

walkman.constants.LOGGER.handlers = walkman.constants.LOGGER.handlers[1:]

# Duplicated in main.py
LOCATION_INFO = LocationInfo(
    name="Essen",
    region="NRW",
    timezone="Europe/Berlin",
    latitude=51.4556432,
    longitude=7.0115552,
)


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
    TOTAL_STRING_COUNT = 9
    BOX_COUNT = 3

    def _setup_pyo_object(self, *args, **kwargs):
        super()._setup_pyo_object(*args, **kwargs)
        sequencer_list = []
        for string_index in range(self.TOTAL_STRING_COUNT + self.BOX_COUNT):
            sequencer = walkman.Sequencer(
                getattr(self, f"audio_input_{string_index}"),
            )
            sequencer_list.append(sequencer)
        self.sequencer_tuple = tuple(sequencer_list)

    def _initialise(
        self,
        play_mode: str = "test",
        jumptime: typing.Optional[str] = None,
        *args,
        **kwargs,
    ):
        super()._initialise(*args, **kwargs)
        self.play_mode = play_mode
        # Allow time travel for testing purposes
        self.traveller = None
        self.jumptime = jumptime
        # We need to ensure all relevant start up code is executed.
        # Usually this shouldn't be a be problem, because this patch isn't
        # meant to be used with jumping between cues, we only need to start
        # one cue and that's it. But still just to be double sure it's added
        # here.
        if self.is_playing:
            self.stop()
            self.play()

    def _reset_events(self):
        play_mode = getattr(self, "play_mode", "test")
        getattr(self, f"_{play_mode}")()

    def _play(self, duration: float, delay: float):
        if self.jumptime:
            # First parse our string to year/month/day/hour/minute/second format...
            jumptime = datetime.datetime.fromisoformat(self.jumptime)
            # ...and then construct the real datetime object by combining the previously
            # parsed information and our timezone information. We can't parse the timezone
            # information directly to the isoformat, because its isoformat is ambigous (due
            # to a different isoformat depending on summer/winter time).
            jumptime = datetime.datetime(
                jumptime.year,
                jumptime.month,
                jumptime.day,
                jumptime.hour,
                jumptime.minute,
                jumptime.second,
                tzinfo=LOCATION_INFO.tzinfo,
            )
            walkman.constants.LOGGER.info(f"Start time travel to {jumptime}.")
            self.traveller = time_machine.travel(jumptime)
            self.traveller.start()
        # The current basic sequencer implementation of walkman isn't
        # very clever and doesn't start the same event at the point where
        # it stopped, but it simply jumps to the next event.
        #
        # This means that whenever any stop is triggered all sequencers
        # won't be in sync anymore. So we simply re-initialize all sequencers
        # before playing again.
        self._reset_events()
        super()._play(duration, delay)

    def _stop(self, wait: float = 0):
        self._shutdown_scheduler()

        if self.traveller:
            walkman.constants.LOGGER.info(f"End time travel, return to present.")
            self.traveller.stop()

        super()._stop(wait)
        for sequencer in self.sequencer_tuple:
            sequencer.event_iterator = iter([])
            sequencer.stop(wait)

        self._is_playing = False

    def _shutdown_scheduler(self):
        walkman.constants.LOGGER.info("Shutdown/cleanup scheduler")
        try:
            [j.remove() for j in self.scheduler.get_jobs()]
            self.scheduler.shutdown()
            del self.scheduler
        except AttributeError:
            pass

    def _music(self):
        # First cleanup all sequencers
        for sequencer in self.sequencer_tuple:
            sequencer.event_iterator = iter([])

        # Now we can schedule new events
        self.scheduler = BackgroundScheduler()
        astral_part_tuple = walkmanio.import_astral_part_tuple("etc/walkmansequences")
        now = datetime.datetime.now(LOCATION_INFO.tzinfo)
        walkman.constants.LOGGER.info(f"Now it's {now}.")
        for d, sequence_tuple in astral_part_tuple:
            walkman.constants.LOGGER.warning(f"Activate astral part on {d}:")
            if d < now:  # Ignore past event
                walkman.constants.LOGGER.info(
                    f"\tPart is ignored (this is in the past)."
                )
                continue
            for s_index, sequence in enumerate(sequence_tuple):
                try:
                    sequencer = self.sequencer_tuple[s_index]
                except IndexError:
                    walkman.constants.LOGGER.warning(
                        f"No sequencer with index {s_index} available."
                    )
                    continue
                f = self._makef(s_index, sequencer, sequence)
                walkman.constants.LOGGER.info(
                    f"\t\tAdded job to sequencer {s_index} on {d}."
                )
                self.scheduler.add_job(
                    f, trigger="date", run_date=d, timezone=LOCATION_INFO.tzinfo
                )

        walkman.constants.LOGGER.info("Start scheduler")
        self.scheduler.start()

    def _makef(self, index, sequencer, sequence):
        def f():
            walkman.constants.LOGGER.info(
                f"Try to execute schedule event on seq ({index}) {sequencer.module}..."
            )
            if self.is_playing:
                sequencer.stop()
                sequencer.event_iterator = iter(sequence)
                sequencer.play()
                walkman.constants.LOGGER.info(
                    f"Successfully started sequencer {index}."
                )
            else:
                walkman.constants.LOGGER.info(
                    "Didn't start scheduled event, because module isn't playing."
                )

        return f

    def _test(self):
        e, f, d = "BASIC", 120, 10
        max_d = d * (self.TOTAL_STRING_COUNT - 1)
        for string_index in range(self.TOTAL_STRING_COUNT):
            event_list = [
                walkmanio.WalkmanEvent(d, dict(envelope=e, frequency=f), False),
            ]
            r0_duration = string_index * d
            for rest_index, rest_duration in enumerate(
                [r0_duration, max_d - (r0_duration)]
            ):
                if rest_duration:
                    r = walkmanio.WalkmanEvent(rest_duration, {}, True)
                    if rest_index:
                        event_list.append(r)
                    else:
                        event_list.insert(0, r)
            self.sequencer_tuple[string_index].event_iterator = itertools.cycle(
                event_list
            )


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


class Gate(
    walkman.ModuleWithDecibel,
    audio_input=walkman.Catch(walkman.constants.EMPTY_MODULE_INSTANCE_NAME),
    thresh=walkman.AutoSetup(walkman.Value, module_kwargs={"value": -50}),
    risetime=walkman.AutoSetup(walkman.Value, module_kwargs={"value": 3}),
    falltime=walkman.AutoSetup(walkman.Value, module_kwargs={"value": 1}),
):
    def _setup_pyo_object(self):
        super()._setup_pyo_object()
        self.gate = pyo.Gate(
            self.audio_input.pyo_object,
            mul=self.amplitude_signal_to,
            thresh=self.thresh.pyo_object_or_float,
            risetime=self.risetime.pyo_object_or_float,
            falltime=self.falltime.pyo_object_or_float,
            lookahead=20,
        ).stop()
        self.internal_pyo_object_list.append(self.gate)

    @functools.cached_property
    def _pyo_object(self) -> pyo.PyoObject:
        return self.gate


class SpectralFilterInput(walkman.AudioInput):
    def __init__(
        self,
        *args,
        noise_file_path: str = "noise.wav",
        size: int = 1024,
        overlaps: int = 3,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.noise_file_path = noise_file_path
        self.size = size
        self.overlaps = overlaps
        self.thread_pool_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def _setup_pyo_object(self):
        super()._setup_pyo_object()

        y_noise, sampling_rate_noise = librosa.load(self.noise_file_path)
        noise_magnitude_list = np.abs(librosa.stft(y_noise, n_fft=self.size))
        self.noise_magnitude_list = [
            float(v) for v in np.mean(noise_magnitude_list, axis=1)
        ]

        self.noise_table = pyo.DataTable(int(self.size / 2))

        self.analysis = pyo.PVAnal(
            self.denorm,
            size=self.size,
            overlaps=self.overlaps,
            callback=self.set_noise_table,
        )
        self.filter = pyo.PVFilter(self.analysis, self.noise_table)
        self.synthesis = pyo.PVSynth(self.filter)
        self.internal_pyo_object_list.extend(
            [self.analysis, self.filter, self.synthesis]
        )

    @functools.cached_property
    def _pyo_object(self) -> pyo.PyoObject:
        return self.synthesis

    def set_noise_table(self, signal_magnitude_list, _):
        # We don't run this in our main thread, because it seems to block
        # pyo / our main thread. If we run this calculation in a separate
        # thread we reduce likelihood for xruns.
        self.thread_pool_executor.submit(
            self.set_signal_noise_ratio_list, signal_magnitude_list
        )

    def set_signal_noise_ratio_list(self, signal_magnitude_list):
        self.noise_table.replace(
            self._signal_noise_ratio_list(
                signal_magnitude_list, self.noise_magnitude_list
            )
        )

    @staticmethod
    def _signal_noise_ratio_list(signal_magnitude_list, noise_magnitude_list):
        # We calculate now the signal-noise ratio.
        # We know how noisy each bin is by comparing its value with the
        # value of a very noisy bin.
        # If the DELTA between noise and signal is 0 this means the noise
        # must be 100% present in our signal (we get 0). If it is 100%
        # present we need to cancel this bin with our filter. Therefore we
        # reverse 100% presence (= min or 0) to max value 1 via 'scale'.
        signal_noise_ratio_list = []
        for magnitude_signal, magnitude_noise in zip(
            signal_magnitude_list, noise_magnitude_list
        ):
            delta = magnitude_noise - magnitude_signal
            signal_noise_ratio = core_utilities.scale(
                delta, min((0, delta)), magnitude_noise, 1, 0
            )
            signal_noise_ratio_list.append(signal_noise_ratio)
        return signal_noise_ratio_list

    def close(self, *args, **kwargs):
        super().close(*args, **kwargs)
        self.thread_pool_executor.shutdown()
