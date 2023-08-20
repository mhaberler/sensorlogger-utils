import re

RE_INT = re.compile(r"^[-+]?([1-9]\d*|0)$")
RE_FLOAT = re.compile(r"^[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?$")


def allowed_file(filename, extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in extensions


def make_numeric(value):
    if isinstance(value, bytes):
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    if RE_INT.match(value):
        return int(value)
    if RE_FLOAT.match(value):
        return float(value)
    return None
