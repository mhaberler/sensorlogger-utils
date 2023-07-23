js = [
    {
        "sensor": "BluetoothMetadata",
        "time": "1690028917795000000",
        "seconds_elapsed": "0.876",
        "id": "DD:79:C6:8F:BD:A2",
        "name": "Ruuvi BDA2",
        "localName": "Ruuvi BDA2",
        "isConnectable": "true",
        "serviceUUIDs_0": "6e400001-b5a3-f393-e0a9-e50e24dcca9e",
        "foo": {
            "sensor": "Microphone",
            "time": "1690028931684000000",
            "seconds_elapsed": "14.765",
            "dBFS": "-131",
        },
    },
    {
        "sensor": "Metadata",
        "version": "3",
        "device name": "SM-G973F",
        "recording time": "2023-07-22_12-28-36",
        "platform": "android",
        "appVersion": "1.17.0",
        "device id": "1d6b3d72-643c-433c-b622-2a62cfbe7afe",
        "sensors": "Microphone|bluetooth-F412FA866B1E|bluetooth-80EACA121A64|bluetooth-DD79C68FBDA2|bluetooth-DB08D33338EF|bluetooth-E691DF7BE54D|Annotation|BluetoothMetadata",
        "sampleRateMs": "100|||||||",
    },
    {
        "sensor": "Microphone",
        "time": "1690028931684000000",
        "seconds_elapsed": "14.765",
        "dBFS": "-131",
    },
    {
        "sensor": "bluetooth-DB08D33338EF",
        "time": "1690028918519000000",
        "seconds_elapsed": "1.6",
        "rssi": "-68",
        "id": "DB:08:D3:33:38:EF",
        "txPowerLevel": "-2147483648",
        "manufacturerData": "0201061bff990405118f5776ffff0070fc18012c8f562e0ea5db08d33338ef11079ecadc240ee5a9e093f3a3b50100406e0b095275757669203338454600",
        "values_name": "Ruuvi 38EF",
        "values_rssi": "-68",
        "values_brand": "Ruuvi",
        "values_model": "RuuviTag",
        "values_model_id": "RuuviTag_RAWv2",
        "values_type": "ACEL",
        "values_track": True,
        "values_tempc": 22.475,
        "values_tempf": 72.455,
        "values_hum": 55.975,
        "values_pres": 1155.35,
        "values_accx": 0.10983448,
        "values_accy": -0.980665,
        "values_accz": 0.2941995,
        "values_volt": 2.746,
        "values_tx": 4,
        "values_mov": 46,
        "values_seq": 3749,
        "values_mac": "DB:08:D3:33:38:EF",
    },
]

t2 = [
    {
        "sensor": "bluetooth-DB08D33338EF",
        "time": "1690028918519000000",
        "rssi": "-68",
    },
]

import re
import json
import arrow
import copy

# arrow.Arrow.fromtimestamp(1690028917795.12312).isoformat()
metadataNames = ["BluetoothMetadata", "Metadata"]


def traverse_and_modify(obj, **kwargs):
    debug = kwargs.get("debug", None)
    options = kwargs.get("options", [])
    useless = kwargs.get("useless", [])
    timestamp = kwargs.get("timestamp", [])
    if isinstance(obj, dict):
        for key, value in obj.copy().items():
            if (
                "drop_metadata" in options
                and key == "sensor"
                and value in metadataNames
            ):
                obj.clear()
                return
            if key in useless:
                if debug:
                    print(f"drop {key=}")
                obj.pop(key)
                continue
            if key == "time" and "linux_timestamp_float" in timestamp:
                obj[key] = float(value) * 1.0e-6
                continue
            if key == "time" and "linux_timestamp" in timestamp:
                obj[key] = int(value) // 1000000
                continue
            if key == "time" and "iso8061" in timestamp:
                obj[key] = arrow.Arrow.fromtimestamp(float(value) * 1.0e-6).isoformat()
                continue
            if "strings_to_numeric" in options and isinstance(value, str):
                try:
                    obj[key] = int(value)
                except ValueError:
                    try:
                        obj[key] = float(value)
                    except ValueError:
                        pass
                    pass
                    continue

        if isinstance(value, dict):
            traverse_and_modify(value, **kwargs)

    elif isinstance(obj, list):
        for _, value in enumerate(obj):
            traverse_and_modify(value, **kwargs)
    return obj


# options = ["drop_metadata", "fix_keys", "drop_useless"]

options = ["drop_metadata", "strings_to_numeric", "fix_keys", "drop_useless"]
useless = ["manufacturerData"]
timestamp = ["linux_timestamp_float"]  # "linux_timestamp" "iso8061" "untouched"
# timestamp = ["linux_timestamp"]  # "linux_timestamp" "iso8061" "untouched"
# timestamp=["iso8061"] # "linux_timestamp" "iso8061" "untouched"
debug = True
# Modifying the value associated with the key "age" to 31
modified_dict = traverse_and_modify(
    js, options=options, useless=useless, timestamp=timestamp, debug=debug
)

# delete empty dicts
final = [x for x in modified_dict if x != {}]


print(json.dumps(final, indent=4))
