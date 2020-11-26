import os
import uuid
import zipfile

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField
from extended_choices import Choices
from rest_framework.authtoken.models import Token
from treebeard.mp_tree import MP_Node




# JURISDICTIONS and USERS
################################################################################

class Jurisdiction(models.Model):
    """
    The top-level organizational structure in which the standards documents are
    published, promulgated. Institutions that publish standards include ministries,
    curriculum bodies, an assesment boards, professional organizations, etc.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Official name of the organization or government body")
    short_name = models.CharField(max_length=200, help_text="the name used in URIs")
    country = CountryField()
    alt_name = models.CharField(max_length=200, blank=True, null=True, help_text="Alternative name")
    language = models.CharField(max_length=20, blank=True, null=True,
                                help_text="BCP47 lang codes like en, es, fr-CA")
    notes = models.TextField(blank=True, null=True, help_text="Public comments and notes about this jurisdiction.")


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    background = models.CharField(max_length=200, help_text="What is your background?")
    jurisdiction = models.ForeignKey(Jurisdiction, related_name="userprofiles", on_delete=models.CASCADE)
    # roles wihin jurisdiction are: admin/editor/approver/technical



# CONTROLLED VOCABULARIES
################################################################################

class ControlledVocabulary(models.Model):
    """
    A set of controlled terms served under /terms/{juri}/{self.name}/.
    This is a Django model (DB table) that closely resembles skos:ConceptScheme.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # uri   (e.g. https://groccad.org/terms/{jury}/{self.name})
    jurisdiction = models.ForeignKey(Jurisdiction, related_name="vocabularies", on_delete=models.CASCADE)
    name = models.CharField(max_length=200, help_text="The name used in URIs")
    label = models.CharField(max_length=200, help_text="Human-readable label" )
    alt_label = models.CharField(max_length=200, blank=True, null=True, help_text="Alternative label" )
    hidden_label = models.CharField(max_length=200, blank=True, null=True, help_text="Hidden label" )
    description = models.TextField(blank=True, null=True, help_text="Explain where this vocab. is used")
    # metadata
    notes = models.TextField(blank=True, null=True, help_text="Other comments and notes about the vocabulary.")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                related_name="vocabularies", on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(default=dict)  # for extensibility


class Term(models.Model):
    """
    A term within a controlled vocabulary that corresponds to an URL like
    `/terms/{juri}/{vocab.name}/{self.name}` if a top-level term, or path like
    `/terms/{juri}/{vocab.name}/{self.parent.name}/{self.name}` in a hierarchy.
    This is a Django model (DB table) that closely resembles skos:Concept.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # A. data 
    vocabulary = models.ForeignKey("ControlledVocabulary", related_name="terms", on_delete=models.CASCADE)
    name = models.CharField(max_length=200, help_text="Term name as it appears in URIs")
    label = models.CharField(max_length=200, help_text="Human-readable label" )
    alt_label = models.CharField(max_length=200, help_text="Alternative label" )
    hidden_label = models.CharField(max_length=200, help_text="Hidden label" )
    notation = models.CharField(max_length=200, blank=True, null=True,
                                help_text="Other unique identifier for this term")
    definition = models.TextField(help_text="Explain the meaning of this term")
    notes = models.TextField(help_text="Comments and notes about the term")
    language = models.CharField(max_length=20, blank=True, null=True,
                help_text="BCP47/RFC5646 codes like en, es, fr-CA.")

    # B. structural
    sort_order = models.FloatField(default=1.0)  # sort order among siblings
    parent = models.ForeignKey("Term", related_name="children",
                               on_delete=models.CASCADE, blank=True, null=True)
                               # e.g. None if term is a top concept in scheme

    # C. metadata
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(default=dict)  # for extensibility


    def get_term_path(self):
        if self.parent:
            raise NotImplementedError('TODO')
        else:
            v = self.vocabulary
            return '/'.join([v.jurisdiction.name, v.name, self.name])

    def get_absolute_url(self):
        return "/terms/" + self.get_term_path()

    @property
    def uri(self):
        "Canonical URI for term eg. https://vd.link/terms/Ghana/SubjectAreas/PE"
        return self.get_absolute_url()




TERMREL_KINDS = Choices(
    # skos:semanticRelation (within-vocabulary links)
    ('broader',      0,  'has parent (a broader term)'),
    ('narrower',     1,  'has child (a more specific term)'),
    ('related',      2,  'has a related term'),
    # skos:mappingRelation (links to other vocabularies including external URIs)
    ('exactMatch', 100,  'matches exactly'),        # identity matches (foreign keys)
    ('closeMatch',  80,  'matches closely'),        # 80%+ match (subjective)
    ('relatedMatch',40,  'has a related match'),    # source and target are of same "size" and related
    ('broadMatch',  21,  'has a broader match'),    # source is related to a subset of the target
    ('narrowMatch', 20,  'has a narrower match'),   # target is related to a subset of the source
)

class TermRelation(models.Model):
    """
    A relation between two Terms.
    Defines a sub-property of skos:semanticRelation property from the origin concept to the target concept
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(Term, related_name='source+', on_delete=models.CASCADE)
    target_uri = models.CharField(max_length=500, null=True, blank=True)
    # for internal references target_uri is NULL and and target is a FK
    target = models.ForeignKey(Term, related_name='target+', blank=True, null=True, on_delete=models.CASCADE)
    kind = models.PositiveSmallIntegerField(choices=TERMREL_KINDS.choices)

    # metadata
    notes = models.TextField(help_text="Comments and notes about the relation")
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

