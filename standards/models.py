import os
import uuid
import zipfile

from django.conf import settings
from django.db.models import CASCADE
from django.db.models import CharField
from django.db.models import DateField
from django.db.models import DateTimeField
from django.db.models import FloatField
from django.db.models import ForeignKey
from django.db.models import JSONField
from django.db.models import OneToOneField
from django.db.models import Manager
from django.db.models import ManyToManyField
from django.db.models import Model
from django.db.models import SET_NULL
from django.db.models import TextField
from django.db.models import URLField
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

class Jurisdiction(Model):
    """
    The top-level organizational structure in which the standards documents are
    published, promulgated. Institutions that publish standards include ministries,
    curriculum bodies, an assesment boards, professional organizations, etc.
    """
    id = ShortUUIDField(primary_key=True, editable=False, prefix='J')
    # data
    display_name = CharField(max_length=200, help_text="Official name of the organization or government body")
    name = CharField(max_length=200, unique=True, help_text="the name used in URIs")
    country = CountryField(blank=True, null=True, help_text='Country of jurisdiction')
    alt_name = CharField(max_length=200, blank=True, null=True, help_text="Alternative name")
    language = CharField(max_length=20, blank=True, null=True,
                                help_text="BCP47 lang codes like en, es, fr-CA")
    notes = TextField(blank=True, null=True, help_text="Public comments and notes about this jurisdiction.")
    website_url = URLField(max_length=512, null=True, blank=True)

    def __str__(self):
        return self.name

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


class UserProfile(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="profile")
    background = CharField(max_length=200, help_text="What is your background?")
    jurisdiction = ForeignKey(Jurisdiction, related_name="userprofiles", on_delete=CASCADE)
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
    # NEED FEEDBACK BEFORE INCLUSION
    # ('cognitive_process_dimensions', "Congitive Process Dimensions (Bloom's taxonomy level)"),
    # ('knowledge_dimensions',         "Knoledge dimensions"),
)


class ControlledVocabulary(Model):
    """
    A set of controlled terms served under /terms/{juri}/{self.name}/.
    This is a Django model (DB table) that closely resembles skos:ConceptScheme.
    """
    id = ShortUUIDField(primary_key=True, editable=False, prefix='V')
    # uri, computed field, e.g., https://rocdata.global/terms/{jury}/{self.name}
    jurisdiction = ForeignKey(Jurisdiction, related_name="vocabularies", on_delete=CASCADE)
    kind = CharField(max_length=50, blank=True, null=True, choices=SPECIAL_VOCABULARY_KINDS, help_text="Vocabulay kind (e.g. education_levels)")
    name = CharField(max_length=200, help_text="The name used in URIs")
    label = CharField(max_length=200, help_text="Human-readable label")
    alt_label = CharField(max_length=200, blank=True, null=True, help_text="Alternative label" )
    hidden_label = CharField(max_length=200, blank=True, null=True, help_text="Hidden label" )
    description = TextField(blank=True, null=True, help_text="Explain where this vocab. is used")
    language = CharField(max_length=20, blank=True, null=True, help_text="BCP47/RFC5646 codes like en, es, fr-CA.")
    # metadata
    source = TextField(blank=True, null=True, help_text="Where is this vocabulary defined?")
    notes = TextField(blank=True, null=True, help_text="Comments and notes about this vocabulary")
    creator = CharField(max_length=200, blank=True, null=True, help_text="Person or organization that published this vocabulary")
    date_created = DateTimeField(auto_now_add=True)
    date_modified = DateTimeField(auto_now=True)
    extra_fields = JSONField(default=dict, blank=True)  # for data extensibility

    class Meta:
        verbose_name_plural = 'Controlled vocabularies'
        unique_together = [['jurisdiction', 'name']]

    def __str__(self):
        return self.jurisdiction.name + '/' + self.name

    def get_absolute_url(self):
        return "/terms/" + self.__str__()

    @property
    def uri(self):
        return self.get_absolute_url()

    def get_fields(self):
        fields = [('uri', self.get_absolute_url())]      # for display in HTML
        for field in ControlledVocabulary._meta.fields:
            if getattr(self, field.name):
                fields.append((field.name, field.value_to_string(self)))
        return fields


class TermModelManager(Manager):
    def get_queryset(self):
        return super(TermModelManager, self).get_queryset().select_related("vocabulary", "vocabulary__jurisdiction")

class Term(Model):
    """
    A term within a controlled vocabulary that corresponds to an URL like
    `/terms/{juri.name}/{vocab.name}/{self.path}`. Paths can a be either simple
    terms or a /-separated taxon path of terms.
    This is a Django model (DB table) that closely resembles skos:Concept.
    """
    id = ShortUUIDField(primary_key=True, editable=False, prefix='T')
    # Data
    vocabulary = ForeignKey("ControlledVocabulary", related_name="terms", on_delete=CASCADE)
    path = CharField(max_length=200, help_text="Term path as it appears in URI")
    label = CharField(max_length=200, help_text="Human-readable label" )
    alt_label = CharField(max_length=200, blank=True, null=True, help_text="Alternative label" )
    hidden_label = CharField(max_length=200, blank=True, null=True, help_text="Hidden label" )
    notation = CharField(max_length=200, blank=True, null=True, help_text="Other unique identifier for this term")
    definition = TextField(blank=True, null=True, help_text="Explain the meaning of this term")
    notes = TextField(blank=True, null=True, help_text="Comments and notes about the term")
    language = CharField(max_length=20, blank=True, null=True, help_text="BCP47/RFC5646 codes like en, es, fr-CA.")

    # Import and publishing
    source_uri = URLField(max_length=512, null=True, blank=True)
    canonical_uri = URLField(max_length=512, null=True, blank=True)

    # Structural
    sort_order = FloatField(default=1.0)  # sort order among siblings

    # Metadata
    date_created = DateTimeField(auto_now_add=True)
    date_modified = DateTimeField(auto_now=True)
    extra_fields = JSONField(default=dict, blank=True)  # for data extensibility

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
    ('broadMatch',   'source is related to a subset of the target'),
    ('narrowMatch',  'target is related to a subset of the source'),
    ('relatedMatch', 'source and target are related and of similar size'),
)

class TermRelation(Model):
    """
    A relation between two Terms (`source` and `target`) or a source Term and
    an external target URI (`target_uri`).
    """
    id = ShortUUIDField(primary_key=True, editable=False, prefix='TR', length=10)
    source = ForeignKey(Term, related_name='relations_source', on_delete=CASCADE)
    target_uri = CharField(max_length=500, null=True, blank=True)
    # for internal references target_uri is NULL and and target is a FK
    target = ForeignKey(Term, related_name='relations_target', blank=True, null=True, on_delete=CASCADE)
    kind = CharField(max_length=32, choices=TERM_REL_KINDS)

    # metadata
    notes = TextField(help_text="Additional notes about the relation")
    date_created = DateTimeField(auto_now_add=True)
    date_modified = DateTimeField(auto_now=True)

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

class StandardsDocument(Model):
    """
    General Stores the metadata for a curriculum standard, usually one document.
    """
    # IDs
    id = ShortUUIDField(primary_key=True, editable=False, prefix='D')
    canonical_uri = URLField(max_length=512, null=True, blank=True)
    # uri = computed field = localhost + get_absolute_url()
    #
    # Document info
    jurisdiction = ForeignKey(Jurisdiction, related_name="documents", on_delete=CASCADE, help_text='Jurisdiction of standards document')
    title = CharField(max_length=200, help_text="The offficial title of the document")
    short_name = CharField(unique=True, max_length=200, help_text="A short, unique name for the document, e.g. CCSSM")
    description = TextField(blank=True, null=True, help_text="Detailed info about this document")
    language = CharField(max_length=20, blank=True, null=True, help_text="BCP47/RFC5646 codes like en, es, fr-CA.")
    publisher = CharField(max_length=200, blank=True, null=True, help_text="The name of the organizaiton publishing the document")
    version = CharField(max_length=50, blank=True, null=True, help_text="Document version or edition")
    #
    # Licensing
    license	= ForeignKey(Term, related_name='+', blank=True, null=True, on_delete=SET_NULL, limit_choices_to={'vocabulary__kind': 'license_kinds'})
    license_description	= TextField(blank=True, null=True, help_text="Full text of the document's licencing information")
    copyright_holder = CharField(max_length=200, blank=True, null=True, help_text="Name of organization that holds the copyright to the document")
    #
    # Educational domain
    subjects = ManyToManyField(Term, related_name="+", limit_choices_to={'vocabulary__kind': 'subjects'})
    education_levels = ManyToManyField(Term, related_name="+", limit_choices_to={'vocabulary__kind': 'education_levels'})
    date_valid = DateField(blank=True, null=True, help_text="Date when document started being valid")
    date_retired = DateField(blank=True, null=True, help_text="Date when document stopped being valid")
    #
    # Digitization domain
    digitization_method = CharField(max_length=200, choices=DIGITIZATION_METHODS, help_text="Digitization method")
    source_url = URLField(max_length=512, blank=True, help_text="Where the data of this document was imported from")
    publication_status	= CharField(max_length=30, choices=PUBLICATION_STATUSES, default=PUBLICATION_STATUSES.draft)
    #
    # Metadata
    notes = TextField(blank=True, null=True, help_text="Additional notes about the document")
    date_created = DateTimeField(auto_now_add=True, help_text="When the standards document was added to repository.")
    date_modified = DateTimeField(auto_now=True, help_text="Date of last modification to document metadata.")
    extra_fields = JSONField(default=dict, blank=True)  # for other data


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


