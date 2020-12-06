from functools import partial

from django.db import models

from standards.utils import ShortUUIDField, generate_short_code


# MODEL FIXTURES
################################################################################

class UUIDModel(models.Model):
    field = ShortUUIDField()

class NullableUUIDModel(models.Model):
    field = ShortUUIDField(blank=True, null=True)

class PrimaryKeyUUIDModel(models.Model):
    id = ShortUUIDField(primary_key=True, default=partial(generate_short_code, length=7))

class RelatedToUUIDModel(models.Model):
    uuid_fk = models.ForeignKey('PrimaryKeyUUIDModel', models.CASCADE)

class UUIDChild(PrimaryKeyUUIDModel):
    pass

class UUIDGrandchild(UUIDChild):
    pass
