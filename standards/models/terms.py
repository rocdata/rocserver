from django.db.models import CASCADE
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import FloatField
from django.db.models import ForeignKey
from django.db.models import JSONField
from django.db.models import Manager
from django.db.models import Model
from django.db.models import TextField
from django.db.models import URLField
from model_utils import Choices
from standards.fields import ShortUUIDField

from .jurisdictions import Jurisdiction


# CONTROLLED VOCABULARIES
################################################################################

SPECIAL_VOCABULARY_KINDS = Choices(
    ('education_levels',     'Local education levels (local grade levels)'),
    ('subjects',             'Local academic subjects'),
    ('topic_terms',          'Global topic taxonomy terms'),
    ('curriculum_elements',  'Curriculum standard elements'),
    ('license_kinds',        'License kinds'),
    # THESE NEED DISCUSSION BEFORE INCLUSION
    # ('cognitive_process_dimensions', "Cognitive Process Dimensions (Bloom's taxonomy level)"),
    # ('knowledge_dimensions',         "Knowledge dimensions"),
)


class ControlledVocabulary(Model):
    """
    A set of controlled terms served under /terms/{juri}/{self.name}/.
    This is a Django model (DB table) that closely resembles skos:ConceptScheme.
    """
    id = ShortUUIDField(primary_key=True, editable=False, prefix='V')
    # uri, computed field, e.g., https://rocdata.global/terms/{jury}/{self.name}
    jurisdiction = ForeignKey(Jurisdiction, related_name="vocabularies", on_delete=CASCADE)
    kind = CharField(max_length=50, blank=True, null=True, choices=SPECIAL_VOCABULARY_KINDS, help_text="Vocabulary kind (e.g. education_levels)")
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
    #
    # Structural
    jurisdiction = ForeignKey(Jurisdiction, related_name="termrelations", on_delete=CASCADE)
    #
    # Edge domain
    source = ForeignKey(Term, related_name='source_rels', on_delete=CASCADE)
    target_uri = CharField(max_length=500, null=True, blank=True)
    # for internal references target_uri is NULL and and target is a FK
    target = ForeignKey(Term, related_name='target_rels', blank=True, null=True, on_delete=CASCADE)
    kind = CharField(max_length=32, choices=TERM_REL_KINDS)
    #
    # Metadata
    notes = TextField(blank=True, help_text="Additional notes about the relation")
    date_created = DateTimeField(auto_now_add=True)
    date_modified = DateTimeField(auto_now=True)
    extra_fields = JSONField(default=dict, blank=True)  # for data extensibility


    def __str__(self):
        target_str = self.target_uri if self.target_uri else str(self.target)
        return str(self.source) + '--' + self.kind + '-->' + target_str

    def get_absolute_url(self):
        return "/termrels/" + self.jurisdiction.name + '/' + self.id

    @property
    def uri(self):
        return self.get_absolute_url()
