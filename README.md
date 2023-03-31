# 10.1

Composition for aeolian harps + siter panerus, for the duration of one moon cycle (~ 27.5 days).


## Tuning of boxes

Please see `mutwo/project_parameters/instruments.py`:

- box 1: f
- box 2: a
- box 3: d


## start script

1. ./scripts/set-permission
2. ./scripts/start-jack-server-usb
3. walkman walkman.toml.j2
4. ./scripts/record.py
5. ./scripts/connect-jack-usb

## Internal representation of aeolian harp

This is a bit complicated, because in walkman each string need to be represented by an individual sequential event, on the notation level we simply use one staff.

So this is solved like this:

- the basic internal representation of an aeolian event harp is a SimultaneousEvent with 9 SequentialEvent
- the tag of the SimultaneousEvent is 'aeolian harp'
- when converted to notation this SimultaneousEvent is merged together to one SequentialEvent
- diary entries usually return one SimultaneousEvent with 9 SequentialEvent as this is the expected internal representation
- but during the nighttime we use entries where each entry is responsible for exactly one string
- the mutwo representation is therefore a SimultaneousEvent with exactly one SequentialEvent
- tag of those SimultaneousEvent is 'aeolian harp {index}'
