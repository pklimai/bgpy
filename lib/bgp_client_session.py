import socket
from lib.constants import *
from lib.functions import *
from lib.settings import DEBUG


class BGPClientSession:
    def __init__(self, host, port=DEFAULT_BGP_PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def send(self, message):
        return self.socket.send(message)

    def read_message(self):
        message = {}

        data_msg_header = self.socket.recv(BGP_HEADER_LENGTH)
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
            data_msg_remaining = self.socket.recv(msg_length - BGP_HEADER_LENGTH)
            message["remainder"] = data_msg_remaining
            if DEBUG: print("Received raw, remainder: ", repr(data_msg_remaining))
        return message

    def close(self):
        self.socket.close()
