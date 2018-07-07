"""gateway mqtt<->openwebnet."""
from brownpaperbag.bpbgate import BpbGate, SESSION_EVENT, SESSION_COMMAND
import logging
import paho.mqtt.client as mqtt
import re

msg_regex = re.compile(r'(\*\d*\*\d*\*\d*##|\*#\d+\*\d+\*\d+\*\d+##)')
msg_topic_regex = re.compile(r'\d+')


def split_message(raw_msg):
    """Split event message from openwebnet to atomic event."""
    return msg_regex.findall(raw_msg)


def message_to_topic_and_value(raw_msg):
    """Convert openwebnet event to topic and value for mqtt."""
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


def on_connect(client, userdata, flags, rc):
    """Subscribe to right topic."""
    client.subscribe("bticino/+/+/set")


def on_message(client, userdata, msg):
    """Send Openwebnet command when a message is received."""
    logging.info('handling '+msg.payload.decode()+' on topic '+msg.topic)
    wh = msg.topic.split('/')
    gate_command.send_command(wh[1], msg.payload.decode(), wh[2])
    gate_command.receive()


if __name__ == '__main__':
    """Launch mqtt client to publish and subscribe."""
    logging.basicConfig(level=logging.DEBUG)
    logging.info('starting')
    mqttc = mqtt.Client()
    mqttc.connect("localhost")
    mqttc.loop_start()

    def log_callback(client, userdata, level, buf):
        """Log when mqtt receive or post a message."""
        logging.debug(buf)

    mqttc.on_log = log_callback
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    gate_event = BpbGate('192.168.1.13', 20000, 'azerty123', SESSION_EVENT)
    #gate_event.logger = logging.basicConfig(level=logging.DEBUG)
    gate_event.connect()
    gate_command = BpbGate('192.168.1.13', 20000, 'azerty123', SESSION_COMMAND)
    gate_command.logger = logging.basicConfig(level=logging.DEBUG)
    gate_command.connect()
    while True:
        msgs = split_message(gate_event.receive())
        for msg in msgs:
            to_publish = message_to_topic_and_value(msg)
            if to_publish:
                mqttc.publish(
                    'bticino'+to_publish['topic'],
                    to_publish['payload'],
                    retain=True
                )
            else:
                logging.warning('skip message '+msg)
