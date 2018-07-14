"""gateway mqtt<->openwebnet."""
import logging
import paho.mqtt.client as mqtt
import json

from brownpaperbag.bpbgate import BpbGate, SESSION_EVENT, SESSION_COMMAND

lights = {
    "salon_prise": "01",
    "salon_plafond": "02",
    "cuisine_plafond": '0012',
    "cuisine_meuble": '0011',
    "parents": '15',
    "enfant": '19',
    "bureau": '0111',
    "wc": '04',
    "couloir": '11',
    "sdb_plafond": '0010',
    "sdb_prise": '09',
    "buanderie": '0014'
}

sensors = {

}

logging.basicConfig(level=logging.DEBUG)
logging.info('starting')
mqttc = mqtt.Client()
mqttc.connect("localhost")
mqttc.loop_start()

for name, where in lights.items():
    print(name, where)
    payload = {
        "name": name,
        "command_topic": "bticino/1/"+where+"/set",
        "state_topic":"bticino/1/"+where,
        "payload_on": "1",
        "payload_off": "0"
    }
    topic = "homeassistant/light/bticino/"+where+"/config"
    message = mqttc.publish(
        topic,
        json.dumps(payload),
        retain=True
    )
    message.wait_for_publish()