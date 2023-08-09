from PIL import Image

import pyzstd
import base64
import json
import qrcode
from copy import deepcopy
import re

RE_INT = re.compile(r"^[-+]?([1-9]\d*|0)$")
RE_FLOAT = re.compile(r"^[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?$")


prefix = b"sensorlogger://config/"

template = {
    "workflow": "Classic",
    "sensorState": {
        "Accelerometer": {"enabled": False, "speed": 1000},
        "Gravity": {"enabled": False, "speed": 1000},
        "Gyroscope": {"enabled": False, "speed": 1000},
        "Orientation": {"enabled": False, "speed": 1000},
        "Magnetometer": {"enabled": False, "speed": 1000},
        "Barometer": {"enabled": False, "speed": 1000},
        "Location": {"enabled": True, "speed": 1000},
        "Microphone": {"enabled": False, "speed": "disable"},
        "Camera": {"enabled": False, "speed": 600000},
        "Battery": {"enabled": False},
        "Brightness": {"enabled": False},
        "Pedometer": {"enabled": False},
        "Heart Rate": {"enabled": False},
        "Wrist Motion": {"enabled": False},
    },
    "http": {
        "enabled": True,
        "url": "",
        "batchPeriod": 1000,
        "authToken": None,
    },
    "additionalLocation": False,
    "uncalibrated": False,
    "fileFormat": ".json",
    "fileName": "RECORDING_NAME-DATETIME_LOCAL_FORMATTED",
}


def make_numeric(value):
    if RE_INT.match(value):
        return int(value)
    if RE_FLOAT.match(value):
        return float(value)
    return value


def merge(request, params):
    t = deepcopy(template)
    enabled = request.form.getlist("sensors")
    for s in enabled:
        t["sensorState"][s]["enabled"] = True

    accelRate = request.form.getlist("accelRate")[0]
    for s in ["Accelerometer", "Gravity", "Gyroscope", "Orientation", "Magnetometer"]:
        t["sensorState"][s]["speed"] = make_numeric(accelRate)
    baroRate = request.form.getlist("baroRate")[0]
    t["sensorState"]["Barometer"]["speed"] = make_numeric(baroRate)
    # remove config for disabled sensors
    for k in template["sensorState"].keys():
        if not k in enabled:
            t["sensorState"].pop(k, None) 

    t.update(params)
    batchPeriod = request.form.getlist("batchPeriod")[0]
    t["http"]["batchPeriod"] = make_numeric(batchPeriod)
    t["uncalibrated"] = len(request.form.getlist("Uncalibrated")) > 0
    return t


def gen_export_code(cfg):
    s = json.dumps(cfg).encode()
    z = pyzstd.compress(s)
    return prefix + base64.b64encode(z)


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
