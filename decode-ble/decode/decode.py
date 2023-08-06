import click
import asyncio
import json
from TheengsDecoder import decodeBLE
from TheengsDecoder import getProperties, getAttribute
import sys
from bleak import BleakScanner
import struct


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


try:
    sys.path.append(".")
    import custom

    customDecoder = custom.Decoder

except Exception:
    customDecoder = None


def detection_callback(device, advertisement_data):
    print(f"{device.address}:{advertisement_data}")
    data_json = {}

    if advertisement_data.service_data:
        dstr = list(advertisement_data.service_data.keys())[0]
        # TheengsDecoder only accepts 16 bit uuid's, this converts the 128 bit uuid to 16 bit.
        data_json["servicedatauuid"] = dstr[4:8]
        dstr = str(list(advertisement_data.service_data.values())[0].hex())
        data_json["servicedata"] = dstr

    if advertisement_data.manufacturer_data:
        dstr = str(
            struct.pack(
                "<H", list(advertisement_data.manufacturer_data.keys())[0]
            ).hex()
        )
        dstr += str(list(advertisement_data.manufacturer_data.values())[0].hex())
        data_json["manufacturerdata"] = dstr

    if advertisement_data.local_name:
        data_json["name"] = advertisement_data.local_name

    if data_json:
        data_json["id"] = device.address
        data_json["rssi"] = advertisement_data.rssi
        print("data sent to decoder: ", json.dumps(data_json))
        data_json = decodeBLE(json.dumps(data_json))
        print("TheengsDecoder found device:", data_json)

        if data_json:
            dev = json.loads(data_json)
            print(getProperties(dev["model_id"]))
            brand = getAttribute(dev["model_id"], "brand")
            model = getAttribute(dev["model_id"], "model")
            print("brand:", brand, ", model:", model)


async def ble_scan(seconds):
    # scanning_mode='passive' # Windows only
    scanner = BleakScanner(detection_callback=detection_callback)
    await scanner.start()
    await asyncio.sleep(seconds)
    await scanner.stop()

    for d in scanner.discovered_devices:
        print(d)


@click.command()
@click.option("--scan/--no-scan", default=False)
@click.option("--duration", default=5.0)
@click.option("--debug/--no-debug", default=False)
@click.option("--custom/--no-custom", default=False)
@click.argument("input", type=click.File("r"), default="-", nargs=1)
@click.argument("output", type=click.File("w"), default="-", nargs=1)
def cli(scan, duration, debug, custom, input, output):
    if scan:
        asyncio.run(ble_scan(duration))
    else:
        """decode BLE announcements in a sensorlogger JSON log"""
        j = json.load(input)
        for sample in j:
            if sample["sensor"].startswith("Bluetooth"):
                data = {}
                data["name"] = sample["name"]
                data["id"] = sample["id"]
                try:
                    # Kelvin fix needed
                    # this should be an array
                    # data['servicedatauuid'] = list(sample['serviceUUIDs'])
                    data["servicedatauuid"] = [sample["serviceUUIDs"]]
                except KeyError:
                    pass
                data["manufacturerdata"] = sample["manufacturerData"]
                result = decodeBLE(json.dumps(data))
                if result:
                    js = json.loads(result)
                    js.pop("id", None)
                    js.pop("mfid", None)
                    js.pop("manufacturerdata", None)
                    js.pop("servicedatauuid", None)
                    sample["decoded"] = js
                    if debug and sample["decoded"]:
                        print(json.dumps(sample, indent=2))
                    continue

                if customDecoder:
                    result = customDecoder(data, debug)
                    if result:
                        sample["decoded"] = result
                        continue
                eprint(f"failed to decode: {sample}")

        print(json.dumps(j, indent=2), file=output)
