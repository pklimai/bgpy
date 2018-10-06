#! /usr/bin/python3

from lib.constants import *
from lib.functions import *
from lib.bgp_client_session import BGPClientSession
from lib.settings import *


def keepalive_message():
    return (BGP_HEADER_MARKER +
            two_bytes(16 + 2 + 1) +   # Keepalive message length
            byte(MSG_TYPE_KEEPALIVE)
            )


def open_message(AS, holdtime, bgp_id):

    # Multiprotocol extensions AFI 1, SAFI 1 and AFI 2, SAFI 1:
    opt_params = b"\x02\x06\x01\x04\x00\x01\x00\x01" + b"\x02\x06\x01\x04\x00\x02\x00\x01"

    return (BGP_HEADER_MARKER +
            two_bytes(29 + len(opt_params)) +     # 29 = Open message length when no optional parameters are provided
            byte(MSG_TYPE_OPEN) +     # Type 1 = Open
            byte(BGP_VERSION) +       # Version
            two_bytes(AS) +           # My Autonomous System
            two_bytes(holdtime) +     # Hold Time
            bgp_id +                  # BGP Identifier
            byte(len(opt_params)) +   # Opt Parm Len
            opt_params
            )

if __name__ == "__main__":
    session = BGPClientSession(HOST)

    sent = session.send(open_message(MY_AS, MY_HOLDTIME, MY_BGP_ID))
    print("Sent {} bytes in Open message".format(sent))

    sent = session.send(keepalive_message())
    print("Sent {} bytes in Keepalive message".format(sent))

    while True:
        message = session.read_message()
        message.dump_message()
        if message.type == MSG_TYPE_NOTIFICATION:
            session.close()
            break
        elif message.type == MSG_TYPE_KEEPALIVE:
            sent = session.send(keepalive_message())
            print("Sent {} bytes in Keepalive message".format(sent))

