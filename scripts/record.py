#! /usr/bin/env python3
import datetime
import time

import pyo

channel_count = 4
server = (
    pyo.Server(
        jackname="10-1-record", audio="jack", ichnls=channel_count, nchnls=channel_count
    )
    .boot()
    .start()
)
input_tuple = tuple(pyo.Input(n) for n in range(channel_count))
now = datetime.datetime.now().isoformat()
filename = f"etc/recordings/{now[:13]}_{now[14:16]}.wav"

print("Start recording on", filename)

server.recordOptions(sampletype=4, fileformat=0)
server.recstart(filename)
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, Exception):
    server.recstop()
    print("Record stopped.")
server.stop()
