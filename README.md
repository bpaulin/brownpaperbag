# brown paper bag

python package to communicate with myHomeServer1 (legrand/bticino) using openwebnet protocol

## brown paper what?

because You were lucky to have a [ROOM](https://www.youtube.com/watch?v=ue7wM0QC5LE)! *We* used to have to live in a [corridor](http://www.montypython.net/scripts/4york.php)!

## how to use
```python
from brownpaperbag.bpbgate import BpbGate

gate = BpbGate("192.168.1.1300", 20000, 'azerty123')

lights = gate.get_light_ids() # return list of every light
gate.turn_on_light('01') # turn on light #01
gate.turn_off_light('01') # turn off light #01
gate.is_light_on('01') # return true if light #01 is on
```

homeassistant/light/bticino/01/config
{"name": "prise", "command_topic": "bticino/1/01/set",  "payload_on": "1", "payload_off": "0", "state_topic":"bticino/1/01"}