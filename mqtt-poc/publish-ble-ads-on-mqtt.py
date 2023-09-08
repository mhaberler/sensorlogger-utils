
import argparse
import asyncio
import logging
import os
import json
import struct
import shortuuid
import binascii
import paho.mqtt.client as mqtt

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

clientuuid = "123456789ABCDEF"

logger = logging.getLogger(__name__)
        
def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def simple_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    # prepare a bleak ad such that it can be directly fed to theengs/decoder
    # taken from theengs/decoder/examples/python/ScanAndDecode.py
    data_json = {}
    if advertisement_data.service_data:
        dstr = list(advertisement_data.service_data.keys())[0]
        # TheengsDecoder only accepts 16 bit uuid's, this converts the 128 bit uuid to 16 bit.
        data_json['servicedatauuid'] = dstr[4:8]
        dstr = str(list(advertisement_data.service_data.values())[0].hex())
        data_json['servicedata'] = dstr

    if advertisement_data.manufacturer_data:
        dstr = str(struct.pack('<H', list(advertisement_data.manufacturer_data.keys())[0]).hex())
        dstr += str(list(advertisement_data.manufacturer_data.values())[0].hex())
        data_json['manufacturerdata'] = dstr

    if advertisement_data.local_name:
        data_json['name'] = advertisement_data.local_name
    if data_json:
        data_json["id"] = device.address
        data_json["rssi"] = advertisement_data.rssi    
        
        logger.info("%s: %r", device.address, data_json)
        mqttc.publish(f"/sensorlogger/{clientuuid}/ble/ads/{device.address}", json.dumps(data_json)) 
    
async def main(args: argparse.Namespace):
    scanner = BleakScanner(
        simple_callback, None, cb=dict(use_bdaddr=args.macos_use_bdaddr)
    )

    while True:
        logger.info("(re)starting scanner")
        await scanner.start()
        await asyncio.sleep(5.0)
        await scanner.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--macos-use-bdaddr",
        action="store_true",
        help="when true use Bluetooth address instead of UUID on macOS",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="sets the logging level to debug",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    mqttc = mqtt.Client(f'client-{shortuuid.uuid()}', transport="websockets")
    mqttc.ws_set_options(path="/mqtt", headers=None)
    mqttc.tls_set()

    mqttc.username_pw_set(username=os.getenv("MQTT_USER"),password=os.getenv("MQTT_PASS"))
    mqttc.on_connect = on_connect

    print(f'trying to connect.....')
    mqttc.connect(os.getenv("MQTT_BROKER"), 443, 60)


    asyncio.run(main(args))
