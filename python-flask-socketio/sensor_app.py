from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from random import random
from threading import Lock, Thread

from datetime import datetime
import json
from flask_qrcode import QRcode
import shortuuid

# from celery import Celery
import socket, select, queue
import time

# from flask_cors import CORS
from TheengsDecoder import decodeBLE
from slconfig import genconfig

# from flask_sock import Sock


"""
Background Thread
"""
thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = "donsky!"
app.config["SOCK_SERVER_OPTIONS"] = {"ping_interval": 25}

QRcode(app)

socketio = SocketIO()
socketio.init_app(app)

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

socket_queue = queue.Queue()
web_socket = None
udp_socket = None


def udp_thread():
    global udp_socket
    if udp_socket:
        app.logger.error(f"udp_socket already openend ")
        return

    app.logger.info(f"udp_thread")

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
    udp_socket.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = udp_socket.recvfrom(1024)  # buffer size is 1024 bytes
        # if web_socket:
        #     web_socket.writ

        emit("chat", {"message": message, "username": username}, broadcast=True)

        socket_queue.put(data.decode() + "\n")
        print("received message:", data)


# CORS(app)


# - ws.send(data)
# - ws.receive(timeout=None)
# - ws.close(reason=None, message=None)
# @socketio.route("/tpws")
# def tpws(sock):
#     global web_socket
#     web_socket = sock
#     while True:
#         # print i, i.recvfrom(131072)
#         data = sock.receive()

#         app.logger.info(f"ws:  {data=}")

users = {}


@socketio.on("connect")
def handle_connect():
    print("Client connected!")


@socketio.on("user_join")
def handle_user_join(username):
    print(f"User {username} joined!")
    users[username] = request.sid


@socketio.on("new_message")
def handle_new_message(message):
    print(f"New message: {message}")
    username = None
    for user in users:
        if users[user] == request.sid:
            username = user
    emit("chat", {"message": message, "username": username}, broadcast=True)


# @app.route("/echotest")
# def echotest():
#     return render_template("echotest.html")


@app.route("/tp")
def teleplot():
    # listen_to_udp.delay()
    # print(socket_queue.get())
    # udp_thread()
    return render_template("teleplot.html")


def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")


"""
Generate random sequence of dummy sensor values and send it to our clients
"""


# def udp_thread():
#     app.logger.info(f"Generating random sensor values")
#     while True:
#         # dummy_sensor_value = round(random() * 100, 3)
#         # socketio.emit(
#         #     "updateSensorData",
#         #     {"value": dummy_sensor_value, "date": get_current_datetime()},
#         # )
#         # socketio.sleep(1)
#         pass


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
            # socketio.emit("updateLocation", p)
            pass
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


@app.route("/uplot")
def uplot():
    app.logger.info(f"uplot")
    return render_template("stream-data.html")


"""
Serve root index file
"""


@app.route("/")
def index():
    return render_template("index.html")


"""
Decorator for connect
"""


# @socketio.on("connect")
# def connect():
#     global thread
#     app.logger.info(f"Client connected: {request.sid=}")
#     global thread
#     with thread_lock:
#         if thread is None:
#             thread = socketio.start_background_task(udp_thread)


# @socketio.on_error_default
# def default_error_handler(e):
#     app.logger.error(
#         f"on_error_default: {request.event['message']}"
#     )  # "my error event"
#     app.logger.error(f"on_error_default: {request.event['args']}")  # (data,)


"""
Decorator for disconnect
"""


# @socketio.on("disconnect")
# def disconnect():
#     app.logger.error(f"Client disconnected: {request.sid=}")


# if __name__ == "__main__":
# thread = Thread(target=udp_thread)
# thread.daemon = True
# thread.start()

# if __name__ == "__main__":
#     socketio.run(app)
