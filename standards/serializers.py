import functools


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
            (kwarg, view_kwargs[urlparam])
            for kwarg, urlparam in self.lookup_kwargs_mapping.items()
        )
        return self.get_queryset().get(**lookup_kwargs)

    def use_pk_only_optimization(self):
        # via
        # https://github.com/django-json-api/django-rest-framework-json-api/issues/489#issuecomment-428002360
        return False


class JurisdictionHyperlinkField(MultiKeyHyperlinkField):
    # /<name> ==  Jurisdiction namespace root
    view_name = 'jurisdiction-detail'
    queryset = Jurisdiction.objects.all()
    url_kwargs_mapping = {"name": "name"}
    lookup_kwargs_mapping = {"name": "name"}


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

class StandardsDocumentHyperlinkHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/documents/<pk>
    view_name = 'jurisdiction-document-detail'
    queryset = StandardsDocument.objects.all()

class StandardNodeHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/standardnodes/<pk>
    view_name = 'jurisdiction-standardnode-detail'
    queryset = StandardNode.objects.all()

class StandardsCrowsswalkHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/standardscrosswalks/<pk>
    view_name = 'jurisdiction-standardscrosswalk-detail'
    queryset = StandardsCrosswalk.objects.all()

class StandardNodeRelationHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/standardnoderels/<pk>
    view_name = 'jurisdiction-standardnoderel-detail'
    queryset = StandardNodeRelation.objects.all()



class ContentCollectionHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/contentcollections/<pk>
    view_name = 'jurisdiction-contentcollection-detail'
    queryset = ContentCollection.objects.all()

class ContentNodeHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/contentnodes/<pk>
    view_name = 'jurisdiction-contentnode-detail'
    queryset = ContentNode.objects.all()

class ContentNodeRelationHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/contentnoderels/<pk>
    view_name = 'jurisdiction-contentnoderel-detail'
    queryset = ContentNodeRelation.objects.all()

class ContentCorrelationHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/contentcorrelations/<pk>
    view_name = 'jurisdiction-contentcorrelation-detail'
    queryset = ContentCorrelation.objects.all()

class ContentStandardRelationHyperlinkField(JurisdictionScopedHyperlinkField):
    # /<jurisdiction_name>/contentstandardrels/<pk>
    view_name = 'jurisdiction-contentstandardrel-detail'
    queryset = ContentStandardRelation.objects.all()





# OLD CUSTOM HYPERLINK FIELDS
################################################################################

class OLDJurisdictionHyperlink(serializers.HyperlinkedRelatedField):
    # /terms/<jurisdiction__name>
    # We define these as class attributes so we don't need to pass them as args.
    view_name = 'api-juri-detail'
    queryset = Jurisdiction.objects.all()

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'name': obj.name
        }
        if 'format' in request.GET:
            # This is a hack to avoid ?format=api appended to URIs by preserve_builtin_query_params
            # github.com/encode/django-rest-framework/blob/master/rest_framework/reverse.py#L12-L29
            request.GET._mutable = True
            del request.GET['format']
            request.GET._mutable = False
        return reverse(view_name, kwargs=url_kwargs, request=request)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            'name': view_kwargs['name'],
        }
        return self.get_queryset().get(**lookup_kwargs)

    def use_pk_only_optimization(self):
        # via
        # https://github.com/django-json-api/django-rest-framework-json-api/issues/489#issuecomment-428002360
        return False


class ControlledVocabularyHyperlink(serializers.HyperlinkedRelatedField):
    # /terms/<jurisdiction__name>/<name>
    # We define these as class attributes so we don't need to pass them as args.
    view_name = 'api-juri-vocab-detail'
    queryset = ControlledVocabulary.objects.select_related('jurisdiction').all()

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'jurisdiction__name': obj.jurisdiction.name,
            'name': obj.name
        }
        if 'format' in request.GET:
            # This is a hack to avoid ?format=api appended to URIs by preserve_builtin_query_params
            # github.com/encode/django-rest-framework/blob/master/rest_framework/reverse.py#L12-L29
            request.GET._mutable = True
            del request.GET['format']
            request.GET._mutable = False
        return reverse(view_name, kwargs=url_kwargs, request=request)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            'jurisdiction__name': view_kwargs['jurisdiction__name'],
            'name': view_kwargs['name'],
        }
        return self.get_queryset().get(**lookup_kwargs)

    def use_pk_only_optimization(self):
        # via
        # https://github.com/django-json-api/django-rest-framework-json-api/issues/489#issuecomment-428002360
        return False

class TermHyperlink(serializers.HyperlinkedRelatedField):
    # /terms/<jurisdiction__name>/<name>
    # We define these as class attributes so we don't need to pass them as args.
    view_name = 'api-juri-vocab-term-detail'
    queryset = Term.objects.select_related('vocabulary', 'vocabulary__jurisdiction').all()

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'vocabulary__jurisdiction__name': obj.vocabulary.jurisdiction.name,
            'vocabulary__name': obj.vocabulary.name,
            'path': obj.path,
        }
        if 'format' in request.GET:
            # This is a hack to avoid ?format=api appended to URIs by preserve_builtin_query_params
            # github.com/encode/django-rest-framework/blob/master/rest_framework/reverse.py#L12-L29
            request.GET._mutable = True
            del request.GET['format']
            request.GET._mutable = False
        return reverse(view_name, kwargs=url_kwargs, request=request)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            'vocabulary__jurisdiction__name': view_kwargs['vocabulary__jurisdiction__name'],
            'vocabulary__name': view_kwargs['vocabulary__name'],
            'path': view_kwargs['path'],
        }
        return self.get_queryset().get(**lookup_kwargs)

    def use_pk_only_optimization(self):
        # via
        # https://github.com/django-json-api/django-rest-framework-json-api/issues/489#issuecomment-428002360
        return False









# OLD HIERARCHICAL TERMS API
################################################################################


class ControlledVocabularySerializer(serializers.ModelSerializer):
    jurisdiction = OLDJurisdictionHyperlink(required=True)
    terms = TermHyperlink(many=True, required=False)

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
    jurisdiction = OLDJurisdictionHyperlink(source='vocabulary.jurisdiction', required=True)
    vocabulary = ControlledVocabularyHyperlink(required=True)

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
    jurisdiction = OLDJurisdictionHyperlink(required=True)
    source = TermHyperlink(required=True)
    target = TermHyperlink(required=False)

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



# JURISDICTION
################################################################################

class JurisdictionSerializer(serializers.ModelSerializer):
    vocabularies = ControlledVocabularyHyperlink(many=True, required=False)
    documents = serializers.SerializerMethodField()

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
        ]

    def get_documents(self, obj):
        """
        This is done as a method field because `StandardsDocumentSerializer` is
        only defined later in this source file.
        """
        document_hyperlinks = [
            reverse(
                "jurisdiction-document-detail",
                kwargs= {"jurisdiction_name": doc.jurisdiction.name, "pk": doc.id},
                request=self.context["request"],
            )
            for doc in obj.documents.all()
        ]
        return document_hyperlinks



# STANDARDS
################################################################################

class StandardsDocumentSerializer(serializers.ModelSerializer):
    root_node_id = serializers.SerializerMethodField()
    jurisdiction = JurisdictionHyperlinkField(required=True)

    class Meta:
        model = StandardsDocument
        fields = '__all__'

    def get_root_node_id(self, obj):
        try:
            return StandardNode.objects.get(level=0, document_id=obj.id).id
        except StandardNode.DoesNotExist:
            return None


class StandardNodeSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(source='document.jurisdiction', required=False) # check this...
    document = StandardsDocumentHyperlinkHyperlinkField(required=True)

    class Meta:
        model = StandardNode
        fields = '__all__'


# STANDARDS CROSSWALKS
################################################################################

class StandardsCrosswalkSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(required=True)

    class Meta:
        model = StandardsCrosswalk
        fields = '__all__'


class StandardNodeRelationSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(source='crosswalk.jurisdiction', required=False)
    crosswalk = StandardsCrowsswalkHyperlinkField(required=True)

    class Meta:
        model = StandardNodeRelation
        fields = '__all__'





# CONTENT
################################################################################

class ContentCollectionSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(required=True)

    class Meta:
        model = ContentCollection
        fields = '__all__'

class ContentNodeSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(required=False)
    collection = ContentCollectionHyperlinkField(required=True)

    class Meta:
        model = ContentNode
        fields = '__all__'


class ContentNodeRelationSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(required=True)

    class Meta:
        model = ContentNodeRelation
        fields = '__all__'


# CONTENT CORRELATIONS
################################################################################

class ContentCorrelationSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(required=True)

    class Meta:
        model = ContentCorrelation
        fields = '__all__'

class ContentStandardRelationSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlinkField(required=False)
    correlation = ContentCorrelationHyperlinkField(required=True)

    class Meta:
        model = ContentStandardRelation
        fields = '__all__'
