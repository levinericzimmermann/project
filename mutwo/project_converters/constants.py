import types

F0 = types.SimpleNamespace()

F0.PARAMETER_DELIMITER = ","
F0.EVENT_DELIMITER = "\n"
F0.MAX_DURATION = 900  # miliseconds
F0.MIN_VELOCITY = 2

F0.STATE_NEW = 0
F0.STATE_KEEP = 1
F0.STATE_STOP = 2
