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
filename = f"etc/recordings/{now[:13]}_{now[14:16]}"
record_tuple = tuple(
    pyo.Record(inp, f"{filename}_{i}.ogg", sampletype=4, fileformat=7, chnls=1, quality=0.9)
    # pyo.Record(inp, f"{filename}_{i}.wav", sampletype=4, fileformat=0, chnls=1, quality=0.9)
    for i, inp in enumerate(input_tuple)
)

for inp in input_tuple:
    inp.play()

for rec in record_tuple:
    rec.play()

print("Start recording on", filename)

try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, Exception):
    for rec in record_tuple:
        rec.stop()
    print("Record stopped.")
server.stop()
