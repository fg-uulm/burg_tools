import sys
import time
sys.path.append('/home/pi/ola_build/ola/python')

from ola.ClientWrapper import ClientWrapper
from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

# Lamp configuration:
DMX_UNIVERSE = 1
CONFIG_FILE  = 'tradfri_standalone_psk.conf'
TRADFRI_IP   = '192.168.188.21'
START_ADDR = 1      # DMX Start address
LAST_SEND = 0
LAST_DATA = [1] * 100

# Handle DMX Frame
def NewData(data):
  global LAST_SEND
  global LAST_DATA
  global START_ADDR
  try:
     millis = int(round(time.time() * 1000))
     if(millis - LAST_SEND > 30):
       LAST_SEND = millis
       # print("Send")
       # Lamps control from DMX frames
       # print("Send")
       for i in range(len(lights)):
          if(i < 17):
            if(LAST_DATA[START_ADDR+i-1] != data[START_ADDR+i-1]):
               print("Sending "+str(i))
               api(lights[i].light_control.set_dimmer(min(data[START_ADDR+i-1],254)))
       LAST_DATA = data
  except:
     #LAST_SEND = 0
     #print("NAS")
     LAST_DATA = data


# Init Tradfri
conf = load_json(CONFIG_FILE)


try:
    identity = conf[TRADFRI_IP].get('identity')
    psk = conf[TRADFRI_IP].get('key')
    api_factory = APIFactory(host=TRADFRI_IP, psk_id=identity, psk=psk)
except KeyError:
    identity = uuid.uuid4().hex
    api_factory = APIFactory(host=TRADFRI_IP, psk_id=identity)

    try:
        psk = api_factory.generate_psk(args.key)
        print('Generated PSK: ', psk)

        conf[TRADFRI_IP] = {'identity': identity,
                           'key': psk}
        save_json(CONFIG_FILE, conf)
    except AttributeError:
        raise PytradfriError("Please provide the 'Security Code' on the "
                             "back of your Tradfri gateway using the "
                             "-K flag.")

api = api_factory.request

gateway = Gateway()

devices_command = gateway.get_devices()
devices_commands = api(devices_command)
devices = api(devices_commands)

lights = [dev for dev in devices if dev.has_light_control]

# Print all lights
print("Available lights:")
print(lights)

# Start listen to OLA
print("Starting OLA connector...")
wrapper = ClientWrapper()
client = wrapper.Client()
client.RegisterUniverse(DMX_UNIVERSE, client.REGISTER, NewData)
wrapper.Run()
