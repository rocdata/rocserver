from django.db.models import CASCADE
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import FloatField
from django.db.models import ForeignKey
from django.db.models import IntegerField
from django.db.models import JSONField
from django.db.models import ManyToManyField
from django.db.models import Model
from django.db.models import SET_NULL
from django.db.models import TextField
from django.db.models import URLField
from django.db.models import UUIDField
from django.db.models import Q, UniqueConstraint
from django_countries.fields import CountryField
from model_utils import Choices
from mptt.models import MPTTModel
from mptt.models import TreeForeignKey

from standards.fields import CharIdField
from standards.models import Jurisdiction
from standards.models import Term
from standards.models import StandardNode
from standards.models.standards import PUBLICATION_STATUSES
from standards.utils import get_default_license
from standards.utils import get_default_content_standard_relation_kind



# CONTENT
################################################################################

CONTENTIMPORT_METHODS = Choices(
    ("manual_entry",        "Manual data entry"),
    ("spreadsheet_import",  "Imported from a spreadsheet of links"),
    ("api_created",         "Created through the API"),
    ("bulk_import",         "Created by a content metadata integration script"),
    ("kolibri_channel",     "Imported from Kolibri database"),
    ("studio_channel",      "Imported from Studio data"),
    ("khan_export",         "Imported from Khan Academy TSV data exports"),
)


class ContentCollection(Model):
    """
    A content collection in the form of an external website, content archive, or
    repository of open educational resources (OERs). Each collection is identified
    by a unique ``collection_id`` (str) and contains a tree of ``ContentNode`` s.
    For example, a website with learning resources, a YouTube channel or a Kolibri
    content channel.
    """
    id = CharIdField(primary_key=True, editable=False, prefix='CC', length=10)
    # uri = computed field = localhost + get_absolute_url()
    #
    # Collection info
    jurisdiction = ForeignKey(Jurisdiction, related_name="contentcollections", on_delete=CASCADE, help_text='Jurisdiction of this collection')
    name = CharField(max_length=200, help_text="Collection name")
    description = TextField(blank=True, null=True, help_text="Detailed info about this collection")
    thumbnail_url = URLField(max_length=512, blank=True, help_text="External thumbnail URL this collection")
    language = CharField(max_length=20, blank=True, null=True, help_text="BCP47/RFC5646 codes like en, es, fr-CA")
    country = CountryField(blank=True, null=True, help_text='Country where content collection was produced')
    publication_status = CharField(max_length=30, choices=PUBLICATION_STATUSES, default=PUBLICATION_STATUSES.publicdraft)
    #
    # Educational domain
    subjects = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'subjects'})
    education_levels = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'education_levels'})
    #
    # Content import method
    import_method = CharField(max_length=200, choices=CONTENTIMPORT_METHODS, help_text="Content import method")
    source_domain = CharField(max_length=200, blank=True, null=True, help_text="The domain name of the content collection (e.g. khanacademy.org)")
    source_url = URLField(max_length=512, blank=True, help_text="The web location for this content collection")
    collection_id = CharField(max_length=100, blank=True, help_text="The identifier for this collection in the external content repository")    
    version = CharField(max_length=200, blank=True, null=True, help_text="Collection version or edition")
    #
    # Licensing
    license = ForeignKey(Term, related_name='+', null=True, on_delete=SET_NULL,
        default=get_default_license, limit_choices_to={'vocabulary__kind': 'license_kinds'})
    license_description = TextField(blank=True, null=True, help_text="Full text of the collection licensing information")
    copyright_holder = CharField(max_length=200, blank=True, null=True, help_text="Name of organization that holds the copyright to this content")
    #
    # Metadata
    notes = TextField(blank=True, null=True, help_text="Additional notes about the collection")
    date_created = DateTimeField(auto_now_add=True, help_text="When the collection was added to the repository")
    date_modified = DateTimeField(auto_now=True, help_text="Date of last modification to collection metadata")
    extra_fields = JSONField(default=dict, blank=True)  # for data extensibility

    def __str__(self):
        return "{} ({})".format(self.name, self.id)

    def get_absolute_url(self):
        return "/" + self.jurisdiction.name + "/contentcollections/" + self.id

    @property
    def uri(self):
        return self.get_absolute_url()

    @property
    def root(self):
        return ContentNode.objects.get(level=0, collection=self)

    def get_children(self):
        self.root.get_children()





class ContentNode(MPTTModel):
    """
    A class that represents individual content items (learning resources) within
    a content collection. Each content node is identified by a ``source_id``
    (eg. database identifier within the ``source_domain``) and has ``source_url``
    where the content node can be accessed or downloaded from.
    Examples of content nodes include web pages, YouTube videos, and the content
    nodes within Kolibri content channels.
    """
    id = CharIdField(primary_key=True, editable=False, prefix='C', length=10)
    #
    # Structural
    collection = ForeignKey(ContentCollection, related_name="contentnodes", on_delete=CASCADE, help_text='Content collection this node is part of')
    parent = TreeForeignKey('self', on_delete=CASCADE, null=True, blank=True, related_name='children')
    kind = ForeignKey(Term, related_name='+', blank=True, null=True, on_delete=SET_NULL, limit_choices_to={'vocabulary__kind': 'contentnode_kinds'})
    sort_order = FloatField(default=1.0)   # the position of node within parent
    #
    # Content info
    title = CharField(max_length=200, help_text="Content node title")
    description = TextField(blank=True, help_text="Detailed description of content node")
    language = CharField(max_length=20, blank=True, null=True, help_text="BCP47/RFC5646 codes like en, es, fr-CA.")
    author = CharField(max_length=200, blank=True, help_text="Who created this content node?")
    aggregator = CharField(max_length=200, blank=True, help_text="Website or org. hosting the content collection")
    provider = CharField(max_length=200, blank=True, help_text="Organization that made the creation or distribution this content possible")
    size = IntegerField(blank=True, null=True, help_text="File storage size required (in bytes)")
    #
    # Educational domain
    subjects = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'subjects'})
    education_levels = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'education_levels'})
    concept_terms = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'concept_terms'})
    concept_keywords = CharField(max_length=500, blank=True, null=True, help_text="Free-form, comma-separated keywords for this content node")
    # TODO: tags = models.ManyToManyField(?, blank=True, related_name='tagged_contentnodes')
    # TODO? audience ~= educational_role ~= studio.role_visibility
    #
    # Content source info
    source_url = URLField(max_length=512, blank=True, help_text="The primary web location for this content node")
    source_domain = CharField(max_length=200, help_text="The domain name of the content source (e.g. khanacademy.org)")
    source_id = CharField(max_length=100, help_text="An identifier for this content item within the source domain (e.g. a database id)")
    content_id = UUIDField(blank=True, null=True, db_index=True, help_text="Content ID computed from source_domain and source_id")
    node_id = UUIDField(blank=True, null=True, editable=False, db_index=True, help_text="An identifier for the content node within the collection")
    #
    # Licensing
    license = ForeignKey(Term, related_name='+', null=True, on_delete=SET_NULL,
        default=get_default_license, limit_choices_to={'vocabulary__kind': 'license_kinds'})
    license_description = TextField(blank=True, null=True, help_text="Full text of the node's licensing information")
    copyright_holder = CharField(max_length=200, blank=True, null=True, help_text="Name of organization that holds the copyright to this content")
    #
    # Metadata
    date_created = DateTimeField(auto_now_add=True, help_text="When the node was added to the repository")
    date_modified = DateTimeField(auto_now=True, help_text="Date of last modification to node metadata")
    extra_fields = JSONField(default=dict, blank=True)  # for data extensibility


    class Meta:
        # Make sure every content collections has at most one tree
        constraints = [
            UniqueConstraint(
                name="single_root_per_collection",
                fields=["collection", "tree_id"],
                condition=Q(level=0),
            )
        ]
        ordering = ('sort_order', )

    class MPTTMeta:
        order_insertion_by = ['sort_order']

    def __str__(self):
        title_start = self.title[0:30] + '..'
        return "{}({})".format(title_start, self.id)

    def get_absolute_url(self):
        return "/" + self.collection.jurisdiction.name + "/contentnodes/" + self.id

    @property
    def uri(self):
        return self.get_absolute_url()

    def add_child(self, **kwargs):
        if "collection" not in kwargs:
            kwargs["collection"] = self.document
        return super().add_child(**kwargs)

    @property
    def relations(self):
        return ContentNodeRelation.objects.filter(Q(source=self) | Q(target=self))




class ContentNodeRelation(Model):
    """
    A relation between two ``ContentNode`` s.
    """
    id = CharIdField(primary_key=True, editable=False, prefix='CR', length=10)
    #
    # Structural
    jurisdiction = ForeignKey(Jurisdiction, related_name="contentnoderels", on_delete=CASCADE)
    #
    # Edge domain
    source = ForeignKey(ContentNode, related_name="source_rels", on_delete=CASCADE)
    kind = ForeignKey(Term, related_name='+', blank=True, null=True, on_delete=SET_NULL, limit_choices_to={'vocabulary__kind': 'content_node_relation_kinds'})
    target = ForeignKey(ContentNode, related_name="target_rels", on_delete=CASCADE)
    #
    # Publishing domain
    canonical_uri = URLField(max_length=512, null=True, blank=True, help_text="URI for this relation used when publishing")
    source_uri = URLField(max_length=512, null=True, blank=True, help_text="External URI of an imported relation")
    #
    # Metadata
    notes = TextField(blank=True, null=True, help_text="Additional notes and supporting text")
    date_created = DateTimeField(auto_now_add=True, help_text="When the relation was added to repository")
    date_modified = DateTimeField(auto_now=True, help_text="Date of last modification to relation data")
    extra_fields = JSONField(default=dict, blank=True)  # for data extensibility

    def __str__(self):
        return str(self.source) + '--' + str(self.kind) + '-->' + str(self.target)

    def get_absolute_url(self):
        return "/" + self.jurisdiction.name + "/contentnoderels/" + self.id

    @property
    def uri(self):
        return self.get_absolute_url()








# CONTENT CORRELATIONS
################################################################################

CONTENT_CORRELATION_DIGITIZATION_METHODS = Choices(
    ("manual_entry",        "Manual data entry"),
    ("spreadsheet_import",  "Imported from a content correlation spreadsheet"),
    ("api_created",         "Created through the API"),
    ("bulk_import",         "Created using a content correlations integration script"),
    ("human_judgments",     "Curriculum alignment judgment provided by human curriculum experts"),
    ("data_import",         "Curriculum alignment alignment data imported from data"),
    ("ka_import",           "Curriculum alignment alignment data imported from Achievement Standards Network (ASN)"),
    ("kolibri_import",      "Curriculum alignment data imported from Kolibri channel DB"),
    ("studio_import",       "Curriculum alignment data imported from Kolibri Studio DB"),
)


class ContentCorrelation(Model):
    """
    A content correlation is a collection of content<->standard relations that
    encode the curriculum information between collections of content nodes
    and the curriculum standards nodes.
    """
    # IDs
    id = CharIdField(primary_key=True, editable=False, prefix='CS')
    # uri = computed field = localhost + get_absolute_url()
    #
    # Content correlation info
    jurisdiction = ForeignKey(Jurisdiction, related_name="contentcorrelations", on_delete=CASCADE, help_text='Jurisdiction of content correlations')
    title = CharField(max_length=200, help_text="The publicly visible title for this content correlation")
    description = TextField(blank=True, null=True, help_text="Detailed info about this content correlation")
    creator = CharField(max_length=200, blank=True, null=True, help_text="Person or organization that created this content correlation")
    publisher = CharField(max_length=200, blank=True, null=True, help_text="The name of the organization publishing the content correlation")
    version = CharField(max_length=200, blank=True, null=True, help_text="Content correlation versioning info")
    #
    # Licensing
    license = ForeignKey(Term, related_name='+', null=True, on_delete=SET_NULL,
        default=get_default_license, limit_choices_to={'vocabulary__kind': 'license_kinds'})
    license_description = TextField(blank=True, null=True, help_text="Description of the licensing of this content correlation")
    copyright_holder = CharField(max_length=200, blank=True, null=True, help_text="Name of organization that holds the copyright to this content correlation")
    #
    # Educational domain
    subjects = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'subjects'})
    education_levels = ManyToManyField(Term, blank=True, related_name="+", limit_choices_to={'vocabulary__kind': 'education_levels'})
    #
    # Digitization domain
    digitization_method = CharField(max_length=200, choices=CONTENT_CORRELATION_DIGITIZATION_METHODS, help_text="Digitization method")
    publication_status = CharField(max_length=30, choices=PUBLICATION_STATUSES, default=PUBLICATION_STATUSES.publicdraft)

    def __str__(self):
        return "{} ({})".format(self.title, self.id)

    def get_absolute_url(self):
        return "/" + self.jurisdiction.name + "/contentcorrelations/" + self.id

    @property
    def uri(self):
        return self.get_absolute_url()




class ContentStandardRelation(Model):
    """
    Describes an association between a content node and a standard node that
    indicates curriculum alignment of type ``kind`` (default ``majorAlignment``).
    """
    id = CharIdField(primary_key=True, editable=False, prefix='CSR', length=10)
    #
    # Structural
    correlation = ForeignKey(ContentCorrelation, related_name="relations", on_delete=CASCADE)
    #
    # Edge domain
    contentnode = ForeignKey(ContentNode, related_name="standards_rels", on_delete=CASCADE, help_text='The content node (source)')
    kind = ForeignKey(Term, related_name='+', null=True, on_delete=SET_NULL,
        default=get_default_content_standard_relation_kind, # = majorCorrelation
        limit_choices_to={'vocabulary__kind': 'content_standard_relation_kinds'})
    standardnode = ForeignKey(StandardNode, related_name="content_rels", on_delete=CASCADE, help_text='The standard node (target)')
    #
    # Publishing domain
    canonical_uri = URLField(max_length=512, null=True, blank=True, help_text="URI for this relation used when publishing")
    source_uri = URLField(max_length=512, null=True, blank=True, help_text="External URI for imported relations")
    #
    # Metadata
    notes = TextField(blank=True, null=True, help_text="Additional notes and supporting text")
    date_created = DateTimeField(auto_now_add=True, help_text="When the relation was added to the repository")
    date_modified = DateTimeField(auto_now=True, help_text="Date of last modification to relation data")
    extra_fields = JSONField(default=dict, blank=True)  # for data extensibility

    def __str__(self):
        return str(self.contentnode) + '--' + str(self.kind) + '-->' + str(self.standardnode)

    def get_absolute_url(self):
        return "/" + self.correlation.jurisdiction.name + "/contentstandardrels/" + self.id

    @property
    def uri(self):
        return self.get_absolute_url()

