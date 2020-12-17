from functools import partial
import shortuuid
import uuid


from django import forms
from django.core import exceptions
from django.db import models



# SHORT UUID MODEL FIELD
################################################################################


class ShortUUIDField(models.UUIDField):
    """
    A Short UUID Field that is stored as a UUID under the hood, but is presented
    to users as an alphanumeric string.
    """
    default_error_messages = {
        'invalid': '%(value)s is not a valid shortuuid.',
    }
    description = "A Short UUID Field."

    @classmethod
    def generate_short_code_with_prefix(cls, prefix='', length=7):
        long_code = shortuuid.uuid()
        short_code = long_code[0:length]
        short_code = short_code.lstrip(shortuuid.get_alphabet()[0])
        if prefix:
            short_code = prefix + short_code
        return short_code


    def __init__(self, verbose_name=None, **kwargs):
        self.prefix = kwargs.pop('prefix', '')
        self.length = kwargs.pop('length', 7)
        if 'default' not in kwargs:
            kwargs['default'] = partial(ShortUUIDField.generate_short_code_with_prefix,
                                        prefix=self.prefix, length=self.length)
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
        value = super(models.UUIDField, self).get_prep_value(value)   # promises
        value = self.to_python(value)
        if isinstance(value, str) and len(value) < 32:
            value = self.short_code_to_uuid(value)
        return super().get_prep_value(value)


    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Convert value from short_code (str) to UUID if needed then call parent.
        """
        value = self.to_python(value)
        if isinstance(value, str) and len(value) < 32:
            value = self.short_code_to_uuid(value)
        return super().get_db_prep_value(value, connection, prepared=prepared)


    # DB -> PYTHON CONVERSIONS  ################################################

    def from_db_value(self, value, expression, connection):
        """
        Convert the UUID object we get from DB to short_code (str).
        """
        if value is None:
            return value
        return self.uuid_to_short_code(value)


    def to_python(self, value):
        """
        Convert to short_code (str); value can be a short_code or a UUID object.
        """
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

