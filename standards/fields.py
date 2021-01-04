from functools import partial
import shortuuid
import uuid


from django import forms
from django.core import exceptions
from django.db import models
from django.utils.crypto import get_random_string
from django_extensions.db.fields import UniqueFieldMixin, MAX_UNIQUE_QUERY_ATTEMPTS





# RANDOM STRING ID MODEL FIELD
################################################################################

class CharIdField(UniqueFieldMixin, models.CharField):
    """
    A random character field that is used as primary key for ROC data models.
    By default uses prefix="", length=9, editable=False, blank=True, unique=True.
    Arguments:
        length: Specifies the length of the field including prefix (default: 9)
        prefix: A prefix that will be used for all IDs (default: "")
        unique: If True, duplicate entries are not allowed (default: True)
    This field is an adaptation of django_extensions.db.fields.RandomCharField.
    """
    # Custom alphabet that excludes possibly confusing symbols like I, l, and 1
    ALPHABET = list("23456789ABEFGHKLMNPQUWXYZ" "abcdefghijkmnopqrstuvwxyz")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('blank', True)
        kwargs.setdefault('editable', False)

        self.length = kwargs.pop('length', 9)
        if self.length is None:
            raise ValueError("missing 'length' argument")
        kwargs['max_length'] = self.length

        self.prefix = kwargs.pop('prefix', '')

        self.max_unique_query_attempts = kwargs.pop('max_unique_query_attempts', MAX_UNIQUE_QUERY_ATTEMPTS)

        # Set unique=True unless it's been set manually.
        if 'unique' not in kwargs:
            kwargs['unique'] = True

        super().__init__(*args, **kwargs)

    def random_char_generator(self, chars):
        for i in range(self.max_unique_query_attempts):
            len_random_chars = self.length - len(self.prefix)
            random_chars = ''.join(get_random_string(len_random_chars, chars))
            yield self.prefix + random_chars
        raise RuntimeError('max random character attempts exceeded (%s)' % self.max_unique_query_attempts)

    def in_unique_together(self, model_instance):
        for params in model_instance._meta.unique_together:
            if self.attname in params:
                return True
        return False

    def pre_save(self, model_instance, add):
        if not add and getattr(model_instance, self.attname) != '':
            return getattr(model_instance, self.attname)

        population = self.ALPHABET

        random_chars = self.random_char_generator(population)
        if not self.unique and not self.in_unique_together(model_instance):
            new = next(random_chars)
            setattr(model_instance, self.attname, new)
            return new

        return self.find_unique(
            model_instance,
            model_instance._meta.get_field(self.attname),
            random_chars,
        )

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['length'] = self.length
        del kwargs['max_length']
        if self.prefix:
            kwargs['prefix'] = self.prefix
        if self.unique is False:
            kwargs['unique'] = self.unique
        return name, path, args, kwargs



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

