import socket
from lib.constants import *
from lib.functions import *
from lib.settings import DEBUG
from lib.bgp_messages import BGPMessageFactory


class BGPClientSession:
    def __init__(self, host, port=DEFAULT_BGP_PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def send(self, message):
        return self.socket.send(message)

    def read_message(self):
        data_msg_header = self.socket.recv(BGP_HEADER_LENGTH)
        if DEBUG: print("Received raw: ", repr(data_msg_header))

        msg_length = get_word(data_msg_header[16:18])
        if DEBUG: print("Message length: ", msg_length)

        msg_type = data_msg_header[18]
        if DEBUG: print("Message type: {} ({})".format(msg_type, MSG_TYPE_NAMES[msg_type]))

        data_msg_remaining = None
        if msg_length > BGP_HEADER_LENGTH:
            data_msg_remaining = self.socket.recv(msg_length - BGP_HEADER_LENGTH)
            if DEBUG: print("Received raw, remainder: ", repr(data_msg_remaining))
        return BGPMessageFactory.get_message(msg_type, msg_length, data_msg_header, data_msg_remaining)

    def close(self):
        self.socket.close()
