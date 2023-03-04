import time
import typing

import pyo
import serial
import walkman


__all__ = ("String", "AeolianHarp")

BAUDRATE = 9600
READ_TIMEOUT = 0.1


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
                    walkman.constants.LOGGER.info(f"{self.name} => C: {line}")

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
    msg_delimiter: str = "\n"
    Data: typing.TypeAlias = tuple[int, int, int]
    frequency_factor: int = 10**6  # mikro (seconds)
    mode_frequency: int = 0
    mode_envelope: int = 1

    def __init__(self, board: ReadingSerial, pin_index: int):
        self.board = board
        self.pin_index = pin_index

    def send(self, data: Data):
        msg = "{}{}".format(
            self.item_delimiter.join(map(str, data)), self.msg_delimiter
        )
        walkman.constants.LOGGER.info(f"C => {self.board.name}: {msg}")
        self.board.write(msg.encode("utf-8"))

    def set_frequency(self, frequency: float):
        period = int((1 / frequency) * self.frequency_factor)
        self.send((self.pin_index, self.mode_frequency, period))

    def set_envelope(self, envelope_index: int):
        self.send((self.pin_index, self.mode_envelope, envelope_index))

    def stop(self):
        self.set_envelope(0)


class String(
    walkman.ModuleWithFader,
    frequency=walkman.AutoSetup(walkman.Value, module_kwargs={"value": 75}),
):
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

        self.last_frequency = 0

        try:
            board = self.com_port_to_board[com_port]
        except KeyError:
            board = self.com_port_to_board[com_port] = ReadingSerial(
                com_port, timeout=READ_TIMEOUT, baudrate=BAUDRATE
            )

        self.protocol = Protocol(board, pin_index)
        self.board = board
        self.pin_index = pin_index
        walkman.constants.LOGGER.info(
            f"Finished setup for String with com_port = {com_port} and pin_index = {pin_index}."
        )

    def _setup_pyo_object(self):
        super()._setup_pyo_object()
        self.frequency_changer_metro = pyo.Metro(2)
        self.frequency_changer = pyo.TrigFunc(
            self.frequency_changer_metro, self._set_frequency
        )
        self.internal_pyo_object_list.extend(
            [self.frequency_changer, self.frequency_changer_metro]
        )
        walkman.constants.LOGGER.info(
            f"Frequency obj: {self.frequency}, {self.frequency.replication_key}."
        )

    def _set_frequency(self):
        if (frequency := self.frequency.pyo_object.get()) != self.last_frequency:
            self.protocol.set_frequency(frequency)
            self.last_frequency = frequency

    def _play(self, *args, **kwargs):
        super()._play(*args, **kwargs)
        self.protocol.set_envelope(1)
        # self.protocol.set_envelope(3)  # basic II 
        # self.protocol.set_envelope(4)  # plucking

    def _stop_without_fader(self, wait: float = 0):
        super()._stop_without_fader(wait=wait)
        self.protocol.stop()

    def close(self):
        super().close()
        self.board.close()


class AeolianHarp(walkman.Hub):
    pass
