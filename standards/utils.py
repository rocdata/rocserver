import shortuuid
import uuid


def short_code_to_uuid(short_code):
    """
    >>> short_code_to_uuid('XR8zjfq')
    "00000000-0000-0000-0000-00eacfdd3baf"

    """
    return shortuuid.decode(short_code)


def uuid_to_short_code(uid):
    """
    >>> uuid_to_short_code(uuid.UUID('00000000-0000-0000-0000-00eacfdd3baf'))
    "XR8zjfq"
    """
    short_code = shortuuid.encode(uid, pad_length=0)
    return short_code


def generate_short_uuid(length=7):
    """
    Generate a uuid.UUID object that has lots of leading zeros, so that the
    corresponding short_code will be short: of length no greater than `length`.
    """
    long_code = shortuuid.uuid()
    short_code = long_code[0:length]
    return shortuuid.decode(short_code)






# Custom field? (subclass UUIDField to make it easier to work)
# https://docs.djangoproject.com/en/3.1/howto/custom-model-fields/