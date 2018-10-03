#! /usr/bin/python3

import socket

DEBUG = True

HOST = "10.254.0.41"
PORT = 179

MY_AS = 65500
MY_HOLDTIME = 90

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


class WrongValue(Exception):
    pass


def get_word(lst):
    if len(lst) != 2:
        raise WrongValue
    return lst[0] * 256 + lst[1]


def read_message_from_bgp_socket(s):
    message = {}

    data_msg_header = s.recv(BGP_HEADER_LENGTH)
    message["header"] = data_msg_header
    if DEBUG: print("Received raw: ", repr(data_msg_header))

    msg_length = get_word(data_msg_header[16:18])
    message["length"] = msg_length
    if DEBUG: print("Message length: ", msg_length)

    msg_type = data_msg_header[18]
    message["type"] = msg_type
    if DEBUG: print("Message type: {} ({})".format(msg_type, MSG_TYPE_NAMES[msg_type]))

    message["remainder"] = None
    if msg_length > BGP_HEADER_LENGTH:
        data_msg_remaining = s.recv(msg_length - BGP_HEADER_LENGTH)
        message["remainder"] = data_msg_remaining
        if DEBUG: print("Received raw, remainder: ", repr(data_msg_remaining))
    return message


def dump_message(message):
    msg_type = message["type"]
    data_msg_remaining = message["remainder"]
    if msg_type == MSG_TYPE_OPEN:
        print("Open message: version {}".format(data_msg_remaining[0]))
        print("  AS {}".format(get_word(data_msg_remaining[1:3])))
        print("  Hold time {}".format(get_word(data_msg_remaining[3:5])))
        print("  BGP ID {}.{}.{}.{}".format(*data_msg_remaining[5:9]))
    elif msg_type == MSG_TYPE_NOTIFICATION:
        err_code = data_msg_remaining[0]
        err_subcode = data_msg_remaining[1]
        print("Notification message: code {}, subcode {}".format(err_code, err_subcode))
    elif msg_type == MSG_TYPE_UPDATE:
        withdrawn_len = get_word(data_msg_remaining[0:2])
        tot_path_attr_len = get_word(data_msg_remaining[withdrawn_len + 2:withdrawn_len + 4])
        nlri_data = data_msg_remaining[withdrawn_len + tot_path_attr_len + 4:]
        pos = 0
        print("NLRI in update:")
        while pos < len(nlri_data):
            prefix_len = nlri_data[pos]
            pr_from = pos + 1
            pr_to = pr_from + (prefix_len // 8) + (1 if prefix_len % 8 != 0 else 0)
            prefix = nlri_data[pr_from:pr_to]
            print("    {}/{}".format(".".join([str(i) for i in prefix]), prefix_len))
            pos = pr_to


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

        while True:
            message = read_message_from_bgp_socket(s)
            if message["type"] == MSG_TYPE_NOTIFICATION:
                break
            dump_message(message)





