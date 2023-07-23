{
    "workflow": "Integrated",
    "sensorState": {
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
