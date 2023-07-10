import sys
import struct

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def b2mac(adr):
   return "%X:%X:%X:%X:%X:%X" % struct.unpack("BBBBBB",adr)

def Decoder(args, debug):
    if 'servicedatauuid' in args:
        if 'fbb0' in args['servicedatauuid']:
            if args['manufacturerdata'].startswith('0001'):
                if debug:
                    eprint(f"found TPMS with hijacked TomTom MFID: {args}")
                data = bytearray.fromhex(args['manufacturerdata'])
                mfid,adr, pressure, temperature, battery, status = struct.unpack(
            '<H6sIIBB', data)
            return {
                'type': 'tpms0100',
                'mac':  b2mac(adr),
                'pressure': pressure/100000.0,
                'temperature': temperature/100.0,
                'location': adr[0] & 0x7f,
                'batteryLevel': battery,
                'status': status
            }
            if args['manufacturerdata'].startswith('AC00'):
                eprint(f"found TPMS with hijacked Green Throttle Games MFID: {args}")

        if '4faf' in args['servicedatauuid'] and args['manufacturerdata'].startswith('1147'):
            if debug:
                eprint(f"found FlowSensor {args}")
            data = bytearray.fromhex(args['manufacturerdata'])
            # see https://github.com/mhaberler/flowsensor/blob/main/src/defs.h#L33-L42
            mfid, adr, count, last_change, rate, batteryLevel, flags = struct.unpack('<H6siIhbb', data)
            return {
                'type': 'customFLowSensor',
                'brand': 'Haberler',
                'mac':  b2mac(adr),
                'mfid': mfid,
                'count': count,
                'last_change': last_change,
                'rate': rate,
                'batteryLevel': batteryLevel,
                'flags': flags
            }
    return None
