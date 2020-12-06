from functools import partial
import shortuuid
import uuid

from urllib.parse import urlparse


from django import forms
from django.core import exceptions
from django.db import models
from django.urls import resolve



# SHORT UUIDs
################################################################################

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



# Custom field? (subclass UUIDField to make it easier to work)
# https://docs.djangoproject.com/en/3.1/howto/custom-model-fields/

class ShortUUIDField(models.UUIDField):
    """
    A Short UUID Field that is stored as a UUID under the hood, but is presented
    to users as an alphanumeric string.
    """
    default_error_messages = {
        'invalid': '“%(value)s” is not a valid shortuuid.',
    }
    description = "A Short UUID Field of length %(length). "


    def __init__(self, verbose_name=None, **kwargs):
        self.prefix = kwargs.pop('prefix', '')
        self.length = kwargs.pop('length', 7)
        if 'default' not in kwargs:
            kwargs['default'] = partial(generate_short_code, length=self.length)
        super().__init__(verbose_name, **kwargs)


    def deconstruct(self):
        """
        Provides the info needed to reconstruct the field (used in migrations).
        """
        name, path, args, kwargs = super().deconstruct()
        if self.prefix != "":
            kwargs['prefix'] = self.prefix
        if self.length != 7:
            kwargs['length'] = self.length
        return name, path, args, kwargs


    def short_code_to_uuid(self, short_code):
        """
        Strip prefix if needed and convert `short_code` (str) to a UUID object.
        """
        if self.prefix:
            short_code = short_code[len(self.prefix):]
        return shortuuid.decode(short_code)


    def uuid_to_short_code(self, uuid_obj):
        """
        Convert UUID object to `short_code` (str) and prepend prefix if needed.
        """
        short_code = shortuuid.encode(uuid_obj, pad_length=0)
        if self.prefix:
            short_code = self.prefix + short_code
        return short_code


    # PYTHON -> DB CONVERSIONS  ################################################

    def get_prep_value(self, value):
        """
        Convert value from short_code (str) to UUID if needed then call parent.
        """
        print('get_prep_value called value=', value, 'of type', type(value))
        value = super(models.UUIDField, self).get_prep_value(value)   # promises
        value = self.to_python(value)
        if isinstance(value, str) and len(value) < 32:
            print('  >> converting to UUID...')
            value = self.short_code_to_uuid(value)
        return super().get_prep_value(value)


    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Convert value from short_code (str) to UUID if needed then call parent.
        """
        print('get_db_prep_value called value=', value, 'of type', type(value))
        value = self.to_python(value)
        if isinstance(value, str) and len(value) < 32:
            print('  db >> converting to UUID...')
            value = self.short_code_to_uuid(value)
        return super().get_db_prep_value(value, connection, prepared=prepared)


    # DB -> PYTHON CONVERSIONS  ################################################

    def from_db_value(self, value, expression, connection):
        """
        Convert the UUID object we get from DB to short_code (str).
        """
        print('from_db_value called value=', value, 'of type', type(value))
        if value is None:
            return value
        return self.uuid_to_short_code(value)


    def to_python(self, value):
        """
        Convert to short_code (str); value can be a short_code or a UUID object.
        """
        print('to_python called value=', value, 'of type', type(value))
        if value is None:
            return None
        if not isinstance(value, uuid.UUID) and not isinstance(value, str):
            raise exceptions.ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': value},
            )
        if isinstance(value, uuid.UUID):
            short_code = self.uuid_to_short_code(value)
        else:
            try:
                uuid_obj = self.short_code_to_uuid(value)
                short_code = self.uuid_to_short_code(uuid_obj)
            except (ValueError):
                raise exceptions.ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': value},
                )
        return short_code

    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': forms.CharField,
            **kwargs,
        })

