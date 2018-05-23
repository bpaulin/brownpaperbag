from brownpaperbag.bpbgate import BpbGate
import logging
import paho.mqtt.client as mqtt
import re

msg_regex = re.compile(r'(\*\d*\*\d*\*\d*##|\*#\d+\*\d+\*\d+\*\d+##)')
msg_topic_regex = re.compile(r'\d+')


def split_message(raw_msg):
    return msg_regex.findall(raw_msg)


def message_to_topic_and_value(raw_msg):
    wh = msg_topic_regex.findall(raw_msg)
    if wh[0] in ('1', '2'):
        return {
            'topic': '/'+wh[0]+'/'+wh[2],
            'payload': wh[1]
        }
    if wh[0] == '18':
        return {
            'topic': '/'+wh[0]+'/'+wh[1],
            'payload': wh[3]
        }
    return False

if __name__ == '__main__':
    logger = logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    mqttc = mqtt.Client()
    mqttc.connect("localhost")
    mqttc.loop_start()

    def log_callback(client, userdata, level, buf):
        logging.debug(buf)

    mqttc.on_log = log_callback
    gate = BpbGate('192.168.1.13', 20000, 'azerty123')
    gate.set_logger(logging)

    gate.connect()
    while True:
        msgs = split_message(gate.receive())
        for msg in msgs:
            to_publish = message_to_topic_and_value(msg)
            if to_publish:
                mqttc.publish('bticino'+to_publish['topic'], to_publish['payload'], retain=True)
            else:
                logging.info('skip message '+msg)
