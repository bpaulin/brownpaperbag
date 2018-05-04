import logging
from light import myhome

import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

ch.setFormatter(formatter)
logger.addHandler(ch)

my = myhome.MyHomeSocket("192.168.1.13", 20000, 'azerty123')
my.setlogger(logger)

cuisine = myhome.MyHomeLight('0012',my)
hacuisine = myhome.AwesomeLight(cuisine)

while True:
    logger.info('turn on')
    hacuisine.turn_off()
    logger.info('request')
    hacuisine.update()
    logger.info(hacuisine.is_on)

    time.sleep(1)

    logger.info('turn off')
    hacuisine.turn_off()
    logger.info('request')
    hacuisine.update()

    logger.info(hacuisine.is_on)

# lights = []
# my.send('*#1*0##')
# while True:
#     response = my.receive()
#     if response == "*#*1##":
#         break
#     lights.append(response[5:-2])
#
# print(lights)
#
# for light in lights:
#     print('light #'+light)
#     my.sendcommand('1','0',light)
