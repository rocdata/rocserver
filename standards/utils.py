
from urllib.parse import urlparse


from functools import partial
import shortuuid
import uuid


# GENERIC SHORT UUIDs HELPERS
###############################################################################

def short_code_to_uuid(short_code):
    """
    Convert a `short_code` (str) to a UUID object.
    >>> short_code_to_uuid('XR8zjfq')
    "00000000-0000-0000-0000-00eacfdd3baf"
    """
    return shortuuid.decode(short_code)


def uuid_to_short_code(uid):
    """
    Convert a UUID object to it's `short_code` (str) representation.
    >>> uuid_to_short_code(uuid.UUID('00000000-0000-0000-0000-00eacfdd3baf'))
    "XR8zjfq"
    """
    short_code = shortuuid.encode(uid, pad_length=0)
    return short_code


def generate_short_code(length=7):
    """
    Generate a `short_code` (str) with of length `length` (int).
    The short_code corresponds to a uuid.UUID object with lots of leading zeros.
    """
    long_code = shortuuid.uuid()
    short_code = long_code[0:length]
    short_code = short_code.lstrip(shortuuid.get_alphabet()[0])
    return short_code


def generate_short_uuid(length=7):
    """
    Generate a uuid.UUID object that has lots of leading zeros, so that the
    corresponding `short_code` (str) will be of length no greater than `length`.
    """
    short_code = generate_short_code(length=length)
    return shortuuid.decode(short_code)


