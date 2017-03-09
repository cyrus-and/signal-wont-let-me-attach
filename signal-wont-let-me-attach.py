#!/usr/bin/env python3

import codecs
import io
import itertools
import math
import os
import struct
import sys

from PIL import Image


__prefix_format = '!I'
__prefix_size = struct.calcsize(__prefix_format)


def __build_payload(name, data):
    # store name and data using two size-value records
    name_prefix = struct.pack(__prefix_format, len(name))
    data_prefix = struct.pack(__prefix_format, len(data))
    payload = bytearray()
    payload.extend(name_prefix)
    payload.extend(name)
    payload.extend(data_prefix)
    payload.extend(data)
    return payload


def __parse_payload(payload):
    # extract the file name
    name_size = struct.unpack(__prefix_format, payload[:__prefix_size])[0]
    payload = payload[__prefix_size:]
    name = payload[:name_size].decode('utf-8')
    payload = payload[name_size:]
    # extract the file data
    data_size = struct.unpack(__prefix_format, payload[:__prefix_size])[0]
    payload = payload[__prefix_size:]
    data = codecs.decode(payload[:data_size], 'zlib')
    return name, data


def __measure_container(size):
    # compute the appropriate extents in order to contain size
    n_planes = 4  # RGBA
    side = int(math.ceil(math.sqrt(size / n_planes)))
    capacity = (side ** 2) * n_planes
    return (side, capacity)


def __load_file(path):
    # fetch the name as a byte string
    name = os.path.basename(path)
    if sys.version_info >= (3,):
        name = name.encode('utf-8')
    # read anz compress the file content
    with open(path, 'rb') as content_file:
        data = codecs.encode(content_file.read(), 'zlib')
    return (name, data)


def __write_file(name, data):
    with open(name, 'wb') as content_file:
        content_file.write(data)
    return name


def __load_image(path):
    # fetch image data as raw bytes
    with Image.open(path) as image:
        integers = itertools.chain.from_iterable(image.getdata())
        data = bytes(bytearray(integers))
    return data


def __save_image(path, data, side):
    mode = 'RGBA'
    size = (side, side)
    with Image.frombytes(mode, size, data, decoder_name='raw') as image:
        image.save(path, 'PNG')


def pack(image_path, content_path):
    name, data = __load_file(content_path)
    payload = __build_payload(name, data)
    side, capacity = __measure_container(len(payload))
    payload.extend(b'\x00' * (capacity - len(payload)))
    __save_image(image_path, bytes(payload), side)


def unpack(image_path):
    payload = __load_image(image_path)
    name, data = __parse_payload(payload)
    __write_file(name, data)
    return name


def __usage():
    usage_string = '''Usage:

    <image.png>           attempt unpack and delete the PNG
    <file> [<image.png>]  pack the file into the PNG
'''
    sys.stderr.write(usage_string)
    sys.exit(1)


def __pack_action(image_path, content_path):
    pack(image_path, content_path)
    print(image_path)


def __unpack_action(image_path):
    content_name = unpack(image_path)
    print(content_name)
    os.unlink(image_path)


def __main(args):
    # check arguments
    if len(args) not in (1, 2):
        __usage()
    # extract path components
    input_path = args[0]
    input_base, input_ext = os.path.splitext(input_path)
    # operate according to the extension
    if input_ext.lower() == '.png':
        # attempt to unpack then delete the PNG
        if len(args) != 1:
            __usage()
        else:
            __unpack_action(input_path)
    else:
        # pack the file into the PNG
        if len(args) == 2:
            image_path = args[1]
        else:
            image_path = '{}.png'.format(input_base)
        __pack_action(image_path, input_path)


if __name__ == '__main__':
    try:
        __main(sys.argv[1:])
    except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
        sys.stderr.write('{}\n'.format(str(e)))
        sys.exit(1)
