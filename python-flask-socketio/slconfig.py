from PIL import Image

import pyzstd
import base64
import json
import qrcode


prefix = b"sensorlogger://config/"

def genconfig(uri, authToken=None, rate=1000, **kwargs):
    cfg = {
        "sensorState": {"Location": {"enabled": True, "speed": rate}},
        "http": {
            "enabled": True,
            "url": uri,
            "batchPeriod": rate,
        },
        "fileFormat": ".json",
        "fileName": "DATETIME_LOCAL_FORMATTED-RECORDING_NAME",
    }
    if authToken:
        cfg["http"]["authToken"] = authToken
    s = json.dumps(cfg).encode()
    z = pyzstd.compress(s)
    e = prefix + base64.b64encode(z)
    return e


if __name__ == "__main__":
    ip = "172.16.0.212"
    port = 5010
    route = "tracking"
    uri = f"http://{ip}:{port}/{route}"
    e = genconfig(uri, authToken="foo=bar")
    print(e)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(e)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("genconfig.png")

# suggested = {
#     "workflow": "Integrated",
#     "sensorState": {
#         "Accelerometer": {"enabled": None, "speed": 1000},
#         "Gravity": {"enabled": None, "speed": 1000},
#         "Gyroscope": {"enabled": None, "speed": 1000},
#         "Orientation": {"enabled": None, "speed": 1000},
#         "Magnetometer": {"enabled": None, "speed": 1000},
#         "Barometer": {"enabled": None, "speed": 1000},
#         "Location": {"enabled": True, "speed": 1000},
#         "Microphone": {"enabled": None, "speed": "disable"},
#         "Camera": {"enabled": None, "speed": 600000},
#         "Battery": {"enabled": None},
#         "Brightness": {"enabled": None},
#         "Heart Rate": {"enabled": None},
#         "Wrist Motion": {"enabled": None},
#     },
#     "http": {
#         "enabled": True,
#         "url": "https://foobar.com/push",
#         "batchPeriod": 1000,
#         "authToken": "foo=bar",
#     },
#     "additionalLocation": True,
#     "uncalibrated": None,
#     "fileFormat": ".json",
#     "fileName": "DATETIME_LOCAL_FORMATTED-RECORDING_NAME",
# }
