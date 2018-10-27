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


def update_message_host_route(host_route):
    """
    :param host_route: is 4-byte prefix e.g. bytes([10, 1, 1, 1]) for 10.1.1.1/32 route
    """

    path_attrs = bytes([])

    path_attrs += two_bytes(0x4001) + byte(1) + byte(0)                     # Origin
    path_attrs += two_bytes(0x4002) + byte(4) + byte(2) + byte(1) + two_bytes(MY_AS)            # AS-PATH
    path_attrs += two_bytes(0x4003) + byte(4) + bytes([10, 254, 0, 251])    # Next-hop

    upd_msg = two_bytes(len(path_attrs))   # Total path attr length
    upd_msg += path_attrs

    upd_msg += byte(32) + host_route

    return (BGP_HEADER_MARKER +
            two_bytes(21 + len(upd_msg)) +
            byte(MSG_TYPE_UPDATE) +
            two_bytes(0) +               # Withdrawn routes length
            upd_msg
            )


if __name__ == "__main__":
    session = BGPClientSession(HOST)

    sent = session.send(open_message(MY_AS, MY_HOLDTIME, MY_BGP_ID))
    print("Sent {} bytes in Open message".format(sent))

    sent = session.send(keepalive_message())
    print("Sent {} bytes in Keepalive message".format(sent))

    print("Sending {} routes to the peer...".format(NUM_ROUTES_SEND))
    for r in range(ROUTE_SEND_START, ROUTE_SEND_START + NUM_ROUTES_SEND):
        session.send(update_message_host_route(four_bytes(r)))
    print("   ...done!")

    while True:
        message = session.read_message()
        message.dump_message()
        if message.type == MSG_TYPE_NOTIFICATION:
            session.close()
            break
        elif message.type == MSG_TYPE_KEEPALIVE:
            sent = session.send(keepalive_message())
            print("Sent {} bytes in Keepalive message".format(sent))

