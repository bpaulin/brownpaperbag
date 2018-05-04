import logging
import myhome
import time

logger = logging.getLogger('myhome')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

ch.setFormatter(formatter)
logger.addHandler(ch)

my = myhome.MyHomeSocket("192.168.1.13", 20000, 'azerty123')
my.connect()
lights = []
my.send('*#1*0##')
while True:
    response = my.receive()
    if response == "*#*1##":
        break
    lights.append(response[5:-2])

print(lights)

for light in lights:
    print('light #'+light)
    my.sendcommand('1','0',light)
