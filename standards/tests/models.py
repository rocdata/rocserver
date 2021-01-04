from functools import partial

from django.db import models

from standards.fields import CharIdField



# MODEL FIXTURES
################################################################################

class CharIdModel(models.Model):
    field = CharIdField()

class CharIdModelWithPrefix(models.Model):
    field = CharIdField(prefix='WP', length=10)

class NullableCharIdModel(models.Model):
    field = CharIdField(blank=True, null=True)

class PrimaryKeyCharIdModel(models.Model):
    id = CharIdField(primary_key=True)

class RelatedToCharIdModel(models.Model):
    char_fk = models.ForeignKey('PrimaryKeyCharIdModel', models.CASCADE)

class CharIdChildModel(PrimaryKeyCharIdModel):
    pass

class CharIdGrandchildModel(CharIdChildModel):
    pass
