#! /usr/bin/python3

import socket
from datetime import datetime
from lib.exceptions import WrongValue
from lib.constants import *
from lib.functions import *

DEBUG = False

HOST = "10.254.0.41"
PORT = 179

MY_AS = 65500
MY_HOLDTIME = 90
MY_BGP_ID = bytes([10, 0, 0, 10])


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


def decode_open_message(data_msg_remaining):
    result = {"text": []}
    result["text"].append("Open message: version {}".format(data_msg_remaining[0]))
    result["text"].append("  AS {}".format(get_word(data_msg_remaining[1:3])))
    result["text"].append("  Hold time {}".format(get_word(data_msg_remaining[3:5])))
    result["text"].append("  BGP ID {}.{}.{}.{}".format(*data_msg_remaining[5:9]))
    return result
    # TODO: add other fields to result, not just text


def decode_notification_message(data_msg_remaining):
    result = {"text": []}
    err_code = data_msg_remaining[0]
    err_subcode = data_msg_remaining[1]
    result["text"].append("Notification message: code {}, subcode {}".format(err_code, err_subcode))
    return result


def decode_nlri_data(nlri_data):
    result = {"text": []}
    pos = 0
    while pos < len(nlri_data):
        prefix_len = nlri_data[pos]
        pr_from = pos + 1
        pr_to = pr_from + (prefix_len // 8) + (1 if prefix_len % 8 != 0 else 0)
        prefix = nlri_data[pr_from:pr_to]
        result["text"].append("    {}/{}".format(".".join([str(i) for i in prefix]), prefix_len))
        pos = pr_to
    return result


def decode_update_message(data_msg_remaining):
    result = {"text": []}
    withdrawn_len = get_word(data_msg_remaining[0:2])
    if withdrawn_len > 0:
        withdrawn_routes_data = data_msg_remaining[2:withdrawn_len + 2]
        result["text"].append("  Withdrawn Routes:")
        result["text"] += decode_nlri_data(withdrawn_routes_data)["text"]
    tot_path_attr_len = get_word(data_msg_remaining[withdrawn_len + 2:withdrawn_len + 4])
    nlri_data = data_msg_remaining[withdrawn_len + tot_path_attr_len + 4:]
    if len(nlri_data) > 0:
        result["text"].append("  NLRI in update:")
        result["text"] += decode_nlri_data(nlri_data)["text"]
    return result


def dump_bgp_message(message):
    print(datetime.now(), " Received BGP message:")
    msg_length = message["length"]
    print("  Message length: ", msg_length)
    msg_type = message["type"]
    print("  Message type: {} ({})".format(msg_type, MSG_TYPE_NAMES[msg_type]))

    data_msg_remaining = message["remainder"]
    if msg_type == MSG_TYPE_OPEN:
        print_str_list(decode_open_message(data_msg_remaining)["text"])
    elif msg_type == MSG_TYPE_NOTIFICATION:
        print_str_list(decode_notification_message(data_msg_remaining)["text"])
    elif msg_type == MSG_TYPE_UPDATE:
        print_str_list(decode_update_message(data_msg_remaining)["text"])


def keepalive_message():
    return (BGP_HEADER_MARKER +
                      two_bytes(16 + 2 + 1) +   # Keepalive message length
                      byte(MSG_TYPE_KEEPALIVE))


def open_message(AS, holdtime, bgp_id):
    return (BGP_HEADER_MARKER +
                      two_bytes(29) +           # Open message length when no optional parameters are provided
                      byte(MSG_TYPE_OPEN) +     # Type 1 = Open
                      byte(BGP_VERSION) +       # Version
                      two_bytes(AS) +           # My Autonomous System
                      two_bytes(holdtime) +     # Hold Time
                      bgp_id +                  # BGP Identifier
                      byte(0))                  # Opt Parm Len

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        sent = s.send(open_message(MY_AS, MY_HOLDTIME, MY_BGP_ID))
        print("Sent {} bytes in Open message".format(sent))

        sent = s.send(keepalive_message())
        print("Sent {} bytes in Keepalive message".format(sent))

        while True:
            message = read_message_from_bgp_socket(s)
            dump_bgp_message(message)
            if message["type"] == MSG_TYPE_NOTIFICATION:
                break
            elif message["type"] == MSG_TYPE_KEEPALIVE:
                sent = s.send(keepalive_message())
                print("Sent {} bytes in Keepalive message".format(sent))

