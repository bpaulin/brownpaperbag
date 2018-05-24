from brownpaperbag.bpbgate import BpbGate
import logging
import paho.mqtt.client as mqtt
import re

msg_regex = re.compile(r'(\*\d*\*\d*\*\d*##|\*#\d+\*\d+\*\d+\*\d+##)')
msg_topic_regex = re.compile(r'\d+')


def split_message(raw_msg):
    """split event message from openwebnet to atomic event"""
    return msg_regex.findall(raw_msg)


def message_to_topic_and_value(raw_msg):
    """convert openwebnet event to topic and value for mqtt"""
    wh = msg_topic_regex.findall(raw_msg)
    if len(wh) == 3 and wh[0] in ('1', '2'):
        return {
            'topic': '/'+wh[0]+'/'+wh[2],
            'payload': wh[1]
        }
    if len(wh) == 4 and wh[0] == '18':
        return {
            'topic': '/'+wh[0]+'/'+wh[1],
            'payload': wh[3]
        }
    logging.warning('Unable to convert message: %s', raw_msg)
    return False


if __name__ == '__main__':

    mqttc = mqtt.Client()
    mqttc.connect("localhost")
    mqttc.loop_start()

    def log_callback(client, userdata, level, buf):
        logging.debug(buf)

    mqttc.on_log = log_callback
    gate = BpbGate('192.168.1.13', 20000, 'azerty123')
    gate.logger = logging.basicConfig(level=logging.DEBUG)

    gate.connect()
    while True:
        msgs = split_message(gate.receive())
        for msg in msgs:
            to_publish = message_to_topic_and_value(msg)
            if to_publish:
                mqttc.publish(
                    'bticino'+to_publish['topic'],
                    to_publish['payload'],
                    retain=True
                )
            else:
                logging.info('skip message '+msg)
