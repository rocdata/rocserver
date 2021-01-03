from django.db.models import CASCADE
from django.db.models import CharField
from django.db.models import DateField
from django.db.models import DateTimeField
from django.db.models import FloatField
from django.db.models import ForeignKey
from django.db.models import JSONField
from django.db.models import Manager
from django.db.models import ManyToManyField
from django.db.models import Model
from django.db.models import SET_NULL
from django.db.models import TextField
from django.db.models import URLField
from django.db.models import Q, UniqueConstraint
from model_utils import Choices
from mptt.models import MPTTModel
from mptt.models import TreeForeignKey

from standards.fields import ShortUUIDField
from .jurisdictions import Jurisdiction
from .terms import Term




# CURRICULUM STANDARDS
################################################################################

DIGITIZATION_METHODS = Choices(
    ("manual_entry",        "Manual data entry"),
    ("manual_scan",         "Manual data entry based on OCR"),
    ("automated_scan",      "Semi-automated structure extraction through OCR"),
    ("website_scrape",      "Curriculum data scraped from website"),
    ("hackathon_import",    "Curriculum data imported from Hackathon DB"),
    ("asn_import",          "Curriculum data imported from Achievement Standards Network (ASN)"),
    ("case_import",         "Curriculum data imported from CASE registry"),
)

PUBLICATION_STATUSES = Choices(
    ("draft",       "Draft"),
    ("publicdraft", "Public Draft"),
    ("published",   "Published (active)"),
    ("retired",     "Retired, deprecated, or superseded"),
)

class StandardsDocument(Model):
    """
    A standard document identified by a unique ``name`` and ``id`` that stores
    the info extracted from a source document at ``source_doc`` and contains a
    hierarchy of ``StandardNode`` s.
    """
    # IDs
    id = ShortUUIDField(primary_key=True, editable=False, prefix='D')
    name = CharField(unique=True, max_length=200, help_text="A short, unique name for the document, e.g. CCSSM")
    # uri = computed field = localhost + get_absolute_url()
    #
    # Document info
    jurisdiction = ForeignKey(Jurisdiction, related_name="documents", on_delete=CASCADE, help_text='Jurisdiction of standards document')
    title = CharField(max_length=200, help_text="The full title of the document")
    description = TextField(blank=True, null=True, help_text="Detailed info about this document")
    language = CharField(max_length=20, blank=True, null=True, help_text="BCP47/RFC5646 codes like en, es, fr-CA.")
    publisher = CharField(max_length=200, blank=True, null=True, help_text="The name of the organization publishing the document")
    version = CharField(max_length=200, blank=True, null=True, help_text="Document version or edition")
    #
    # Educational domain
    subjects = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'subjects'})
    education_levels = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'education_levels'})
    date_valid = DateField(blank=True, null=True, help_text="Date when document started being valid")
    date_retired = DateField(blank=True, null=True, help_text="Date when document stops being valid")
    #
    # Licensing
    license	= ForeignKey(Term, related_name='+', blank=True, null=True, on_delete=SET_NULL, limit_choices_to={'vocabulary__kind': 'license_kinds'})
    license_description	= TextField(blank=True, null=True, help_text="Full text of the document's licensing information")
    copyright_holder = CharField(max_length=200, blank=True, null=True, help_text="Name of organization that holds the copyright to the document")
    #
    # Digitization domain
    digitization_method = CharField(max_length=200, choices=DIGITIZATION_METHODS, help_text="Digitization method")
    source_doc = URLField(max_length=512, blank=True, help_text="Where the data of this document was imported from")
    publication_status	= CharField(max_length=30, choices=PUBLICATION_STATUSES, default=PUBLICATION_STATUSES.publicdraft)
    #
    # Publishing domain
    canonical_uri = URLField(max_length=512, null=True, blank=True, help_text="URI for the document used when publishing")
    source_uri = URLField(max_length=512, null=True, blank=True, help_text="External URI for imported document")
    source_id = CharField(max_length=100, blank=True, help_text="An external identifier (usually part of source_uri)")
    #
    # Metadata
    notes = TextField(blank=True, null=True, help_text="Additional notes about the document")
    date_created = DateTimeField(auto_now_add=True, help_text="When the standards document was added to repository.")
    date_modified = DateTimeField(auto_now=True, help_text="Date of last modification to document metadata.")
    extra_fields = JSONField(default=dict, blank=True)  # for data extensibility

    def __str__(self):
        return "{} ({})".format(self.title, self.id)

    def get_absolute_url(self):
        return "/" + self.jurisdiction.name + "/documents/" + self.id

    @property
    def uri(self):
        return self.get_absolute_url()

    @property
    def root(self):
        return StandardNode.objects.get(level=0, document=self)


    def get_children(self):
        self.root.get_children()



class StandardNodeManager(Manager):
    def get_queryset(self):
        return super(StandardNodeManager, self).get_queryset().prefetch_related(
            "document__jurisdiction",
            "document",
            "parent",
            "kind",
            "children",
            "subjects",
            "education_levels",
            "concept_terms",
        )

class StandardNode(MPTTModel):
    """
    An individual standard entry within the a standards document.
    """
    # IDs
    id = ShortUUIDField(primary_key=True, editable=False, prefix='S')
    #
    # Structural
    document = ForeignKey(StandardsDocument, related_name="standardnodes", on_delete=CASCADE)
    parent = TreeForeignKey('self', on_delete=CASCADE, null=True, blank=True, related_name='children')
    kind = ForeignKey(Term, related_name='+', blank=True, null=True, on_delete=SET_NULL, limit_choices_to={'vocabulary__kind': 'curriculum_elements'})
    sort_order = FloatField(default=1.0)   # the position of node within parent
    #
    # Node attributes
    notation = CharField(max_length=200, blank=True, help_text="A human-referenceable code for this node")
    # alt_notations: TODO impl as ArrayField after move to Postgres DB
    list_id = CharField(max_length=50, blank=True, help_text="A character or symbol denoting the node position with a list")
    title = CharField(max_length=200, blank=True, help_text="An optional heading or abbreviated description")
    description	= TextField(help_text="Primary text that describes this node")
    language = CharField(max_length=20, blank=True, null=True, help_text="BCP47/RFC5646 codes like en, es, fr-CA.")
    #
    # Educational domain
    subjects = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'subjects'})
    education_levels = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'education_levels'})
    concept_terms = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'concept_terms'})
    concept_keywords = CharField(max_length=500, blank=True, null=True, help_text="Free form, comma-separated keywords")
    # MAYBE ADD
    # cognitive_process_dimensions	m2m --> Term.vocabulary[kind=cognitive_process_dimensions]
    # knowledge_dimensions		    m2m --> Term[kind=knowledge_dimensions]
    #
    # Publishing domain
    path = CharField(max_length=200, blank=True, help_text="Full path of node. Usually ends in notation.")
    canonical_uri = URLField(max_length=512, null=True, blank=True, help_text="URI for the standard node used when publishing")
    source_uri = URLField(max_length=512, null=True, blank=True, help_text="External URI for imported standard nodes")
    source_id = CharField(max_length=100, blank=True, help_text="An external identifier (usually part of source_uri)")
    #
    # Metadata
    notes = TextField(blank=True, null=True, help_text="Additional notes and supporting text")
    date_created = DateTimeField(auto_now_add=True, help_text="When the node was added to repository")
    date_modified = DateTimeField(auto_now=True, help_text="Date of last modification to node")
    extra_fields = JSONField(default=dict, blank=True)  # for data extensibility

    objects = StandardNodeManager()

    class Meta:
        # Make sure every document has at most one tree
        constraints = [
            UniqueConstraint(
                name="single_root_per_document",
                fields=["document", "tree_id"],
                condition=Q(level=0),
            )
        ]
        ordering = ('sort_order', )

    class MPTTMeta:
        order_insertion_by = ['sort_order']

    def __str__(self):
        description_start = self.description[0:30] + '..'
        return "{}({})".format(description_start, self.id)

    def get_absolute_url(self):
        return "/" + self.document.jurisdiction.name + "/standardnodes/" + self.id

    @property
    def uri(self):
        return self.get_absolute_url()

    def add_child(self, **kwargs):
        if "document" not in kwargs:
            kwargs["document"] = self.document
        return super().add_child(**kwargs)

    @property
    def relations(self):
        return StandardNodeRelation.objects.filter(Q(source=self) | Q(target=self))




# CROSSWALKS
################################################################################

CROSSWALK_DIGITIZATION_METHODS = Choices(
    ("manual_entry",        "Manual data entry"),
    ("spreadsheet_import",  "Imported from a standards crosswalks spreadsheet"),
    ("api_created",         "Created through the API"),
    ("bulk_import",         "Created using a crosswalks integration script"),
    ("human_judgments",     "Alignment judgment provided by human curriculum experts"),
    ("hackathon_import",    "Alignment judgment collected during October 2019 hackathon"),
    ("asn_import",          "Standards alignment data imported from Achievement Standards Network (ASN)"),
    ("case_import",         "Standards alignment data imported from CASE registry"),
    ("data_import",         "Standards alignment data imported from data"),
)


class StandardsCrosswalk(Model):
    """
    A standards crosswalks is a set of ``StandardNodeRelation`` s that describe
    a mapping between source curriculum nodes and a target curriculum nodes.
    """
    # IDs
    id = ShortUUIDField(primary_key=True, editable=False, prefix='SC')
    # uri = computed field = localhost + get_absolute_url()
    #
    # Crosswalk info
    jurisdiction = ForeignKey(Jurisdiction, related_name="crosswalks", on_delete=CASCADE, help_text='Jurisdiction of the crosswalk')
    title = CharField(max_length=200, help_text="The publicly visible title for this crosswalk")
    description = TextField(blank=True, null=True, help_text="Detailed info about this crosswalk")
    creator = CharField(max_length=200, blank=True, null=True, help_text="Person or organization that created this crosswalk")
    publisher = CharField(max_length=200, blank=True, null=True, help_text="The name of the organization publishing the crosswalk")
    version = CharField(max_length=200, blank=True, null=True, help_text="Crosswalks versioning info")
    #
    # Licensing
    license	= ForeignKey(Term, related_name='+', blank=True, null=True, on_delete=SET_NULL, limit_choices_to={'vocabulary__kind': 'license_kinds'})
    license_description	= TextField(blank=True, null=True, help_text="Description of the licensing of this crosswalks")
    copyright_holder = CharField(max_length=200, blank=True, null=True, help_text="Name of organization that holds the copyright to this crosswalk")
    #
    # Educational domain
    subjects = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'subjects'})
    education_levels = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'education_levels'})
    date_valid = DateField(blank=True, null=True, help_text="Date when document started being valid")
    date_retired = DateField(blank=True, null=True, help_text="Date when document stopped being valid")
    #
    # Educational domain
    subjects = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'subjects'})
    education_levels = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'education_levels'})
    date_valid = DateField(blank=True, null=True, help_text="Date when crosswalk becomes approved in publishing jurisdiction")
    date_retired = DateField(blank=True, null=True, help_text="Date when crosswalk stops being valid in publishing jurisdiction")
    #
    # Digitization domain
    digitization_method = CharField(max_length=200, choices=CROSSWALK_DIGITIZATION_METHODS, help_text="Digitization method")
    publication_status	= CharField(max_length=30, choices=PUBLICATION_STATUSES, default=PUBLICATION_STATUSES.publicdraft)


    def __str__(self):
        return "{} ({})".format(self.title, self.id)

    def get_absolute_url(self):
        return "/" + self.jurisdiction.name + "/standardscrosswalks/" + self.id

    @property
    def uri(self):
        return self.get_absolute_url()



class StandardNodeRelation(Model):
    """
    A relations between two ``StandardNode`` s.
    """
    id = ShortUUIDField(primary_key=True, editable=False, prefix='SR')
    #
    # Structural
    crosswalk = ForeignKey(StandardsCrosswalk, related_name="relations", on_delete=CASCADE)
    #
    # Edge domain
    source = ForeignKey(StandardNode, related_name="source_rels", on_delete=CASCADE)
    target = ForeignKey(StandardNode, related_name="target_rels", on_delete=CASCADE)
    kind = ForeignKey(Term, related_name='+', blank=True, null=True, on_delete=SET_NULL, limit_choices_to={'vocabulary__kind': 'standard_node_relation_kinds'})
    #
    # Publishing domain
    canonical_uri = URLField(max_length=512, null=True, blank=True, help_text="URI for this relation used when publishing")
    source_uri = URLField(max_length=512, null=True, blank=True, help_text="External URI for imported relation")
    #
    # Metadata
    notes = TextField(blank=True, null=True, help_text="Additional notes and supporting text")
    date_created = DateTimeField(auto_now_add=True, help_text="When the relation was added to repository")
    date_modified = DateTimeField(auto_now=True, help_text="Date of last modification to relation data")
    extra_fields = JSONField(default=dict, blank=True)  # for data extensibility

    def __str__(self):
        return str(self.source) + '--' + str(self.kind) + '-->' + str(self.target)

    def get_absolute_url(self):
        return "/" + self.crosswalk.jurisdiction.name + "/standardnoderels/" + self.id

    @property
    def uri(self):
        return self.get_absolute_url()
