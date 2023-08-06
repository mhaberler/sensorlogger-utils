decode_ble
=============

sensorlogger records BLE advertisements including serviceUUIDs and manufacturer data.
However, sensorlogger has no knowledge of any particular sensor - it just records
the raw data. To retrieve meaningful sensor values, the sensorlogger log
needs post-processing with a sensor-aware script.

decode_ble processes a sensorlogger JSON export containing BLE advertisements,
and decorates the JSON file with the decoded values.

Here's an example of a Ruuvi sensor tag as it appears in the sensorlogger JSON export:

`````
    {
        "sensor": "BluetoothHOTAIRE54D",
        "time": "1689002042582000000",
        "seconds_elapsed": "13.528000244140625",
        "id": "54edede7-44ae-d2ab-c0a4-21c34d29d909",
        "rssi": "-73",
        "name": "HOTAIR E54D",
        "kCBAdvDataTimestamp": "710694842.581245",
        "isConnectable": "1",
        "kCBAdvDataRxPrimaryPHY": "129",
        "kCBAdvDataRxSecondaryPHY": "0",
        "manufacturerData": "99040513b77414a7a801c0fd20024ca1567a13b9e691df7be54d"
    },
`````

Processing with `decode_ble` extends this to:
`````
 {
    "sensor": "BluetoothHOTAIRE54D",
    "time": "1689002042582000000",
    "seconds_elapsed": "13.528000244140625",
    "id": "54edede7-44ae-d2ab-c0a4-21c34d29d909",
    "rssi": "-73",
    "name": "HOTAIR E54D",
    "kCBAdvDataTimestamp": "710694842.581245",
    "isConnectable": "1",
    "kCBAdvDataRxPrimaryPHY": "129",
    "kCBAdvDataRxSecondaryPHY": "0",
    "manufacturerData": "99040513b77414a7a801c0fd20024ca1567a13b9e691df7be54d",
    "decoded": {
      "name": "HOTAIR E54D",
      "brand": "Ruuvi",
      "model": "RuuviTag",
      "model_id": "RuuviTag_RAWv2",
      "type": "ACEL",
      "track": true,
      "tempc": 25.235,
      "tempf": 77.423,
      "hum": 74.29,
      "pres": 929.2,
      "accx": 0.43933792,
      "accy": -0.72176944,
      "accz": 0.57663102,
      "volt": 2.89,
      "tx": 4,
      "mov": 122,
      "seq": 5049,
      "mac": "E6:91:DF:7B:E5:4D"
    }
  },
`````

# Dependencies

decode_ble relies on the [TheengsDecoder](https://decoder.theengs.io/) library and Python module. Find the [source here](https://github.com/theengs/decoder).

TheengsDecoder currently decodes about [80 different BLE devices](https://decoder.theengs.io/devices/devices.html).

# Extending for new or custom devices
You have two options:
- extend TheengsDecoder
- write your own decoder using the custom.py module.

# Decoding example for a custom sensor
I built a custom sensor, see here: https://github.com/mhaberler/flowsensor/tree/main

I added decoding for this sensor in custom.py.

An undecoded sensorlogger report from this sensor:

`````
    {
        "sensor": "BluetoothFlowSensor848D7E",
        "time": "1689002029097000000",
        "seconds_elapsed": "0.043",
        "id": "ca54186c-0c76-1554-a9f8-bff861dcf32f",
        "rssi": "-35",
        "name": "FlowSensor848D7E",
        "serviceUUIDs": "4faf",
        "kCBAdvDataRxPrimaryPHY": "129",
        "kCBAdvDataRxSecondaryPHY": "0",
        "manufacturerData": "1147f412fa848d7e1a000000b9bae60100006409",
        "isConnectable": "0",
        "kCBAdvDataTimestamp": "710694829.097247"
    },
`````

The decoded report looks like so:
`````
  {
    "sensor": "BluetoothFlowSensor848D7E",
    "time": "1689002029097000000",
    "seconds_elapsed": "0.043",
    "id": "ca54186c-0c76-1554-a9f8-bff861dcf32f",
    "rssi": "-35",
    "name": "FlowSensor848D7E",
    "serviceUUIDs": "4faf",
    "kCBAdvDataRxPrimaryPHY": "129",
    "kCBAdvDataRxSecondaryPHY": "0",
    "manufacturerData": "1147f412fa848d7e1a000000b9bae60100006409",
    "isConnectable": "0",
    "kCBAdvDataTimestamp": "710694829.097247",
    "decoded": {
      "type": "customFLowSensor",
      "brand": "Haberler",
      "mac": "F4:12:FA:84:8D:7E",
      "mfid": 18193,
      "count": 26,
      "last_change": 31898297,
      "rate": 0,
      "batteryLevel": 100,
      "flags": 9
    }
  },
`````

# Scanning BLE devices

decode_ble can also scan for devices using the [Bleak](https://bleak.readthedocs.io/en/latest/index.html) client:
````
decode_ble --scan [--duration <seconds>]
````


# Installation

````
git clone https://github.com/mhaberler/sensorlogger-utils.git
cd decode_ble
python setup.py install
````

