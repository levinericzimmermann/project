import itertools
import random
import typing

import numpy as np
from telemetrix import telemetrix
import pyo
import walkman


__all__ = ("String",)


class String(
    walkman.ModuleWithFader,
    frequency=walkman.AutoSetup(walkman.Value, module_kwargs={"value": 75}),
):
    ComPort: typing.TypeAlias = str
    ArduinoInstanceId: typing.TypeAlias = int
    board_id_to_board: dict[
        tuple[ComPort, ArduinoInstanceId], telemetrix.Telemetrix
    ] = {}

    def __init__(
        self,
        com_port: ComPort,
        arduino_instance_id: ArduinoInstanceId,
        pin: int,
        **kwargs,
    ):
        super().__init__(**kwargs)
        board_id = (com_port, arduino_instance_id)
        try:
            self.board = self.board_id_to_board[board_id]
        except KeyError:
            self.board = self.board_id_to_board[board_id] = telemetrix.Telemetrix(
                com_port, arduino_instance_id=arduino_instance_id
            )
        self.pin = pin

        self.board.set_pin_mode_analog_output(self.pin)

        self._control_point_cycle = iter([0])
        self.envelope_tuple = (
            # (0, 150, 200, 255, 200, 150, 0),
            # (0, 50, 100, 155, 100, 50, 0),
            # (100, 125, 150, 180, 150, 125, 100),
            # (220, 230, 240, 255, 240, 230, 220),
            # (240, 245, 250, 255, 250, 245, 240),
            #
            # sehr laut, und direkt, vielleicht sogar lauter
            # als das erste
            # (0, 255, 255, 255, 255, 255, 0),
            # Only plucking, no static pitch
            (255, 254, 253),
            # rather static pitch
            # (99, 99, 99, 100, 100, 100, 100, 101, 101, 102, 102, 102, 102, 103, 103, 103, 103, 102, 101, 100, 99, 98, 99),
        )
        self.envelope_repetition_count_range = (5, 20)
        self.envelope_cycle = itertools.cycle(self.envelope_tuple)
        walkman.constants.LOGGER.info(
            f"Finished setup for String with com_port = {com_port} and pin = {pin}."
        )

    def _setup_pyo_object(self):
        super()._setup_pyo_object()
        self.control_value_count = pyo.Sig(1)
        self.period_duration = 1 / self.frequency.pyo_object_or_float
        self.sleep_time = self.period_duration / self.control_value_count
        self.mod = pyo.LFO(6, add=1, mul=0.25) + 0.75
        self.metro = pyo.Metro(self.sleep_time * self.mod)
        self.trig_func = pyo.TrigFunc(self.metro, self._set_magnetic_field)

        # We want to be very sure that once the sound ends the magnet is turned
        # off (control value = 0). Because the frequency of the magnetic field
        # doesn't necessarily fall onto the fadeout time, the last send control
        # value is very likely not 0. So we add an extra trigger which waits
        # until the whole fadeout process is finished and then finally sends a
        # 0 to the magnet.

        def deactivate_magnet():
            walkman.constants.LOGGER.debug(f"Deactivate magnet on pin = {self.pin}.")
            self._set_magnetic_field(0)

        self.stop_trigger = pyo.Trig()
        self.stop_trigger_function = pyo.TrigFunc(self.stop_trigger, deactivate_magnet)

        self.internal_pyo_object_list.extend(
            [self.metro, self.trig_func, self.control_value_count, self.mod]
        )
        if not isinstance(self.period_duration, float):
            self.internal_pyo_object_list.append(self.period_duration)
        walkman.constants.LOGGER.info(
            f"Frequency obj: {self.frequency}, {self.frequency.replication_key}."
        )

        # debug
        # self.p = pyo.Print(self._pyo_object).play()

    def _next_control_point(self) -> float:
        try:
            return next(self._control_point_cycle) * self.fader.get()
        except StopIteration:
            envelope = next(self.envelope_cycle)
            assert envelope
            repetition_count = random.choice(
                range(*self.envelope_repetition_count_range)
            )
            self._control_point_cycle = iter(envelope * repetition_count)
            self.control_value_count.setValue(len(envelope))
            return self._next_control_point()

    def _set_magnetic_field(self, value=None):
        if value is None:
            value = int(self._next_control_point())
        walkman.constants.LOGGER.debug(f"Send value {value} on pin = {self.pin}.")
        self.board.analog_write(self.pin, value)

    def _stop_without_fader(self, wait: float = 0):
        super()._stop_without_fader(wait=wait)
        self.stop_trigger.play(delay=wait + 0.1)

    def close(self):
        super().close()
        self.board.analog_write(self.pin, 0)
        self.board.shutdown()
