MSG_TYPE_OPEN = 1
MSG_TYPE_UPDATE = 2
MSG_TYPE_NOTIFICATION = 3
MSG_TYPE_KEEPALIVE = 4

MSG_TYPE_NAMES = {
    MSG_TYPE_OPEN: "OPEN",
    MSG_TYPE_UPDATE: "UPDATE",
    MSG_TYPE_NOTIFICATION: "NOTIFICATION",
    MSG_TYPE_KEEPALIVE: "KEEPALIVE"
}

BGP_HEADER_LENGTH = 19
BGP_VERSION = 4

BGP_HEADER_MARKER = b'\xff' * 16