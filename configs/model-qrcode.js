{
    "workflow": "Integrated",
        "sensorState": {
        // example - config generated on Android so we have a MAC Address
        // using the MAC address as config filter ASSUMES the beacon does
        // NOT randomize the MAC address; I think this is true for most of them
        // but not necessarily all
        "BLESensorsAndroid" : {
            "sensors": [
                {
                    "id": "DC:23:4D:EB:88:46",
                    "name": "TY",
                    "localName": "TY",
                    "isConnectable": "true",
                    "serviceUUIDs": "a201"
                }, {
                    "id": "E6:91:DF:7B:E5:4D",
                    "name": "HOTAIR E54D",
                    "localName": "HOTAIR E54D",
                    "isConnectable": "true",
                    "serviceUUIDs": "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
                }
            ]
        },
        "BLESensorsiOS" : {
            "sensors": [
                {
                    // in the iOS case, we do not have a MAC address and there
                    // is no point in conveying the API UUID for sensor selection
                    // purposes on initial active scan

                    // HOWEVER it sill might make sensor to keep the originating
                    // UUID around, because that would allow post recording and
                    // upload to verify with 100% that the recorded sensor was 
                    // in fact the one the QRcode originator saw
                    // this would require the QRcode to be input to the 
                    // post-upload decoding
                    // this assumes the originating UUID will be retained
                    // as part of the recordings metadata

                    // in the Android case, the ex-post validation could simply
                    // happen through the MAC address
                    "name": "TPMS1_121A64",
                    "id": "659702ad-9718-92af-2443-eaabfe9f494d",
                    "localName": "",
                    "isConnectable": "0",
                    "serviceUUIDs": "fbb0"
                }, {
                    "name": "Ruuvi BDA2",
                    "id": "6ec7c2f2-bd98-5e88-19ed-776a439185ea",
                    "localName": "",
                    "isConnectable": "1",
                    "serviceUUIDs": "" // NB missing service UUID as I reported
                },
                {
                    "name": "COMMON",
                    "id": "763b2929-15c1-906f-fcee-83298fcb631e",
                    "localName": "TY",
                    "isConnectable": "1",
                    "serviceUUIDs": "a201"
                },
                {
                    "name": "032240133",
                    "id": "e542101a-2a02-1c6e-7c28-c91fcc03a7b2",
                    "localName": "032240133",
                    "isConnectable": "1",
                    "serviceUUIDs": "ff00"
                },
                {
                    "name": "FlowSensor866B1E",
                    "id": "da4847e1-108f-89b6-15ce-566d86a26006",
                    "localName": "",
                    "isConnectable": "0",
                    "serviceUUIDs": "4faf"
                }
            ]
        },
        "Accelerometer": {
            "enabled": false,
                "speed": 1000
        },
        "Gravity": {
            "enabled": false,
                "speed": 1000
        },
        "Gyroscope": {
            "enabled": false,
                "speed": 1000
        },
        "Orientation": {
            "enabled": false,
                "speed": 1000
        },
        "Magnetometer": {
            "enabled": false,
                "speed": 1000
        },
        "Barometer": {
            "enabled": true,
                "speed": 1000
        },
        "Light": {
            "enabled": false
        },
        "Location": {
            "enabled": false,
                "speed": 1000
        },
        "Microphone": {
            "enabled": true,
                "speed": "disable"
        },
        "Camera": {
            "enabled": false
        },
        "Heart Rate": {
            "enabled": false
        },
        "Wrist Motion": {
            "enabled": false
        }
    },
    "http": {
        "enabled": true,
            "url": "http://172.16.0.212:4711",
                "batchPeriod": 1000,
                    "authToken": "fooauth"
    },
    "additionalLocation": false,
        "uncalibrated": false,
            "fileFormat": ".json",
                "fileName": "RECORDING_NAME-DATETIME_LOCAL_FORMATTED"
}
