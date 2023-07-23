import gpxpy
from datetime import datetime
import pytz
import logging
from simplify import Simplify3D

highestQuality = True


def stringify(d):
    text = ""
    for k, v in d.items():
        text += f"{k}: {v}, "
    return text.rstrip(", ")


def gengpx(j, gpx_fn="sensorlogger", description="", tolerance=0.0):
    gpx = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    points = []
    metadata = {}
    for row in j:
        if row["sensor"] == "Metadata":
            metadata = row
        if row["sensor"] == "Location":
            secs = float(row["time"]) * 1e-9
            t = datetime.utcfromtimestamp(secs).replace(tzinfo=pytz.utc)
            points.append(
                [
                    row["longitude"],
                    row["latitude"],
                    row["altitude"],
                    t,
                    row["horizontalAccuracy"],
                    row["verticalAccuracy"],
                    row["speed"],
                ]
            )

    pts = points

    if tolerance > 0.0:
        s = Simplify3D()
        pts = s.simplify(
            points,
            tolerance=tolerance,
            highestQuality=highestQuality,
            returnMarkers=False,
        )
        logging.debug(
            f"simplify3d: {len(points)} -> {len(pts)} points with {tolerance=}"
        )

    for p in pts:
        (lat, lon, ele, dt, hdop, vdop, speed) = p
        pt = gpxpy.gpx.GPXTrackPoint(
            lon,
            lat,
            elevation=round(float(ele),2),
            time=dt,
            speed=round(float(speed),2),
            horizontal_dilution=round(float(hdop),2),
            vertical_dilution=round(float(vdop),2)
        )
        gpx_segment.points.append(pt)

    gpx.refresh_bounds()
    gpx.creator = f"Sensor Logger, app version {metadata['appVersion']}"
    metadata.pop("sensor", None)
    gpx.author_name = stringify(metadata)
    gpx.description = description
    gpx_track.name = metadata["device name"] + " " + metadata["recording time"]

    return gpx.to_xml(version="1.0").encode("utf-8")
