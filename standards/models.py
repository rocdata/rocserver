import os
import uuid
import zipfile

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from treebeard.mp_tree import MP_Node


# JURISDICTION
################################################################################


# CONTROLLED VOCABULARIES
################################################################################



class ControlledVocabulary(models.Model):
    """
    A set of controlled terms served under  /terms/{juri}/{self.label}/.
    This is a Django model (DB table) skos:closeMatch to skos:ConceptScheme.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # uri   (e.g. https://groccad.org/schema/Ghana/SubjectAreas)
    # jurisdiction → Jurisdiction instance  (e.g. Ghana)
    name = models.CharField(max_length=200, help_text="Vocabulary name as it appears in URIs.")
    label = models.CharField(max_length=200, help_text="Human-readable label." )
    # altLabel
    # hiddenLabel
    notation = models.CharField(max_length=200, blank=True, null=True)
    # type?
    # version?
    description = models.TextField(help_text="Explain where this vocab. is used.")
    date_created = models.DateTimeField(auto_now_add=True)
    # creator
    date_modified = models.DateTimeField(auto_now=True)


class ControlledVocabularyTerm(models.Model):
    """
    A term within a controlled terms vocabylay served at /terms/{juri}/{self.parent.label}/.
    This is a Django model (DB table) skos:closeMatch to skos:Concept.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # uri (e.g. https://groccad.org/schemas/Ghana/SubjectAreas/physicalEducation)
    vocabulary = models.ForeignKey("ControlledVocabulary", related_name="terms", on_delete=models.CASCADE)
    name = models.CharField(max_length=200, help_text="Term name as it appears in URI.")
    label = models.CharField(max_length=200, help_text="Human-readable label." )
    # altLabel = 
    # hiddenLabel =
    # notation =
    description = models.TextField(help_text="Explain the meaning of this term.")
    parent = models.ForeignKey("ControlledVocabularyTerm", related_name="children",
                               on_delete=models.CASCADE, blank=True, null=True)
                               # e.g. None if term is a top concept in scheme
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)



# CURRICULUM STANARDS
################################################################################



# CROSSWALKS
################################################################################




# CONTENT
################################################################################



# CONTENT CORRELATIONS
################################################################################
