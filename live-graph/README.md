# live-graph

Simple live sensor graph with Flask and SocketIO

## Getting Started

### Install Python pacakages

```bash
$ pip install -r requirements.txt
```

### Run server

```bash
$ python server.py
```

Open `localhost:8000` and click the **start** button

#### Try it out

```bash
$ python client_test.py
```


## notes
https://stackoverflow.com/questions/71850969/importerror-cannot-import-name-run-with-reloader-from-werkzeug-serving

Flask-SocketIO==4.3.1
python-engineio==3.13.2
python-socketio==4.6.0
Flask==2.0.3
Werkzeug==2.0.3