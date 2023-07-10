import click
import json
from TheengsDecoder import decodeBLE
from TheengsDecoder import getProperties, getAttribute

@click.command()
@click.option('--debug/--no-debug', default=False)
@click.argument('input', type=click.File('r'), default='-', nargs=1)
@click.argument('output', type=click.File('w'), default='-', nargs=1)

def cli(debug, input, output):
    """decode BLE announcements in a sensorlogger JSON log
    """
    j = json.load(input)
    for sample in j:
        if sample['sensor'].startswith('Bluetooth'):
            data = {}
            data['name'] = sample['name']
            data['id'] = sample['id']
            try:
               data['servicedatauuid'] = list(sample['serviceUUIDs'])
            except KeyError:
                pass
            data['manufacturerdata'] = sample['manufacturerData']
            # decoder input:
            #  {"manufacturerdata": "24a79a38c1a4", "name": "032240133", "id": "C2034721-D54F-4FE4-A773-1247EB5A28C1", "rssi": -67}
            result = decodeBLE(json.dumps(data))
            if result:
                sample['decoded'] = json.loads(result)
                if debug and sample['decoded']:
                    print(json.dumps(sample, indent=2))

    print(json.dumps(j, indent=2), file=output)