from functools import partial

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
        # allow to set field manually
        if getattr(model_instance, self.attname) != '':
            return getattr(model_instance, self.attname)

        # allow field to be nullable
        if self.null and getattr(model_instance, self.attname) is None:
            return None

        # generate new random value
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
