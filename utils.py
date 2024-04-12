import sqlite3

base = sqlite3.connect('notes.sqlite')


def encode_pixel(px: tuple, batch: list) -> tuple:
    red = px[0] - px[0] % 2 + batch[0]
    green = px[1] - px[1] % 2 + batch[1]
    blue = px[2] - px[2] % 2 + batch[2]
    return red, green, blue


def seq_to_bin(sequence) -> list:
    b = []
    for i in sequence:
        batch = '{0:08b}'.format(i)
        for j in batch:
            b.append(int(j))
    return b


def decode_pixel(px: tuple) -> tuple:
    return tuple(map(lambda x: x % 2, px))


def bin_to_str(binary) -> str:
    s = ''
    for i in range(0, 384, 8):  # len(binary) == 384
        s += chr(int(''.join(map(str, binary[i:i + 8])), 2))
    return s
