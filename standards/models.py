import os
import uuid
import zipfile

from django.conf import settings
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField
from model_utils import Choices
from rest_framework.authtoken.models import Token
from standards.fields import ShortUUIDField
from treebeard.mp_tree import MP_Node





# JURISDICTIONS and USERS
################################################################################

class Jurisdiction(models.Model):
    """
    The top-level organizational structure in which the standards documents are
    published, promulgated. Institutions that publish standards include ministries,
    curriculum bodies, an assesment boards, professional organizations, etc.
    """
    id = ShortUUIDField(primary_key=True, editable=False, prefix='J')
    # data
    display_name = models.CharField(max_length=200, help_text="Official name of the organization or government body")
    name = models.CharField(max_length=200, unique=True, help_text="the name used in URIs")
    country = CountryField(blank=True, null=True, help_text='Country of jurisdiction')
    alt_name = models.CharField(max_length=200, blank=True, null=True, help_text="Alternative name")
    language = models.CharField(max_length=20, blank=True, null=True,
                                help_text="BCP47 lang codes like en, es, fr-CA")
    notes = models.TextField(blank=True, null=True, help_text="Public comments and notes about this jurisdiction.")
    website_url = models.URLField(max_length=512, null=True, blank=True)

    def __str__(self):
        return self.name + ' (id=' + self.id.__str__()[0:7] +')'

    def get_absolute_url(self):
        return "/terms/" + self.name

    @property
    def uri(self):
        return self.get_absolute_url()

    def get_fields(self):
        fields = [('uri', self.get_absolute_url())]      # for display in HTML
        for field in Jurisdiction._meta.fields:
            if getattr(self, field.name):
                fields.append((field.name, field.value_to_string(self)))
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

SPECIAL_VOCABULARY_KINDS = Choices(
    ('education_levels',     'Local education levels (local grade levels)'),
    ('subjects',             'Local academic subjects'),
    ('topic_terms',          'Global topic taxonomy terms'),
    ('curriculum_elements',  'Curriculum standard elements'),
    ('license_kinds',        'License kinds'),
    # ('cognitive_process_dimensions', "Congitive Process Dimensions (Bloom's taxonomy level)"),
    # ('knowledge_dimensions',         "Knoledge dimensions"),
)


class ControlledVocabulary(models.Model):
    """
    A set of controlled terms served under /terms/{juri}/{self.name}/.
    This is a Django model (DB table) that closely resembles skos:ConceptScheme.
    """
    id = ShortUUIDField(primary_key=True, editable=False, prefix='V')
    # uri   (e.g. https://groccad.org/terms/{jury}/{self.name})
    jurisdiction = models.ForeignKey(Jurisdiction, related_name="vocabularies", on_delete=models.CASCADE)
    kind = models.CharField(max_length=50, blank=True, null=True, choices=SPECIAL_VOCABULARY_KINDS, help_text="Vocabulay kind (e.g. education_levels)")
    name = models.CharField(max_length=200, help_text="The name used in URIs")
    label = models.CharField(max_length=200, help_text="Human-readable label")
    alt_label = models.CharField(max_length=200, blank=True, null=True, help_text="Alternative label" )
    hidden_label = models.CharField(max_length=200, blank=True, null=True, help_text="Hidden label" )
    description = models.TextField(blank=True, null=True, help_text="Explain where this vocab. is used")
    language = models.CharField(max_length=20, blank=True, null=True, help_text="BCP47/RFC5646 codes like en, es, fr-CA.")
    # metadata
    source = models.TextField(blank=True, null=True, help_text="Where is this vocabulary defined?")
    notes = models.TextField(blank=True, null=True, help_text="Comments and notes about this vocabulary")
    creator = models.CharField(max_length=200, blank=True, null=True, help_text="Person or organization that published this vocabulary")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(default=dict, blank=True)  # for extensibility

    class Meta:
        verbose_name_plural = 'Controlled vocabularies'
        unique_together = [['jurisdiction', 'name']]

    def __str__(self):
        return self.jurisdiction.name + '/' + self.name

    def get_absolute_url(self):
        return "/terms/" + self.jurisdiction.name + '/' + self.name

    @property
    def uri(self):
        return self.get_absolute_url()

    def get_fields(self):
        fields = [('uri', self.get_absolute_url())]      # for display in HTML
        for field in ControlledVocabulary._meta.fields:
            if getattr(self, field.name):
                fields.append((field.name, field.value_to_string(self)))
        return fields


class TermModelManager(models.Manager):
    def get_queryset(self):
        return super(TermModelManager, self).get_queryset().select_related("vocabulary", "vocabulary__jurisdiction")

class Term(models.Model):
    """
    A term within a controlled vocabulary that corresponds to an URL like
    `/terms/{juri.name}/{vocab.name}/{self.path}`. Paths can a be either simple
    terms or a /-separated taxon path of terms.
    This is a Django model (DB table) that closely resembles skos:Concept.
    """
    id = ShortUUIDField(primary_key=True, editable=False, prefix='T')
    # Data
    vocabulary = models.ForeignKey("ControlledVocabulary", related_name="terms", on_delete=models.CASCADE)
    path = models.CharField(max_length=200, help_text="Term path as it appears in URI")
    label = models.CharField(max_length=200, help_text="Human-readable label" )
    alt_label = models.CharField(max_length=200, blank=True, null=True, help_text="Alternative label" )
    hidden_label = models.CharField(max_length=200, blank=True, null=True, help_text="Hidden label" )
    notation = models.CharField(max_length=200, blank=True, null=True, help_text="Other unique identifier for this term")
    definition = models.TextField(blank=True, null=True, help_text="Explain the meaning of this term")
    notes = models.TextField(blank=True, null=True, help_text="Comments and notes about the term")
    language = models.CharField(max_length=20, blank=True, null=True, help_text="BCP47/RFC5646 codes like en, es, fr-CA.")

    # Import and publishing
    source_uri = models.URLField(max_length=512, null=True, blank=True)
    canonical_uri = models.URLField(max_length=512, null=True, blank=True)

    # Structural
    sort_order = models.FloatField(default=1.0)  # sort order among siblings

    # Metadata
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(default=dict, blank=True)  # for extensibility

    objects = TermModelManager()

    class Meta:
        unique_together = [['vocabulary', 'path']]

    def __str__(self):
        v = self.vocabulary
        return v.jurisdiction.name + '/' + v.name + '/' + self.path

    def get_absolute_url(self):
        return "/terms/" + self.__str__()

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

    def get_fields(self):
        fields = [('uri', self.get_absolute_url())]      # for display in HTML
        for field in Term._meta.fields:
            if getattr(self, field.name):
                fields.append((field.name, field.value_to_string(self)))
        return fields



TERM_REL_KINDS = Choices(
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
    id = ShortUUIDField(primary_key=True, editable=False, prefix='TR', length=10)
    source = models.ForeignKey(Term, related_name='relations_source', on_delete=models.CASCADE)
    target_uri = models.CharField(max_length=500, null=True, blank=True)
    # for internal references target_uri is NULL and and target is a FK
    target = models.ForeignKey(Term, related_name='relations_target', blank=True, null=True, on_delete=models.CASCADE)
    kind = models.CharField(max_length=32, choices=TERM_REL_KINDS)

    # metadata
    notes = models.TextField(help_text="Additional notes about the relation")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        target_str = self.target_uri if self.target_uri else str(self.target)
        return str(self.source) + '--' + self.kind + '-->' + target_str






# CURRICULUM STANDARDS
################################################################################

DIGITIZATION_METHODS = Choices(
    ("manual_entry",    "Manual data entry"),
    ("manual_scan",     "Manual data entry based on OCR"),
    ("automated_scan",  "Semi-automated stucture extraction through OCR"),
    ("website_scrape",  "Curriculum data scraped from website"),
    ("asn_import",      "Curriculum data imported from Achievement Standards Network (ASN)"),
    ("case_import",     "Curriculum data imported from CASE registry"),
)

PUBLICATION_STATUSES = Choices(
    ("draft",       "Draft"),
    ("published",   "Published (active)"),
    ("retired",     "Retired, deprecated, or superceded"),
)

class StandardsDocument(models.Model):
    """
    General Stores the metadata for a curriculum standard, usually one document.
    """
    # IDs
    id = ShortUUIDField(primary_key=True, editable=False, prefix='D')
    canonical_uri = models.URLField(max_length=512, null=True, blank=True)
    # uri = computed field = localhost + get_absolute_url()
    #
    # Document info
    jurisdiction = models.ForeignKey(Jurisdiction, related_name="documents", on_delete=models.CASCADE, help_text='Jurisdiction of standards document')
    title = models.CharField(max_length=200, help_text="The offficial title of the document")
    short_name = models.CharField(unique=True, max_length=200, help_text="A short, unique name for the document, e.g. CCSSM")
    description = models.TextField(blank=True, null=True, help_text="Detailed info about this document")
    language = models.CharField(max_length=20, blank=True, null=True, help_text="BCP47/RFC5646 codes like en, es, fr-CA.")
    publisher = models.CharField(max_length=200, blank=True, null=True, help_text="The name of the organizaiton publishing the document")
    version = models.CharField(max_length=50, blank=True, null=True, help_text="Document version or edition")
    #
    # Licensing
    license	= models.ForeignKey(Term, related_name='+', blank=True, null=True, on_delete=models.SET_NULL, limit_choices_to={'vocabulary__kind': 'license_kinds'})
    license_description	= models.TextField(blank=True, null=True, help_text="Full text of the document's licencing information")
    copyright_holder = models.CharField(max_length=200, blank=True, null=True, help_text="Name of organization that holds the copyright to the document")
    #
    # Educational domain
    subjects = models.ManyToManyField(Term, related_name="+", limit_choices_to={'vocabulary__kind': 'subjects'})
    education_levels = models.ManyToManyField(Term, related_name="+", limit_choices_to={'vocabulary__kind': 'education_levels'})
    date_valid = models.DateField(blank=True, null=True, help_text="Date when document started being valid")
    date_retired = models.DateField(blank=True, null=True, help_text="Date when document stopped being valid")
    #
    # Digitization domain
    digitization_method = models.CharField(max_length=200, choices=DIGITIZATION_METHODS, help_text="Digitization method")
    source_url = models.URLField(max_length=512, blank=True, help_text="Where the data of this document was imported from")
    publication_status	= models.CharField(max_length=30, choices=PUBLICATION_STATUSES, default=PUBLICATION_STATUSES.draft)
    #
    # Metadata
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the document")
    date_created = models.DateTimeField(auto_now_add=True, help_text="When the standards document was added to repository.")
    date_modified = models.DateTimeField(auto_now=True, help_text="Date of last modification to document metadata.")
    extra_fields = models.JSONField(default=dict, blank=True)  # for other data


    # @property
    # def root(self):
    #     return StandardNode.get_root_nodes().get(document=self)

    def __str__(self):
        return "{} ({})".format(self.title, self.id)

    def get_absolute_url(self):
        return "/documents/" + self.id

    @property
    def uri(self):
        return self.get_absolute_url()


