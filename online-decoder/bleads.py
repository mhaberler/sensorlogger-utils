from uttlv import TLV

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

# types and tags for BLE advertisement data which is LTV
bleAdvConfig = {
    BLE_HS_ADV_TYPE_FLAGS: {TLV.Config.Type: bytes, TLV.Config.Name: "FLAGS"},
    BLE_HS_ADV_TYPE_INCOMP_UUIDS16: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "INCOMP_UUIDS16",
    },
    BLE_HS_ADV_TYPE_COMP_UUIDS16: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "COMP_UUIDS16",
    },
    BLE_HS_ADV_TYPE_INCOMP_UUIDS32: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "INCOMP_UUIDS32",
    },
    BLE_HS_ADV_TYPE_COMP_UUIDS32: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "COMP_UUIDS32",
    },
    BLE_HS_ADV_TYPE_INCOMP_UUIDS128: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "INCOMP_UUIDS128",
    },
    BLE_HS_ADV_TYPE_COMP_UUIDS128: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "COMP_UUIDS128",
    },
    BLE_HS_ADV_TYPE_INCOMP_NAME: {TLV.Config.Type: str, TLV.Config.Name: "INCOMP_NAME"},
    BLE_HS_ADV_TYPE_COMP_NAME: {TLV.Config.Type: str, TLV.Config.Name: "COMP_NAME"},
    BLE_HS_ADV_TYPE_TX_PWR_LVL: {TLV.Config.Type: bytes, TLV.Config.Name: "TX_PWR_LVL"},
    BLE_HS_ADV_TYPE_SLAVE_ITVL_RANGE: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "SLAVE_ITVL_RANGE",
    },
    BLE_HS_ADV_TYPE_SOL_UUIDS16: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "SOL_UUIDS16",
    },
    BLE_HS_ADV_TYPE_SOL_UUIDS128: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "SOL_UUIDS128",
    },
    BLE_HS_ADV_TYPE_SVC_DATA_UUID16: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "SVC_DATA_UUID16",
    },
    BLE_HS_ADV_TYPE_PUBLIC_TGT_ADDR: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "PUBLIC_TGT_ADDR",
    },
    BLE_HS_ADV_TYPE_RANDOM_TGT_ADDR: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "RANDOM_TGT_ADDR",
    },
    BLE_HS_ADV_TYPE_APPEARANCE: {TLV.Config.Type: bytes, TLV.Config.Name: "APPEARANCE"},
    BLE_HS_ADV_TYPE_ADV_ITVL: {TLV.Config.Type: bytes, TLV.Config.Name: "ADV_ITVL"},
    BLE_HS_ADV_TYPE_SVC_DATA_UUID32: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "SVC_DATA_UUID32",
    },
    BLE_HS_ADV_TYPE_SVC_DATA_UUID128: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "SVC_DATA_UUID128",
    },
    BLE_HS_ADV_TYPE_URI: {TLV.Config.Type: str, TLV.Config.Name: "URI"},
    BLE_HS_ADV_TYPE_MESH_PROV: {TLV.Config.Type: bytes, TLV.Config.Name: "MESH_PROV"},
    BLE_HS_ADV_TYPE_MESH_MESSAGE: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "MESH_MESSAGE",
    },
    BLE_HS_ADV_TYPE_MESH_BEACON: {
        TLV.Config.Type: bytes,
        TLV.Config.Name: "MESH_BEACON",
    },
    BLE_HS_ADV_TYPE_MFG_DATA: {TLV.Config.Type: bytes, TLV.Config.Name: "MFG_DATA"},
}
