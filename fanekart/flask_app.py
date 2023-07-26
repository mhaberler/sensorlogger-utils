
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, url_for, render_template, make_response, abort
import loggGps

# Directory where we write (and read!) our geojson-data
# dataDir = '/home/<yourPAusername>/fanekart/gpsdata/'
dataDir = '/Users/mah/Ballon/src/sensorlogger-utils/fanekart/gpsdata/'


mySecretGpsKeys = [ 'uniqueAndSecret123', 'topsecret' ]


app = Flask(__name__)
app.secret_key = 'This is really unique and secret'

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/getfile/<filename>')
def getFile(filename):
    filename = dataDir + filename

    try:
        with open( filename) as file:
            blob = file.read()
    except:
        abort(404)
        pass

    r = make_response(blob)
    r.mimetype='application/json'
    r.headers['Access-Control-Allow-Origin'] = '*'

    return r

@app.route('/gpspos/<gpsId>/<secretGpsKey>/')
def getpos(gpsId='', secretGpsKey=''):
    if secretGpsKey not in mySecretGpsKeys:
        abort(401)
        pass

    lat = request.args.get('lat', '')
    lon = request.args.get('lon', '')

    ok = loggGps.loggGps( str(lat), str(lon), str(gpsId), dataDir)

    return( ok + "<br>gps ID" + str(gpsId) + "<br>\n" +
            'lat' + str(lat) + "<br>\n" +
            "lon" + str(lon) )
