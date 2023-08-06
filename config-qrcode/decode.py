from pyzbar.pyzbar import decode
from PIL import Image
import pyzstd
import base64
import json
import sys
import os


"""
decode qr code image or config code
examples: 
    python decode.py screenshot.jpg 
    python decode.py sensorlogger://config/KLUv/WBYAdUJAJbTQSYQ6boBJkxTklxLtrkYycVCBZsDL22CxQUtaS/OlmWzmiICAAA4EDIANQA6AE0d687Oa73TYPh5f3PWe+s5KYZfFEVSd5dhe/6RLb1VZO1q6ctpIbwQuV++gdtb+/JCAXGSpid6DtIzISQIipE397p/jeF3b9fXMNQT3v+WjlSrddYnld6cVHSeaqTLxHfFSIvh9zUIEQWNzHQILgHM5HQMk8kAt8l2jlw7YzPtPcnQUu+INl9WGLLF0AiHdzFM+xuOg5rY6d6CA7RdKJKiHy+qLKMsCcagQCgFBqFU1iOrMmoBUFnURWlcj4UEU1QSjtycvLjam/Bw5JecW0Zv9MLw40t1sOECEQABzojbShMCbTXbSkxQD83xEYgxQ2Yfr8NXfOjCI4M/tE+LlQIUnUQ1DEwOfS14

"""

prefix = b"sensorlogger://config/"

for arg in sys.argv[1:]:
    if os.path.isfile(arg):
        q = decode(Image.open(arg))
        s = q[0].data
    else:
        s = arg
    cf = s[len(prefix) :]
    d = base64.b64decode(cf)
    cfg = pyzstd.decompress(d)
    js = json.loads(cfg)
    print(json.dumps(js, indent=4))
