#! /usr/bin/python3

import socket

HOST = "10.254.0.41"
PORT = 179

MY_AS = 65500
MY_HOLDTIME = 90

# Example what we received without sending anything:
# b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff  \x00\x1d  \x01  \x04\xfd\xe8\x00Z\n\x00\x00\x01\x00
#   \xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff  \x00\x15  \x03  \x04\x00'

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


class WrongValue(Exception):
    pass


def read_message_from_bgp_socket(s):
    data_msg_header = s.recv(BGP_HEADER_LENGTH)
    print("Received raw: ", repr(data_msg_header))
    msg_length = data_msg_header[16] * 256 + data_msg_header[17]
    print("Message length: ", msg_length)
    msg_type = data_msg_header[18]
    print("Message type: {} ({})".format(msg_type, MSG_TYPE_NAMES[msg_type]))
    if msg_length > BGP_HEADER_LENGTH:
        data_msg_remaining = s.recv(msg_length - BGP_HEADER_LENGTH)
        print("Received raw, remainder: ", repr(data_msg_remaining))
        if msg_type == 1:
            print("Open message: version {}".format(data_msg_remaining[0]))
            print("  AS {}".format(data_msg_remaining[1]*256 + data_msg_remaining[2]))
            print("  Hold time {}".format(data_msg_remaining[3] * 256 + data_msg_remaining[4]))
            print("  BGP ID {}.{}.{}.{}".format(*data_msg_remaining[5:9]))
        elif msg_type == 3:
            err_code = data_msg_remaining[0]
            err_subcode = data_msg_remaining[1]
            print("Notification message: code {}, subcode {}".format(err_code, err_subcode))
    return msg_type

BGP_HEADER_MARKER = b'\xff' * 16


def byte(b):
    if b < 0 or b > 255:
        raise WrongValue
    return bytes([b])


def two_bytes(w):
    if w < 0 or w > 65535:
        raise WrongValue
    return bytes([w // 256, w % 256])


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        sent = s.send(BGP_HEADER_MARKER +
                      two_bytes(29) +           # Open message length when no optional parameters are provided
                      byte(MSG_TYPE_OPEN) +
                      byte(BGP_VERSION) +       # Version
                      two_bytes(MY_AS) +        # My Autonomous System
                      two_bytes(MY_HOLDTIME) +  # Hold Time
                      bytes([10, 0, 0, 10]) +   # BGP Identifier
                      byte(0))                  # Opt Parm Len
        print("Sent {} bytes".format(sent))

        sent = s.send(BGP_HEADER_MARKER +
                      two_bytes(19) +           # Keepalive message length
                      byte(MSG_TYPE_KEEPALIVE))
        print("Sent {} bytes".format(sent))

        while read_message_from_bgp_socket(s) != MSG_TYPE_NOTIFICATION:
            pass




