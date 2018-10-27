from datetime import datetime
from lib.constants import *
from lib.functions import *


class BGPMessage:
    def __init__(self, type, length, header, remainder):
        self.type = type
        self.length = length
        self.header = header
        self.remainder = remainder

    def decode_message(self):
        pass   #  Must be implemented by subclass

    def dump_message(self):
        # TODO: need to store actual receipt datetime
        print(datetime.now(), " Received BGP message:")
        print("  Message type: {} ({})".format(self.type, MSG_TYPE_NAMES[self.type]))
        print("  Message length: ", self.length)
        print_str_list(self.decode_message()["text"])


class BGPMessageFactory:
    @staticmethod
    def get_message(msg_type, msg_length, data_msg_header, data_msg_remaining):
        if msg_type == MSG_TYPE_OPEN:
            return BGPOpenMessage(msg_length, data_msg_header, data_msg_remaining)
        elif msg_type == MSG_TYPE_UPDATE:
            return BGPUpdateMessage(msg_length, data_msg_header, data_msg_remaining)
        elif msg_type == MSG_TYPE_KEEPALIVE:
            return BGPKeepaliveMessage(msg_length, data_msg_header, data_msg_remaining)
        elif msg_type == MSG_TYPE_NOTIFICATION:
            return BGPNotificationMessage(msg_length, data_msg_header, data_msg_remaining)
        else:
            raise WrongValue


class BGPOpenMessage(BGPMessage):
    def __init__(self, length, header, remainder):
        super().__init__(MSG_TYPE_OPEN, length, header, remainder)

    def decode_message(self):
        result = {"text": []}
        result["text"].append("  BGP version: {}".format(self.remainder[0]))
        result["text"].append("  AS: {}".format(get_word(self.remainder[1:3])))
        result["text"].append("  Hold time: {}".format(get_word(self.remainder[3:5])))
        result["text"].append("  BGP ID: {}.{}.{}.{}".format(*self.remainder[5:9]))

        opt_param_len = self.remainder[9]
        result["text"].append("  Optional parameters length: {}".format(opt_param_len))
        if opt_param_len > 0:
            opt_params = self.remainder[10:10+opt_param_len]
            pos = 0
            while pos < opt_param_len:
                param_type = opt_params[pos]
                param_len = opt_params[pos+1]
                param_val = opt_params[pos+2 : pos+2+param_len]
                result["text"].append("    Optional parameter type {}, len {}, val {}".
                                      format(param_type, param_len, param_val))
                if param_type == PARAM_TYPE_CAPABILITY:
                    capability_type = param_val[0]
                    capability_len = param_val[1]
                    capability_val = param_val[2 : 2+capability_len]
                    result["text"].append("      Capability type {}, len {}, val {}".
                                          format(capability_type, capability_len, capability_val))
                    if capability_type == 1:
                        afi = get_word(capability_val[0:2])
                        safi = get_word(capability_val[2:4])
                        result["text"].append("        Multiprotocol extensions AFI {}, SAFI {}".format(afi, safi))
                    pos += (param_len + 2)

        return result
        # TODO: add other fields to result, not just text


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


class BGPUpdateMessage(BGPMessage):
    def __init__(self, length, header, remainder):
        super().__init__(MSG_TYPE_UPDATE, length, header, remainder)

    def decode_message(self):
        result = {"text": []}
        withdrawn_len = get_word(self.remainder[0:2])
        if withdrawn_len > 0:
            withdrawn_routes_data = self.remainder[2:withdrawn_len + 2]
            result["text"].append("  Withdrawn Routes:")
            result["text"] += decode_nlri_data(withdrawn_routes_data)["text"]
        tot_path_attr_len = get_word(self.remainder[withdrawn_len + 2:withdrawn_len + 4])
        path_attrs = self.remainder[withdrawn_len + 4:withdrawn_len + 4 + tot_path_attr_len]
        ptr = 0
        while ptr < len(path_attrs):
            attr_flags = path_attrs[ptr + 0]
            attr_typecode = path_attrs[ptr + 1]
            # Defines whether the Attribute Length is one octet (if set to 0) or two octets (if set to 1):
            ext_length_bit = to_bin_byte(attr_flags)[3]
            if ext_length_bit == '0':
                attr_length = path_attrs[ptr + 2]
                attr_start_offset = 3
            else:
                attr_length = get_word(path_attrs[ptr + 2 : ptr + 4])
                attr_start_offset = 4
            attr_val = path_attrs[ptr + attr_start_offset : ptr + attr_start_offset + attr_length]
            result["text"].append("    Attribute: flags {}, typecode {}, value {}".
                                  format(attr_flags, attr_typecode, attr_val))
            # result["text"].append("        Length {}, ext bit {}".format(attr_length, ext_length_bit))
            ptr += (attr_start_offset + attr_length)

        nlri_data = self.remainder[withdrawn_len + 4 + tot_path_attr_len:]
        if len(nlri_data) > 0:
            result["text"].append("  NLRI in update:")
            result["text"] += decode_nlri_data(nlri_data)["text"]
        return result


class BGPKeepaliveMessage(BGPMessage):
    def __init__(self, length, header, remainder):
        super().__init__(MSG_TYPE_KEEPALIVE, length, header, remainder)

    def decode_message(self):
        result = {"text": []}
        return result


class BGPNotificationMessage(BGPMessage):
    def __init__(self, length, header, remainder):
        super().__init__(MSG_TYPE_NOTIFICATION, length, header, remainder)

    def decode_message(self):
        result = {"text": []}
        err_code = self.remainder[0]
        err_subcode = self.remainder[1]
        result["text"].append("Notification message: code {}, subcode {}".format(err_code, err_subcode))
        return result
