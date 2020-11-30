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
from model_utils import Choices
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
    # data
    display_name = models.CharField(max_length=200, help_text="Official name of the organization or government body")
    name = models.CharField(max_length=200, unique=True, help_text="the name used in URIs")
    country = CountryField(blank=True, help_text='Country of jurisdiction')
    alt_name = models.CharField(max_length=200, blank=True, null=True, help_text="Alternative name")
    language = models.CharField(max_length=20, blank=True, null=True,
                                help_text="BCP47 lang codes like en, es, fr-CA")
    notes = models.TextField(blank=True, null=True, help_text="Public comments and notes about this jurisdiction.")

    def __str__(self):
        return self.name + ' (id=' + self.id.__str__()[0:7] +')'

    def get_absolute_url(self):
        return "/terms/" + self.name

    def get_fields(self):
        fields = [('uri', self.get_absolute_url())]      # for display in HTML
        for field in Jurisdiction._meta.fields:
            if getattr(self, field.name):
                fields.append(
                    (field.name, field.value_to_string(self))
                )
        return fields


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    background = models.CharField(max_length=200, help_text="What is your background?")
    jurisdiction = models.ForeignKey(Jurisdiction, related_name="userprofiles", on_delete=models.CASCADE)
    # roles wihin jurisdiction are: admin/editor/approver/technical

    def __str__(self):
        return self.user.username + ' (email=' + self.user.email +')'




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
    language = models.CharField(max_length=20, blank=True, null=True, help_text="BCP47/RFC5646 codes like en, es, fr-CA.")
    # metadata
    source = models.TextField(blank=True, null=True, help_text="Where is this vocabulary defined?")
    notes = models.TextField(blank=True, null=True, help_text="Comments and notes about this vocabulary")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                related_name="vocabularies", on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(default=dict, blank=True)  # for extensibility

    class Meta:
        verbose_name_plural = 'Controlled vocabularies'
        unique_together = [['jurisdiction', 'name']]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/terms/" + self.jurisdiction.name + '/' + self.name

    def get_fields(self):
        fields = [('uri', self.get_absolute_url())]      # for display in HTML
        for field in ControlledVocabulary._meta.fields:
            if getattr(self, field.name):
                fields.append(
                    (field.name, field.value_to_string(self))
                )
        return fields


class Term(models.Model):
    """
    A term within a controlled vocabulary that corresponds to an URL like
    `/terms/{juri.name}/{vocab.name}/{self.path}`. Paths can a be either simple
    terms or a /-separated taxon path of terms.
    This is a Django model (DB table) that closely resembles skos:Concept.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # A. data 
    vocabulary = models.ForeignKey("ControlledVocabulary", related_name="terms", on_delete=models.CASCADE)
    path = models.CharField(max_length=200, help_text="Term path as it appears in URI")
    label = models.CharField(max_length=200, help_text="Human-readable label" )
    alt_label = models.CharField(max_length=200, blank=True, null=True, help_text="Alternative label" )
    hidden_label = models.CharField(max_length=200, blank=True, null=True, help_text="Hidden label" )
    notation = models.CharField(max_length=200, blank=True, null=True, help_text="Other unique identifier for this term")
    definition = models.TextField(blank=True, null=True, help_text="Explain the meaning of this term")
    notes = models.TextField(blank=True, null=True, help_text="Comments and notes about the term")
    language = models.CharField(max_length=20, blank=True, null=True, help_text="BCP47/RFC5646 codes like en, es, fr-CA.")

    # B. structural
    sort_order = models.FloatField(default=1.0)  # sort order among siblings

    # C. metadata
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(default=dict, blank=True)  # for extensibility

    class Meta:
        unique_together = [['vocabulary', 'path']]

    def get_absolute_url(self):
        v = self.vocabulary
        return "/terms/" + v.jurisdiction.name + '/' + v.name + '/' + self.path

    @property
    def uri(self):
        return self.get_absolute_url()

    def get_parent(self):
        if '/' not in self.path:
            return None
        else:
            path_list = self.path.split('/')
            parent_path = '/'.join(path_list[:-1])
            parent = Term.objects.get(path=parent_path, vocabulary=self.vocabulary)
            return parent

    def get_descendants(self):
        return Term.objects.filter(path__startswith=self.path)

    def __str__(self):
        return self.vocabulary.name + '/' + self.path

    def get_fields(self):
        fields = [('uri', self.get_absolute_url())]      # for display in HTML
        for field in Term._meta.fields:
            if getattr(self, field.name):
                fields.append(
                    (field.name, field.value_to_string(self))
                )
        return fields



TERMREL_KINDS = Choices(
    # skos:semanticRelation (within-vocabulary links)
    ('broader',      'has parent (a broader term)'),
    ('narrower',     'has child (a more specific term)'),
    ('related',      'has related term (same vocabulary)'),
    # skos:mappingRelation (links to other vocabularies including external URIs)
    ('exactMatch',   'matches exactly'),        # 100% identity matches
    ('closeMatch',   'matches closely'),        # 80% match (subjective)
    ('relatedMatch', 'source and target are related and of similar size'),
    ('broadMatch',   'source is related to a subset of the target'),
    ('narrowMatch',  'target is related to a subset of the source'),
)

class TermRelation(models.Model):
    """
    A relation between two Terms (`source` and `target`) or a source Term and
    an external target URI (`target_uri`).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(Term, related_name='relations_source', on_delete=models.CASCADE)
    target_uri = models.CharField(max_length=500, null=True, blank=True)
    # for internal references target_uri is NULL and and target is a FK
    target = models.ForeignKey(Term, related_name='relations_target', blank=True, null=True, on_delete=models.CASCADE)
    kind = models.CharField(max_length=32, choices=TERMREL_KINDS)

    # metadata
    notes = models.TextField(help_text="Comments and notes about the relation")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        target_str = self.target_uri if self.target_uri else str(self.target)
        return str(self.source) + '--' + self.kind + '-->' + target_str



# CURRICULUM STANARDS
################################################################################


# CROSSWALKS
################################################################################



# CONTENT
################################################################################


# CONTENT CORRELATIONS
################################################################################


