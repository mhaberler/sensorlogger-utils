from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime
# from flask_cors import CORS


"""
Background Thread
"""
thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'donsky!'

# CORS(app)

socketio = SocketIO(app, cors_allowed_origins='*')
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
        socketio.emit('updateSensorData', {'value': dummy_sensor_value, "date": get_current_datetime()})
        socketio.sleep(1)

"""
Serve root index file
"""
@app.route('/')
def index():
    return render_template('index.html')

"""
Decorator for connect
"""
@socketio.on('connect')
def connect():
    global thread
    app.logger.info(f"Client connected: {request.sid=}")
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

@socketio.on_error_default
def default_error_handler(e):
    app.logger.error(f"on_error_default: {request.event['message']}") # "my error event"
    app.logger.error(f"on_error_default: {request.event['args']}") # (data,)


"""
Decorator for disconnect
"""
@socketio.on('disconnect')
def disconnect():
    app.logger.error(f"Client disconnected: {request.sid=}")

if __name__ == '__main__':
    socketio.run(app)