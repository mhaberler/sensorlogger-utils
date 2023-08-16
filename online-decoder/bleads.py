# https://github.com/h2zero/NimBLE-Arduino/blob/bc333ccb6e8d9ff2059af9cbd5006a290a4de3a5/src/nimble/nimble/host/include/host/ble_hs_adv.h#L108

BLE_HS_ADV_TYPE_FLAGS = 0x01
BLE_HS_ADV_TYPE_INCOMP_UUIDS16 = 0x02
BLE_HS_ADV_TYPE_COMP_UUIDS16 = 0x03
BLE_HS_ADV_TYPE_INCOMP_UUIDS32 = 0x04
BLE_HS_ADV_TYPE_COMP_UUIDS32 = 0x05
BLE_HS_ADV_TYPE_INCOMP_UUIDS128 = 0x06
BLE_HS_ADV_TYPE_COMP_UUIDS128 = 0x07
BLE_HS_ADV_TYPE_INCOMP_NAME = 0x08
BLE_HS_ADV_TYPE_COMP_NAME = 0x09
BLE_HS_ADV_TYPE_TX_PWR_LVL = 0x0A
BLE_HS_ADV_TYPE_SLAVE_ITVL_RANGE = 0x12
BLE_HS_ADV_TYPE_SOL_UUIDS16 = 0x14
BLE_HS_ADV_TYPE_SOL_UUIDS128 = 0x15
BLE_HS_ADV_TYPE_SVC_DATA_UUID16 = 0x16
BLE_HS_ADV_TYPE_PUBLIC_TGT_ADDR = 0x17
BLE_HS_ADV_TYPE_RANDOM_TGT_ADDR = 0x18
BLE_HS_ADV_TYPE_APPEARANCE = 0x19
BLE_HS_ADV_TYPE_ADV_ITVL = 0x1A
BLE_HS_ADV_TYPE_SVC_DATA_UUID32 = 0x20
BLE_HS_ADV_TYPE_SVC_DATA_UUID128 = 0x21
BLE_HS_ADV_TYPE_URI = 0x24
BLE_HS_ADV_TYPE_MESH_PROV = 0x29
BLE_HS_ADV_TYPE_MESH_MESSAGE = 0x2A
BLE_HS_ADV_TYPE_MESH_BEACON = 0x2B
BLE_HS_ADV_TYPE_MFG_DATA = 0xFF

def toString(s):
    return s.decode("utf-8")

def serviceData(s):
    return s.hex()


# types and tags for BLE advertisement data which is LTV
bleAdvConfig = {
    BLE_HS_ADV_TYPE_FLAGS: {"type": bytes, "name": "FLAGS"},
    BLE_HS_ADV_TYPE_INCOMP_UUIDS16: {
        "type": serviceData,
        "name": "INCOMP_UUIDS16",
    },
    BLE_HS_ADV_TYPE_COMP_UUIDS16: {
        "type": serviceData,
        "name": "COMP_UUIDS16",
    },
    BLE_HS_ADV_TYPE_INCOMP_UUIDS32: {
        "type": serviceData,
        "name": "INCOMP_UUIDS32",
    },
    BLE_HS_ADV_TYPE_COMP_UUIDS32: {
        "type": serviceData,
        "name": "COMP_UUIDS32",
    },
    BLE_HS_ADV_TYPE_INCOMP_UUIDS128: {
        "type": serviceData,
        "name": "INCOMP_UUIDS128",
    },
    BLE_HS_ADV_TYPE_COMP_UUIDS128: {
        "type": serviceData,
        "name": "COMP_UUIDS128",
    },
    BLE_HS_ADV_TYPE_INCOMP_NAME: {"type": toString, "name": "INCOMP_NAME"},
    BLE_HS_ADV_TYPE_COMP_NAME: {"type": toString, "name": "COMP_NAME"},
    BLE_HS_ADV_TYPE_TX_PWR_LVL: {"type": bytes, "name": "TX_PWR_LVL"},
    BLE_HS_ADV_TYPE_SLAVE_ITVL_RANGE: {
        "type": bytes,
        "name": "SLAVE_ITVL_RANGE",
    },
    BLE_HS_ADV_TYPE_SOL_UUIDS16: {
        "type": serviceData,
        "name": "SOL_UUIDS16",
    },
    BLE_HS_ADV_TYPE_SOL_UUIDS128: {
        "type": serviceData,
        "name": "SOL_UUIDS128",
    },
    BLE_HS_ADV_TYPE_SVC_DATA_UUID16: {
        "type": bytes,
        "name": "SVC_DATA_UUID16",
    },
    BLE_HS_ADV_TYPE_PUBLIC_TGT_ADDR: {
        "type": bytes,
        "name": "PUBLIC_TGT_ADDR",
    },
    BLE_HS_ADV_TYPE_RANDOM_TGT_ADDR: {
        "type": bytes,
        "name": "RANDOM_TGT_ADDR",
    },
    BLE_HS_ADV_TYPE_APPEARANCE: {"type": bytes, "name": "APPEARANCE"},
    BLE_HS_ADV_TYPE_ADV_ITVL: {"type": bytes, "name": "ADV_ITVL"},
    BLE_HS_ADV_TYPE_SVC_DATA_UUID32: {
        "type": serviceData,
        "name": "SVC_DATA_UUID32",
    },
    BLE_HS_ADV_TYPE_SVC_DATA_UUID128: {
        "type": serviceData,
        "name": "SVC_DATA_UUID128",
    },
    BLE_HS_ADV_TYPE_URI: {"type": str, "name": "URI"},
    BLE_HS_ADV_TYPE_MESH_PROV: {"type": bytes, "name": "MESH_PROV"},
    BLE_HS_ADV_TYPE_MESH_MESSAGE: {
        "type": serviceData,
        "name": "MESH_MESSAGE",
    },
    BLE_HS_ADV_TYPE_MESH_BEACON: {
        "type": serviceData,
        "name": "MESH_BEACON",
    },
    BLE_HS_ADV_TYPE_MFG_DATA: {"type": bytes, "name": "MFG_DATA"},
}

def decode_advertisement(hexbuffer):
    b = bytearray.fromhex(hexbuffer)
    size = len(b)
    i = 0
    result = {}
    while i < size:
        l = int.from_bytes(b[i : i + 1])-1
        type = int.from_bytes(b[i + 1 : i + 2])
        value = b[i + 2 : i + 2 + l]
        d = bleAdvConfig.get(type, None)
        if d:
            result[d["name"]] = d["type"](value)
        else:
            raise Exception(f"invalid {type=} {i=} {hexbuffer=}")
        i += l + 2
    return result


if __name__ == "__main__":
    r = decode_advertisement(
        "0201061bff99040511b0854affff01b403980024739632ac57dd79c68fbda211079ecadc240ee5a9e093f3a3b50100406e0b0952757576692042444132"
    )
    print(r)
