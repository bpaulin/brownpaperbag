import logging
import myhome

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
# my.sendcommand('1', '1', '0012')
# time.sleep(5)
# my.sendcommand('1', '0', '0012')
# lights = []
# my.send('*#1*0##')
# while True:
#     response = my.receive().decode('latin1')
#     if response == "*#*1##":
#         break
#     lights.append(response[5:-2])
#
# print(lights)

# for light in lights:
#     print('light #'+light)
#     my.sendcommand('1','1',light)
#     time.sleep(5)
#     my.sendcommand('1','0',light)
# while response = my.receive().decode(self.ENCODING) != "*#*1##":
#     print('light')
