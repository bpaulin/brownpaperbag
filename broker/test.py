from brownpaperbag.bpbgate import BpbGate
import logging
import paho.mqtt.client as mqtt
import re

mqttc = mqtt.Client()
mqttc.connect("localhost")
mqttc.loop_start()

logger = logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

gate = BpbGate('192.168.1.13', 20000, 'azerty123')
gate.set_logger(logging)
gate.connect()
p = re.compile(r'\d+')
while True:
    msg = gate.receive()
    wh = p.findall(msg)
    try:
        if wh[0] not in ('1', '2'):
            logging.info('skip message '+msg)
            continue
        mqttc.publish('bticino/'+wh[0]+'/'+wh[1], wh[2], retain=True)
    except:
        pass