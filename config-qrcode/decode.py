from pyzbar.pyzbar import decode
from PIL import Image
import pyzstd
import base64
import json
import sys


"""
decode images of sensorlogger qrcodes
example: python decode.py screenshot.jpg 
"""

prefix = b"sensorlogger://config/"

for img in sys.argv[1:]:
    q = decode(Image.open(img))
    s = q[0].data
    cf = s[len(prefix) :]
    d = base64.b64decode(cf)
    cfg = pyzstd.decompress(d)
    js = json.loads(cfg)
    print(json.dumps(js, indent=4))
