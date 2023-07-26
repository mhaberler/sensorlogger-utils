import datetime
import json
import re

# Directory where we write our geojson-data
# dataDir = '/home/<YOUR PATH>/mysite/static/gps/' XXX DELETE tHIS LINE

# Number of points in curves with recent history.
# The number of points should match the update frequency of your GPS logger.
# In my case, I use an app that logs approximately every 30 seconds, so this
# would be about 20 minutes
historyPoints = 40

def findIndex(lst, key, value):
    """ Finds the dictionary item in list where dict['properties']['key'] match the
    provided value. Used to find the geojson object with matching ID

    Cortesy of
    http://stackoverflow.com/questions/4391697/find-the-index-of-a-dict-within-a-list-by-matching-the-dicts-value
    """

    for i, dic in enumerate(lst):
        if dic['properties'][key] == value:
            return i
    return -1

def readGeoJson( filename, id):
    """ Reads GeoJson with featureCollection from file, finds the matching ID within
    that collection and returns both the (geo)JSON object and the index to said ID
    """

    with open(filename) as data_file:
        gjdata = json.load(data_file)

    idx = -1
    # Find index of feature matching ID
    idx = findIndex( gjdata['features'], 'id', id)

    return (gjdata, idx)

def emptyGeoJson( filename):
    """Removes data from GeoJSON file; writes an empty featureCollection
    """

    filename = dataDir + filename
    with open(filename) as data_file:
        gjdata = json.load(data_file)

    gjdata['features'] = []

    with open(filename, "w") as outfile:
        json.dump(gjdata, outfile)


def loggGps(lat, lon, name, dataDir):
    """Main function. Basic sanity check of lat, lon (numeric, within
    geophysical possible range) and name (alphanumeric characters only)

    Valid lat,lon values are logged to appropriate GeoJSON
    files, with file names and ID determined by name parameter. We keep separate
    files for the last valid data point and the track of newest 'historyPoints'
    coordinates.

    Also loggs any requests, including invalid lat-lon pairs, to file
    """

    loggfil  = dataDir + 'gpslogg.txt'          # Log file

    # File names of FeatureCollections containing ALL valid data
    gpspunkt = dataDir + 'gpspunkt.geojson'     # last valid data point
    gpskurve = dataDir + 'gpskurve.geojson'     # curve with newest data points

    # This is javascript-friendly formatted date string
    tid = datetime.datetime.now().strftime("%a %b %d %Y %H:%M:%S") + ' GMT+0000'

    # Logg all incoming requests to file
    with open(loggfil ,'a') as outfile:
        outfile.write(tid + "\t" + str(lon)+ "\t" + str(lat)+ "\t" + name + "\n")

    # Sanity check
    if not name or not lat or not lon:
        return "NOT OK - one or more parameters missing!"
    try:
        lon = float(str(lon))
        lat = float(str(lat))
    except ValueError:
        return "lon, lat not recognized as numeric values"

    # Sanity check of lat, lon values
    if not -90 < lat < 90:
        return "latitude outside accepted range"
    if not -180 < lon < 180:
        return "longitude outside accepted range"

    # Stripping "name" for anything not alphanumeric!
    name2 = re.sub( '\W+', '', name)
    if name2 != name:
        return "Non alphanumeric characters not accepted in name!"

    # Template for GeoJson feature
    pointdata = {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [float(str(lon)), float(str(lat))]
      },
      "properties": {
        "id": str(name),
        "time" : tid
      }
    }

    # (over)writing single feature to file determined by name parameter
    with open(dataDir + name + '.geojson' ,'w') as outfile:
        json.dump(pointdata, outfile)

    # Adding point to featureCollection of points
    # If there exist a feature with correct ID in this collection we replace it
    # If not we append to it.
    gjdata, idx = readGeoJson( gpspunkt, name )
    if idx >= 0:
        gjdata['features'][idx] = pointdata

    else:
        gjdata['features'].append( pointdata)

    with open(gpspunkt, "w") as outfile:
        json.dump(gjdata, outfile)

    # Appending new point to the LineString-feature found in featureCollection
    # of LineString's If no matching ID is found in collection we will append
    # a new LineString-feature to it.
    gjdata, idx = readGeoJson( gpskurve, name)
    if idx >= 0:
        gjdata['features'][idx]['geometry']['coordinates'].append(
                                [float(str(lon)), float(str(lat))]
                            )

        # Removing ancient history
        gjdata['features'][idx]['geometry']['coordinates'] = \
            gjdata['features'][idx]['geometry']['coordinates'][-historyPoints:]

        # Updating timestamp
        gjdata['features'][idx]['properties']['time'] = tid

        newCurve = gjdata['features'][idx]

    else:
    # Creating a new lineString feature.
        newCurve = pointdata
        newCurve['geometry']['type'] = "LineString"
        pos = newCurve['geometry']['coordinates']
        # To have a valid lineString we repeat coordinates
        newCurve['geometry']['coordinates'] = [ pos, pos]
        gjdata['features'].append( newCurve)

    with open(gpskurve, "w") as outfile:
        json.dump(gjdata, outfile)

    # (over)writes track with recent history to file whose name is derived
    # from name parameter
    newCurve['geometry']['coordinates'] = \
                            newCurve['geometry']['coordinates'][-historyPoints:]
    with open( dataDir + name + '_kurve.geojson' ,'w') as outfile:
        json.dump(newCurve, outfile)

    # Return to caller.
    return( 'ok' )


if __name__=="__main__":
    loggGps('63.5', '11.0', 'konsoll2')
    # loggGps('19.9', '5.5', 'test')

#    dataDir = 'Directory where we write our geojson-data'
#    emptyGeoJson( dataDir + 'gpspunkt.geojson' )
#    emptyGeoJson( dataDir + 'gpskurve.geojson' )
