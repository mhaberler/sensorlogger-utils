from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime
import json
from flask_qrcode import QRcode
import shortuuid

# from flask_cors import CORS
from TheengsDecoder import decodeBLE
from slconfig import genconfig


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


@app.route("/trackme/<clientsession>/")
def trackme(clientsession=""):
    app.logger.info(f"trackme {clientsession=}")
    return render_template("leaflet.html", clientsession=clientsession)


@app.route("/sl/<clientsession>/", methods=["GET", "POST"])
def getpos(clientsession=""):
    # if clientsession not in clientsessions:
    #     abort(401)
    #     pass
    body = json.loads(request.data)
    messageId = body["messageId"]
    sessionId = body["sessionId"]
    deviceId = body["deviceId"]
    for p in body["payload"]:
        if p.get("name", None) == "location":
            socketio.emit("updateLocation", p)

        if p.get("name", None) == "test":
            app.logger.info(
                f"client hit test: {clientsession=} {messageId=} {sessionId=} {deviceId=}"
            )

    return {}


@app.route("/livetrack", methods=["GET", "POST"])
def livetrack():
    clientsession = shortuuid.uuid()
    secret = shortuuid.uuid()
    authToken = f"realm={secret}"
    uri = f"{request.host_url}sl/{clientsession}"
    config = genconfig(uri, authToken=authToken)
    app.logger.info(f"generate config: {clientsession=} {secret=} {config=}")
    return render_template(
        "genqrcode.html", config=config, tracker=f"/trackme/{clientsession}/"
    )


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
