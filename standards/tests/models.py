from functools import partial

from django.db import models

from standards.fields import ShortUUIDField



# MODEL FIXTURES
################################################################################

class UUIDModel(models.Model):
    field = ShortUUIDField()

class UUIDModelWithPrefix(models.Model):
    field = ShortUUIDField(prefix='WP', length=10)

class NullableUUIDModel(models.Model):
    field = ShortUUIDField(blank=True, null=True)

class PrimaryKeyUUIDModel(models.Model):
    id = ShortUUIDField(primary_key=True)

class RelatedToUUIDModel(models.Model):
    uuid_fk = models.ForeignKey('PrimaryKeyUUIDModel', models.CASCADE)

class UUIDChild(PrimaryKeyUUIDModel):
    pass

class UUIDGrandchild(UUIDChild):
    pass
