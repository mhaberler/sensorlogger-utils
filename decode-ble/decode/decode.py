import click
import json
from TheengsDecoder import decodeBLE
from TheengsDecoder import getProperties, getAttribute
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


try:
    sys.path.append(".")
    import custom
    customDecoder = custom.Decoder

except Exception:
    customDecoder = None


@click.command()
@click.option('--debug/--no-debug', default=False)
@click.option('--custom/--no-custom', default=False)
@click.argument('input', type=click.File('r'), default='-', nargs=1)
@click.argument('output', type=click.File('w'), default='-', nargs=1)
def cli(debug, custom, input, output):
    """decode BLE announcements in a sensorlogger JSON log
    """
    j = json.load(input)
    for sample in j:
        if sample['sensor'].startswith('Bluetooth'):
            data = {}
            data['name'] = sample['name']
            data['id'] = sample['id']
            try:
                # Kelvin fix needed
                # this should be an array
                # data['servicedatauuid'] = list(sample['serviceUUIDs'])
                data['servicedatauuid'] = [sample['serviceUUIDs']]
            except KeyError:
                pass
            data['manufacturerdata'] = sample['manufacturerData']
            result = decodeBLE(json.dumps(data))
            if result:
                js = json.loads(result)
                js.pop("id", None)
                js.pop("mfid", None)
                js.pop("manufacturerdata", None)
                js.pop("servicedatauuid", None)
                sample['decoded'] = js
                if debug and sample['decoded']:
                    print(json.dumps(sample, indent=2))
                continue

            if customDecoder:
                result = customDecoder(data, debug)
                if result:
                    sample['decoded'] = result
                    continue
            eprint(f"failed to decode: {sample}")

    print(json.dumps(j, indent=2), file=output)
