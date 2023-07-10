import click
import json
import struct
from TheengsDecoder import decodeBLE as dble
from TheengsDecoder import getProperties, getAttribute

@click.command()
@click.option('--debug/--no-debug', default=False)
@click.argument('input', type=click.File('r'), default='-', nargs=1)
@click.argument('output', type=click.File('w'), default='-', nargs=1)

def cli(debug, input, output):
    """decode BLE announcements in a sensorlogger JSON log
    """
    if debug:
        print("debug == True")
    print("hello mah")

