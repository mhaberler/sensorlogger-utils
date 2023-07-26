from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime
import json
from flask_qrcode import QRcode

# from flask_cors import CORS
from TheengsDecoder import decodeBLE


"""
Background Thread
"""
thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = "donsky!"
QRcode(app)

# CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")
# socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins='*')

"""
Get current date time
"""


def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")


"""
Generate random sequence of dummy sensor values and send it to our clients
"""


def background_thread():
    app.logger.info(f"Generating random sensor values")
    while True:
        dummy_sensor_value = round(random() * 100, 3)
        socketio.emit(
            "updateSensorData",
            {"value": dummy_sensor_value, "date": get_current_datetime()},
        )
        socketio.sleep(1)


# fanekart/gpsdata/gpsid_kurve.geojson
# http://172.16.0.212:5010/gpspos/gpsid/dakey/
# b'{"messageId":7,"sessionId":"3fbb1ddc-a645-463b-891e-aa0f4c7c0e97","deviceId":"072aaf1a-c294-4b47-86cd-f97fed7e4f26","payload":[{"name":"bluetooth-e691df7be54d","time":1690393567924000000,"values":{"rssi":-78,"id":"E6:91:DF:7B:E5:4D","txPowerLevel":null,"manufacturerData":"9904050dc5887ca4d901bcfd20024894967a56d4e691df7be54d"}},{"values":{"bearingAccuracy":0,"verticalAccuracy":1.417931318283081,"horizontalAccuracy":20,"speedAccuracy":0,"speed":0.012091556563973427,"bearing":0,"altitude":869,"longitude":15.2118591,"latitude":47.1292252},"name":"location","time":1690393568740000000},{"name":"bluetooth-e691df7be54d","time":1690393570516000000,"values":{"rssi":-77,"id":"E6:91:DF:7B:E5:4D","txPowerLevel":null,"manufacturerData":"9904050dc38885a4d901c0fd20024094967a56d5e691df7be54d"}},{"name":"bluetooth-e691df7be54d","time":1690393571788000000,"values":{"rssi":-77,"id":"E6:91:DF:7B:E5:4D","txPowerLevel":null,"manufacturerData":"9904050dc38885a4d901c0fd20024094967a56d5e691df7be54d"}},{"values":{"bearingAccuracy":0,"verticalAccuracy":1.417931318283081,"horizontalAccuracy":20,"speedAccuracy":0,"speed":0.0026552374474704266,"bearing":0,"altitude":869,"longitude":15.2118591,"latitude":47.1292252},"name":"location","time":1690393572879000000},{"name":"bluetooth-e691df7be54d","time":1690393573069000000,"values":{"rssi":-77,"id":"E6:91:DF:7B:E5:4D","txPowerLevel":null,"manufacturerData":"9904050dc38882a4d901bcfd28024494967a56d6e691df7be54d"}},{"values":{"bearingAccuracy":0,"verticalAccuracy":1.3752892017364502,"horizontalAccuracy":20,"speedAccuracy":0,"speed":0.012174158357083797,"bearing":0,"altitude":869,"longitude":15.2118581,"latitude":47.1292252},"name":"location","time":1690393578752000000},{"values":{"bearingAccuracy":0,"verticalAccuracy":1.3752892017364502,"horizontalAccuracy":20,"speedAccuracy":0,"speed":0.0029675213154405355,"bearing":0,"altitude":869,"longitude":15.211858,"latitude":47.1292252},"name":"location","time":1690393582895000000}]}'
@app.route("/gpspos/<gpsId>/<secretGpsKey>/", methods=["GET", "POST"])
def getpos(gpsId="", secretGpsKey=""):
    # if secretGpsKey not in mySecretGpsKeys:
    #     abort(401)
    #     pass
    body = json.loads(request.data)
    messageId = body["messageId"]
    sessionId = body["sessionId"]
    deviceId = body["deviceId"]
    for p in body["payload"]:
        if p.get("name", None) == "location":
            time = p["time"]
            lat = p["values"]["latitude"]
            lon = p["values"]["longitude"]
            alt = p["values"]["altitude"]
            app.logger.info(f"post {lat=} {lon=} {alt=}")
            socketio.emit(
                "updateLocation",
                {
                    "time": time,
                    "lat": lat,
                    "lon": lon,
                    "alt": alt,
                    "messageId": messageId,
                    "deviceId": deviceId,
                    "sessionId": sessionId,
                },
            )
    return {}


@app.route("/livetrack", methods=["GET", "POST"])
def livetrack():
    app.logger.info(f"rh: {request.headers=}")
    return render_template("genqrcode.html", config="blahfasel")
    # if request.method == "GET":
    #     return render_template("livetrack.html")
    # if request.method == "POST":

#  <img src="{{ qrcode(config,error_correction='H', back_color='white', fill_color='red') }}">

"""
Serve root index file
"""


@app.route("/")
def index():
    return render_template("index.html")


"""
Decorator for connect
"""


@socketio.on("connect")
def connect():
    global thread
    app.logger.info(f"Client connected: {request.sid=}")
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


@socketio.on_error_default
def default_error_handler(e):
    app.logger.error(
        f"on_error_default: {request.event['message']}"
    )  # "my error event"
    app.logger.error(f"on_error_default: {request.event['args']}")  # (data,)


"""
Decorator for disconnect
"""


@socketio.on("disconnect")
def disconnect():
    app.logger.error(f"Client disconnected: {request.sid=}")


if __name__ == "__main__":
    socketio.run(app)
