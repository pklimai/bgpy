import socket
from time import sleep

HOST = "10.254.0.41"
PORT = 179

# Example what we received without sending anything:
# b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff  \x00\x1d  \x01  \x04\xfd\xe8\x00Z\n\x00\x00\x01\x00
#   \xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff  \x00\x15  \x03  \x04\x00'

MSG_TYPE_NAMES = {1: "OPEN", 2: "UPDATE", 3: "NOTIFICATION", 4: "KEEPALIVE"}


def read_message_from_bgp_socket(s):
    data_msg_header = s.recv(19)
    print("Received raw :", repr(data_msg_header))
    msg_length = data_msg_header[16] * 256 + data_msg_header[17]
    print("Message length: ", msg_length)
    msg_type = data_msg_header[18]
    print("Message type: {} ({})".format(msg_type, MSG_TYPE_NAMES[msg_type]))
    if msg_length > 19:
        data_msg_remaining = s.recv(msg_length - 19)
        print("Received raw, remainder: ", repr(data_msg_remaining))
        if msg_type == 1:
            print("Open message: version {}".format(data_msg_remaining[0]))
            print("  AS {}".format(data_msg_remaining[1]*256 + data_msg_remaining[2]))
            print("  Hold time {}".format(data_msg_remaining[3] * 256 + data_msg_remaining[4]))
            print("  BGP ID {}.{}.{}.{}".format(data_msg_remaining[5], data_msg_remaining[6],
                                                            data_msg_remaining[7], data_msg_remaining[8]))
        elif msg_type == 3:
            err_code = data_msg_remaining[0]
            err_subcode = data_msg_remaining[1]
            print("Notification message: code {}, subcode {}".format(err_code, err_subcode))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    sleep(1)

    sent = s.send(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' +
           b'\x00\x1d' + b'\x01' + b'\x04' +b'\xff\xdc' + b'\x00\x5a' + b'\x0a\x00\x00\x01' + b'\x00')
    print("Sent {} bytes".format(sent))

    sent = s.send(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' +
           b'\x00\x13' + b'\x04')
    print("Sent {} bytes".format(sent))

    sleep(1)

    # print("GOT: ", repr(s.recv(1)))

    read_message_from_bgp_socket(s)
    read_message_from_bgp_socket(s)
    read_message_from_bgp_socket(s)
    read_message_from_bgp_socket(s)




