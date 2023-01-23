import random
import time

import numpy as np
from mutwo import music_parameters

from telemetrix import telemetrix

try:
    board = telemetrix.Telemetrix("/dev/ttyACM0", arduino_instance_id=1)
    pin = 3
    board.set_pin_mode_analog_output(pin)

    frequency = music_parameters.JustIntonationPitch("3/5").frequency
    period_duration = 1 / (frequency / 2)

    # higher control numbers -> much more overtones
    # control_value_tuple = tuple(np.geomspace(1, 256, num=250))

    # lower control numbers -> much more stable
    control_value_tuple = tuple(np.geomspace(1, 256, num=70))

    # no sound at all for 35 :)
    # control_value_tuple = tuple(np.geomspace(1, 256, num=35))

    # control_value_tuple = (0, 255)

    control_value_tuple += tuple(reversed(control_value_tuple))
    control_value_tuple = tuple(map(int, control_value_tuple))

    curve_list = (
        # control_value_tuple,
        # !! THOSE VERY SIMPLE ENVELOPES BELOW WORK BEST !!
        (0, 150, 200, 255, 200, 150, 0),
        # (0, 150, 200, 225, 255, 225, 200, 150, 0),
    )

    while 1:
        control_value_tuple = random.choice(curve_list)
        control_value_count = len(control_value_tuple)
        sleep_time = period_duration / control_value_count
        for control_value in control_value_tuple:
            board.analog_write(pin, control_value)
            time.sleep(sleep_time)

except KeyboardInterrupt:
    pass

finally:
    board.analog_write(pin, 0)
    board.shutdown()
