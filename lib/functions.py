from lib.exceptions import WrongValue

def get_word(lst):
    if len(lst) != 2:
        raise WrongValue
    return lst[0] * 256 + lst[1]


def byte(b):
    if b < 0 or b > 255:
        raise WrongValue
    return bytes([b])


def two_bytes(w):
    if w < 0 or w > 65535:
        raise WrongValue
    return bytes([w // 256, w % 256])


def print_str_list(lst):
    for line in lst:
        print(line)
