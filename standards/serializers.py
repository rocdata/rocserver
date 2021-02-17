import functools

from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers
from rest_framework.reverse import reverse

from standards.models import Jurisdiction, UserProfile
from standards.models import ControlledVocabulary, Term
from standards.models import TermRelation

from standards.models import StandardsDocument, StandardNode
from standards.models import StandardsCrosswalk, StandardNodeRelation
from standards.models import ContentCollection, ContentNode, ContentNodeRelation
from standards.models import ContentCorrelation, ContentStandardRelation




# ROC HYPERLINK FIELDS
################################################################################

class MultiKeyHyperlinkField(serializers.HyperlinkedRelatedField):
    """
    Used to create and parse ROC resources hyperlinks that have multiple keys.
    Subclasses must define ``view_name``, ``queryset``, ``url_kwargs_mapping``
    (used by ``get_url``), and ``lookup_kwargs_mapping`` (used by ``get_object``).
    """

    def rgetattr(self, obj, attrpath):
        """
        A fancy version of ``getattr`` that allows getting dot-separated nested attributes
        like ``jurisdiction.id`` used in ``MultiKeyHyperlinkField`` mapping dicst.
        This code is inspired by solution in https://stackoverflow.com/a/31174427.
        """
        return functools.reduce(getattr, [obj] + attrpath.split('.'))

    def get_url(self, obj, view_name, request, format):
        url_kwargs = dict(
            (urlparam, self.rgetattr(obj, attrpath))
            for urlparam, attrpath in self.url_kwargs_mapping.items()
        )
        if "format" in request.GET:
            # This is a hack to avoid ?format=api appended to URIs by preserve_builtin_query_params
            # github.com/encode/django-rest-framework/blob/master/rest_framework/reverse.py#L12-L29
            request.GET._mutable = True
            del request.GET["format"]
            request.GET._mutable = False
        return reverse(view_name, kwargs=url_kwargs, request=request)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = dict(
            (kwarg, view_kwargs[url_kwarg])
            for kwarg, url_kwarg in self.lookup_kwargs_mapping.items()
        )
        return self.get_queryset().get(**lookup_kwargs)

    def use_pk_only_optimization(self):
        # via
        # https://github.com/django-json-api/django-rest-framework-json-api/issues/489#issuecomment-428002360
        return False


class JurisdictionScopedHyperlinkField(MultiKeyHyperlinkField):
    # /<jurisdiction_name>/*/<pk>
    url_kwargs_mapping = {
        "jurisdiction_name": "jurisdiction.name",
        "pk": "id",
    }
    lookup_kwargs_mapping = {
        "jurisdiction__name": "jurisdiction_name",
        "id": "pk",
    }


# JURISDICTION

class JurisdictionHyperlinkField(MultiKeyHyperlinkField):
    # /<name> ==  Jurisdiction namespace root
    view_name = 'jurisdiction-detail'
    queryset = Jurisdiction.objects.all()
    url_kwargs_mapping = {"name": "name"}
    lookup_kwargs_mapping = {"name": "name"}



# VOCABULARIES AND TERMS

class ControlledVocabularyHyperlinkField(MultiKeyHyperlinkField):
    # /<jurisdiction__name>/terms/<name>
    view_name = 'jurisdiction-vocabulary-detail'
    queryset = ControlledVocabulary.objects.all()
    url_kwargs_mapping = {
        "jurisdiction_name": "jurisdiction.name",
        "name": "name",
    }
    lookup_kwargs_mapping = {
        "jurisdiction__name": "jurisdiction_name",
        "name": "name",
    }

class TermHyperlinkField(MultiKeyHyperlinkField):
    # /<jurisdiction_name>/terms/<vocabulary_name>/<path>
    view_name = 'jurisdiction-vocabulary-term-detail'
    queryset = Term.objects.all()
    url_kwargs_mapping = {
        "jurisdiction_name": "vocabulary.jurisdiction.name",
        "vocabulary_name": "vocabulary.name",
        "path": "path",
    }
    lookup_kwargs_mapping = {
        "vocabulary__jurisdiction__name": "jurisdiction_name",
        "vocabulary__name": "vocabulary_name",
        "path": "path",
    }

class TermRelationHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/termrels/<pk>
    view_name = 'jurisdiction-termrelation-detail'
    queryset = TermRelation.objects.all()



# CURRICULUM STANDARDS

class StandardsDocumentHyperlinkHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/documents/<pk>
    view_name = 'jurisdiction-document-detail'
    queryset = StandardsDocument.objects.all()

class StandardNodeHyperlinkField(MultiKeyHyperlinkField):
    # /<jurisdiction_name>/standardnodes/<pk>
    view_name = 'jurisdiction-standardnode-detail'
    queryset = StandardNode.objects.all()
    url_kwargs_mapping = {
        "jurisdiction_name": "document.jurisdiction.name",
        "pk": "id",
    }
    lookup_kwargs_mapping = {
        "document__jurisdiction__name": "jurisdiction_name",
        "id": "pk",
    }


# CROSSWALKS

class StandardsCrowsswalkHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/standardscrosswalks/<pk>
    view_name = 'jurisdiction-standardscrosswalk-detail'
    queryset = StandardsCrosswalk.objects.all()

class StandardNodeRelationHyperlinkField(MultiKeyHyperlinkField):
    # /<jurisdiction_name>/standardnoderels/<pk>
    view_name = 'jurisdiction-standardnoderel-detail'
    queryset = StandardNodeRelation.objects.all()
    url_kwargs_mapping = {
        "jurisdiction_name": "crosswalk.jurisdiction.name",
        "pk": "id",
    }
    lookup_kwargs_mapping = {
        "crosswalk__jurisdiction__name": "jurisdiction_name",
        "id": "pk",
    }




# CONTENT

class ContentCollectionHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/contentcollections/<pk>
    view_name = 'jurisdiction-contentcollection-detail'
    queryset = ContentCollection.objects.all()

class ContentNodeHyperlinkField(MultiKeyHyperlinkField):
    # /<jurisdiction_name>/contentnodes/<pk>
    view_name = 'jurisdiction-contentnode-detail'
    queryset = ContentNode.objects.all()
    url_kwargs_mapping = {
        "jurisdiction_name": "collection.jurisdiction.name",
        "pk": "id",
    }
    lookup_kwargs_mapping = {
        "collection__jurisdiction__name": "jurisdiction_name",
        "id": "pk",
    }

class ContentNodeRelationHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/contentnoderels/<pk>
    view_name = 'jurisdiction-contentnoderel-detail'
    queryset = ContentNodeRelation.objects.all()


# CONTENT CORRELATIONS

class ContentCorrelationHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/contentcorrelations/<pk>
    view_name = 'jurisdiction-contentcorrelation-detail'
    queryset = ContentCorrelation.objects.all()

class ContentStandardRelationHyperlinkField(MultiKeyHyperlinkField):
    # /<jurisdiction_name>/contentstandardrels/<pk>
    view_name = 'jurisdiction-contentstandardrel-detail'
    queryset = ContentStandardRelation.objects.all()
    url_kwargs_mapping = {
        "jurisdiction_name": "correlation.jurisdiction.name",
        "pk": "id",
    }
    lookup_kwargs_mapping = {
        "correlation__jurisdiction__name": "jurisdiction_name",
        "id": "pk",
    }




# JURISDICTION
################################################################################

class JurisdictionSerializer(serializers.ModelSerializer):
    vocabularies = ControlledVocabularyHyperlinkField(many=True, required=False)
    documents = serializers.SerializerMethodField()
    crosswalks = serializers.SerializerMethodField()
    contentcollections = serializers.SerializerMethodField()
    contentcorrelations = serializers.SerializerMethodField()

    class Meta:
        model = Jurisdiction
        fields = [
            # "id",  # internal identifiers; need not be exposed to users
            "uri",
            "name",
            "display_name",
            "country",
            "language",
            "alt_name",
            "notes",
            "vocabularies",
            "documents",
            "crosswalks",
            "contentcollections",
            "contentcorrelations",
        ]

    # The following four are done as a method fields because the serializers are
    # only defined later in this source file.

    def get_documents(self, obj):
        return [
            reverse(
                "jurisdiction-document-detail",
                kwargs= {"jurisdiction_name": doc.jurisdiction.name, "pk": doc.id},
                request=self.context["request"],
            ) for doc in obj.documents.all()
        ]

    def get_crosswalks(self, obj):
        return [
            reverse(
                "jurisdiction-standardscrosswalk-detail",
                kwargs= {"jurisdiction_name": sc.jurisdiction.name, "pk": sc.id},
                request=self.context["request"],
            ) for sc in obj.crosswalks.all()
        ]

    def get_contentcollections(self, obj):
        return [
            reverse(
                "jurisdiction-contentcollection-detail",
                kwargs= {"jurisdiction_name": cc.jurisdiction.name, "pk": cc.id},
                request=self.context["request"],
            )
            for cc in obj.contentcollections.all()
        ]

    def get_contentcorrelations(self, obj):
        return [
            reverse(
                "jurisdiction-contentcorrelation-detail",
                kwargs= {"jurisdiction_name": cs.jurisdiction.name, "pk": cs.id},
                request=self.context["request"],
            )
            for cs in obj.contentcorrelations.all()
        ]


# VOCABULARIES, TERMS, and TERM RELATIONS
################################################################################

class ControlledVocabularySerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(required=True)
    terms = TermHyperlinkField(many=True, required=False)

    class Meta:
        model = ControlledVocabulary
        fields = [
            # "id",  # internal identifiers; need not be exposed to users
            "jurisdiction",
            "uri",
            "name",
            "label",
            "alt_label",
            "hidden_label",
            "description",
            "language",
            "source",
            "notes",
            "date_created",
            "date_modified",
            "extra_fields",
            "creator",
            "terms",
        ]


class TermSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(source='vocabulary.jurisdiction', required=True)
    vocabulary = ControlledVocabularyHyperlinkField(required=True)

    class Meta:
        model = Term
        fields = [
            # "id",  # internal identifiers; need not be exposed to users
            "jurisdiction",
            "vocabulary",
            "uri",
            "path",
            "label",
            "alt_label",
            "hidden_label",
            "notation",
            "definition",
            "notes",
            "language",
            "sort_order",
            "date_created",
            "date_modified",
            "extra_fields",
        ]


class TermRelationSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(required=True)
    source = TermHyperlinkField(required=True)
    target = TermHyperlinkField(required=False)

    class Meta:
        model = TermRelation
        fields = [
            "id",
            "uri",
            "jurisdiction",
            "source",
            "target_uri",
            "target",
            "kind",
            "notes",
            "date_created",
            "date_modified",
            "extra_fields",
        ]


# STANDARDS
################################################################################

class StandardsDocumentSerializer(serializers.ModelSerializer):
    root_node_id = serializers.SerializerMethodField()
    jurisdiction = JurisdictionHyperlinkField(required=True)
    children = StandardNodeHyperlinkField(source='root.children', many=True)
    subjects = TermHyperlinkField(many=True)
    education_levels = TermHyperlinkField(many=True)
    license = TermHyperlinkField()

    class Meta:
        model = StandardsDocument
        fields = '__all__'

    def get_root_node_id(self, obj):
        try:
            return StandardNode.objects.get(level=0, document_id=obj.id).id
        except StandardNode.DoesNotExist:
            return None

class FullStandardsDocumentSerializer(StandardsDocumentSerializer):
    """
    Full standard document serialization recursive traversal of standard nodes.
    """
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return [
            FullStandardNodeSerializer(node, context=self.context).data
            for node in obj.root.children.all()
        ]


class StandardNodeSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField()
    jurisdiction = JurisdictionHyperlinkField(source='document.jurisdiction', required=False) # check this...
    document = StandardsDocumentHyperlinkHyperlinkField(required=True)
    parent = StandardNodeHyperlinkField()
    kind = TermHyperlinkField()
    subjects = TermHyperlinkField(many=True)
    education_levels = TermHyperlinkField(many=True)
    concept_terms = TermHyperlinkField(many=True)
    children = StandardNodeHyperlinkField(many=True)

    class Meta:
        model = StandardNode
        fields = '__all__'

    def get_uri(self, obj):
        return obj.uri


class FullStandardNodeSerializer(StandardNodeSerializer):
    """
    Recursive variant of ``StandardNodeSerializer`` to use for ``/full`` action.
    """
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return [
            FullStandardNodeSerializer(node, context=self.context).data
            for node in obj.children.all()
        ]


# STANDARDS CROSSWALKS
################################################################################

class StandardsCrosswalkSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(required=True)
    license = TermHyperlinkField()
    subjects = TermHyperlinkField(many=True)
    education_levels = TermHyperlinkField(many=True)
    relations = StandardNodeRelationHyperlinkField(many=True)

    class Meta:
        model = StandardsCrosswalk
        fields = '__all__'


class StandardNodeRelationSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(source='crosswalk.jurisdiction', required=False)
    crosswalk = StandardsCrowsswalkHyperlinkField(required=True)
    source = StandardNodeHyperlinkField(style={'base_template': 'input.html'})
    kind = TermHyperlinkField()
    target = StandardNodeHyperlinkField(style={'base_template': 'input.html'})

    class Meta:
        model = StandardNodeRelation
        fields = '__all__'





# CONTENT
################################################################################

class ContentCollectionSerializer(CountryFieldMixin, serializers.ModelSerializer):
    uri = serializers.SerializerMethodField()
    jurisdiction = JurisdictionHyperlinkField(required=True)
    license = TermHyperlinkField()
    subjects = TermHyperlinkField(many=True)
    education_levels = TermHyperlinkField(many=True)
    children = ContentNodeHyperlinkField(source='root.children', many=True)

    class Meta:
        model = ContentCollection
        fields = '__all__'
    
    def get_uri(self, obj):
        return obj.uri

class FullContentCollectionSerializer(ContentCollectionSerializer):
    """
    Full content collection serialization recursive traversal of content nodes.
    """
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return [
            FullContentNodeSerializer(node, context=self.context).data
            for node in obj.root.children.all()
        ]


class ContentNodeSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField()
    jurisdiction = JurisdictionHyperlinkField(source='document.jurisdiction', required=False)
    collection = ContentCollectionHyperlinkField(required=True)
    parent = ContentNodeHyperlinkField()
    kind = TermHyperlinkField()
    subjects = TermHyperlinkField(many=True)
    education_levels = TermHyperlinkField(many=True)
    concept_terms = TermHyperlinkField(many=True)
    license = TermHyperlinkField()
    children = ContentNodeHyperlinkField(many=True)

    class Meta:
        model = ContentNode
        fields = '__all__'

    def get_uri(self, obj):
        return obj.uri


class FullContentNodeSerializer(ContentNodeSerializer):
    """
    Recursive variant of ``ContentNodeSerializer`` to use for ``/full`` action.
    """
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return [
            FullContentNodeSerializer(node, context=self.context).data
            for node in obj.children.all()
        ]


class ContentNodeRelationSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(required=True)
    source = ContentNodeHyperlinkField(style={'base_template': 'input.html'})
    kind = TermHyperlinkField()
    target = ContentNodeHyperlinkField(style={'base_template': 'input.html'})

    class Meta:
        model = ContentNodeRelation
        fields = '__all__'



# CONTENT CORRELATIONS
################################################################################

class ContentCorrelationSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(required=True)
    license = TermHyperlinkField()
    subjects = TermHyperlinkField(many=True)
    education_levels = TermHyperlinkField(many=True)
    relations = ContentStandardRelationHyperlinkField(many=True)

    class Meta:
        model = ContentCorrelation
        fields = '__all__'


class ContentStandardRelationSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(source='correlation.jurisdiction', required=False)
    correlation = ContentCorrelationHyperlinkField(required=True)
    contentnode = ContentNodeHyperlinkField(style={'base_template': 'input.html'})
    kind = TermHyperlinkField()
    standardnode = StandardNodeHyperlinkField(style={'base_template': 'input.html'})

    class Meta:
        model = ContentStandardRelation
        fields = '__all__'
