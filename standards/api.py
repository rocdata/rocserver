from collections import OrderedDict

from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect
from rest_framework import serializers, viewsets, views, status, response
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.reverse import reverse


from standards.models import Jurisdiction
from standards.serializers import JurisdictionSerializer
from standards.publishing import get_publishing_context

from standards.models import ControlledVocabulary, Term, TermRelation
from standards.serializers import ControlledVocabularySerializer
from standards.serializers import TermSerializer, TermRelationSerializer

from standards.models import StandardsDocument, StandardNode
from standards.models import StandardsCrosswalk, StandardNodeRelation
from standards.serializers import StandardsDocumentSerializer, StandardNodeSerializer
from standards.serializers import StandardsCrosswalkSerializer, StandardNodeRelationSerializer

from standards.models import ContentCollection, ContentNode, ContentNodeRelation
from standards.models import ContentCorrelation, ContentStandardRelation
from standards.serializers import ContentCollectionSerializer, ContentNodeSerializer, ContentNodeRelationSerializer
from standards.serializers import ContentCorrelationSerializer, ContentStandardRelationSerializer




# HELPERS
################################################################################

def LargeResultsSetPagination(size=100):
    class CustomPagination(PageNumberPagination):
        page_size = size
        page_size_query_param = "page_size"
        max_page_size = page_size * 10
    return CustomPagination


class MultipleFieldLookupMixin:
    """
    Apply this mixin to any view or viewset to get multiple field filtering based
    on a `lookup_fields` attribute, instead of the default single field filtering.
    via django-rest-framework.org/api-guide/generic-views/#creating-custom-mixins
    """
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs[field]:                  # Ignore empty fields.
                filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)  # Lookup the object
        self.check_object_permissions(self.request, obj)
        return obj


TREE_DATA_SKIP_KEYS = ["lft", "rght", "tree_id"]   # MPTT internal impl. details

class CustomHTMLRendererRetrieve:
    """
    Custom retrieve method that skips the serialization when rendering HTML, via
    django-rest-framework.org/api-guide/renderers/#varying-behaviour-by-media-type
    """

    def retrieve(self, request, *args, **kwargs):
        """
        This is used for ROC-data specific manipulation of object data URIs and
        also takes care of special handling for HTML format of details endpoints.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        publishing_context = get_publishing_context(request=request)
        processed_data = self.process_uris(serializer.data, publishing_context=publishing_context)
        if request.accepted_renderer.format == 'html':
            # HTML browsing
            htmlized_data = self.htmlize_data_values(processed_data)
            context = {'data': htmlized_data, 'object': instance}
            return Response(context, template_name=self.template_name)
        else:
            # JSON + API
            return Response(processed_data)

    def process_uris(self, data, publishing_context=None):
        """
        Transform absolute path like `/terms/Ghana` to absolute URI for a given
        `publishing_context` context, e.g. `http://localhost:8000/terms/Ghana`.
        """
        processed_data = OrderedDict()
        for key, value in data.items():
            if key in TREE_DATA_SKIP_KEYS:
                continue
            if isinstance(value, str) and key.endswith('uri') and value.startswith('/'):
                pc = publishing_context
                base_url = pc['scheme'] + '://' + pc['netloc'] + pc['path_prefix']
                processed_data[key] = base_url + value
            else:
                processed_data[key] = value
        return processed_data

    def htmlize_data_values(self, data):
        """
        Make hyperlink data values clickable (used only in HTML browsing views).
        """
        htmlized_data = OrderedDict()

        def htmlize_hyperlink(href):
            return "<a href=\"{href}\">{href}</a>".format(href=href)

        def htmlize_list(values):
            newvalues = []
            for el in value:
                if isinstance(el, str) and el.startswith('http'):
                    newel = htmlize_hyperlink(el)
                else:
                    newel = el
                newvalues.append(newel)
            return newvalues

        for key, value in data.items():
            if isinstance(value, str) and value.startswith('http'):
                newvalue = htmlize_hyperlink(value)
            elif isinstance(value, list):
                newvalue = htmlize_list(value)
            else:
                newvalue = value
            htmlized_data[key] = newvalue

        return htmlized_data





# HIERARCHICAL API   /api/terms/{juri.name}/{vocab.name}/{term.path}
################################################################################

class OLDJurisdictionViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    queryset = Jurisdiction.objects.all()
    serializer_class = JurisdictionSerializer
    lookup_field = "name"
    template_name = 'standards/jurisdiction_detail.html'         # /terms/{juri} AND /{juri}

    def list(self, request, *args, **kwargs):                    # /terms/
        """Used for HTML format of the jurisdiction create-list endpoint."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = JurisdictionSerializer(queryset, many=True, context={'request': request})
        publishing_context = get_publishing_context(request=request)
        processed_datas = []
        for data in serializer.data:
            processed_data = self.process_uris(data, publishing_context=publishing_context)
            processed_datas.append(processed_data)
        #
        if request.accepted_renderer.format == 'html':
            htmlized_datas = [self.htmlize_data_values(pd) for pd in processed_datas]
            context = {'datas': htmlized_datas}
            return Response(context, template_name='standards/jurisdictions.html')
        else:
            return Response(processed_datas)

juri_list = OLDJurisdictionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
juri_detail = OLDJurisdictionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})


class JurisdictionVocabularyViewSet(MultipleFieldLookupMixin, CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    queryset = ControlledVocabulary.objects.select_related('jurisdiction').all()
    lookup_fields = ["jurisdiction__name", "name"]
    serializer_class = ControlledVocabularySerializer
    template_name = 'standards/vocabulary_detail.html'          # /terms/{juri}/{vocab}

    def redirect_to_juri(self, request, *args, **kwargs):       # /terms/{juri}/
        if request.accepted_renderer.format == 'html':
            r = reverse('api-juri-detail', kwargs=kwargs, request=request)
            return HttpResponseRedirect(redirect_to=r)
        else:
            return super(JurisdictionVocabularyViewSet, self).list(request, *args, **kwargs)


juri_vocab_create = JurisdictionVocabularyViewSet.as_view({
    # 'get': 'redirect_to_juri',
    'post': 'create'
})
juri_vocab_detail = JurisdictionVocabularyViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})



class JurisdictionVocabularyTermViewSet(MultipleFieldLookupMixin, CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    queryset = Term.objects.select_related('vocabulary', 'vocabulary__jurisdiction').all()
    lookup_fields = ["vocabulary__jurisdiction__name", "vocabulary__name", "path"]
    serializer_class = TermSerializer
    template_name = 'standards/term_detail.html'                 # /terms/{juri}/{vocab}/{term.path}

    def redirect_to_vocab(self, request, *args, **kwargs):       # /terms/{juri}/{vocab}/
        r = reverse('api-juri-vocab-detail', kwargs=kwargs, request=request)
        return HttpResponseRedirect(redirect_to=r)


juri_vocab_term_create = JurisdictionVocabularyTermViewSet.as_view({
    'get': 'redirect_to_vocab',
    'post': 'create'
})
juri_vocab_term_detail = JurisdictionVocabularyTermViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})



class JurisdictionTermRelationViewSet(MultipleFieldLookupMixin, CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    queryset = TermRelation.objects.select_related('jurisdiction').all()
    lookup_fields = ["jurisdiction__name", "id"]
    serializer_class = TermRelationSerializer
    template_name = 'standards/termrelation_detail.html'        # /termrels/{juri}/{tr.id}

    def list(self, request, *args, **kwargs):                   # /termrels/{juri}/
        queryset = self.filter_queryset(self.get_queryset())
        print(queryset)
        serializer = TermRelationSerializer(queryset, many=True, context={'request': request})
        publishing_context = get_publishing_context(request=request)
        processed_datas = []
        for data in serializer.data:
            processed_data = self.process_uris(data, publishing_context=publishing_context)
            processed_datas.append(processed_data)
        #
        if request.accepted_renderer.format == 'html':
            htmlized_datas = [self.htmlize_data_values(pd) for pd in processed_datas]
            context = {'datas': htmlized_datas}
            import pprint
            pprint.pprint(context)
            return Response(context, template_name='standards/termrelations.html')
        else:
            return Response(processed_datas)



juri_termrel_create = JurisdictionTermRelationViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
juri_termrel_detail = JurisdictionTermRelationViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})



# JURISDICTION
################################################################################

class JurisdictionViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}
    queryset = Jurisdiction.objects.all()
    serializer_class = JurisdictionSerializer
    lookup_field = "name"
    template_name = 'standards/jurisdiction_detail.html'



# STANDARDS
################################################################################

class StandardsDocumentViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}/documents/{d.id}
    queryset = StandardsDocument.objects.all()
    serializer_class = StandardsDocumentSerializer
    pagination_class = LargeResultsSetPagination(100)
    template_name = 'standards/document_detail.html'

    def get_queryset(self):
        return self.queryset.filter(jurisdiction__name=self.kwargs['jurisdiction_name'])


class StandardNodeViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}/standardnodes/{sn.id}
    queryset = StandardNode.objects.all()
    serializer_class = StandardNodeSerializer
    pagination_class = LargeResultsSetPagination(100)
    template_name = 'standards/standardnode_detail.html'

    def get_queryset(self):
        return self.queryset.filter(document__jurisdiction__name=self.kwargs['jurisdiction_name'])


# STANDARDS CROSSWALKS
################################################################################

class StandardsCrosswalkViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}/standardnodes/{sc.id}
    queryset = StandardsCrosswalk.objects.all()
    serializer_class = StandardsCrosswalkSerializer
    pagination_class = LargeResultsSetPagination(100)
    template_name = 'standards/standardscrosswalk_detail.html'

    def get_queryset(self):
        return self.queryset.filter(jurisdiction__name=self.kwargs['jurisdiction_name'])


class StandardNodeRelationViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}/standardnoderels/{snr.id}
    queryset = StandardNodeRelation.objects.all()
    serializer_class = StandardNodeRelationSerializer
    pagination_class = LargeResultsSetPagination(100)
    template_name = 'standards/standardnoderelation_detail.html'

    def get_queryset(self):
        return self.queryset.filter(jurisdiction__name=self.kwargs['jurisdiction_name'])




# CONTENT
################################################################################

class ContentCollectionViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}/contentcollections/{cc.id}
    queryset = ContentCollection.objects.all()
    serializer_class = ContentCollectionSerializer
    pagination_class = LargeResultsSetPagination(100)
    template_name = 'standards/contentcollection_detail.html'

    def get_queryset(self):
        return self.queryset.filter(jurisdiction__name=self.kwargs['jurisdiction_name'])


class ContentNodeViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}/contentnodes/{c.id}
    queryset = ContentNode.objects.all()
    serializer_class = ContentNodeSerializer
    partial=True
    pagination_class = LargeResultsSetPagination(100)
    template_name = 'standards/contentnode_detail.html'

    def get_queryset(self):
        return self.queryset.filter(collection__jurisdiction__name=self.kwargs['jurisdiction_name'])


class ContentNodeRelationViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}/contentnoderels/{cnr.id}
    queryset = ContentNodeRelation.objects.all()
    serializer_class = ContentNodeRelationSerializer
    pagination_class = LargeResultsSetPagination(100)
    template_name = 'standards/contentnoderelation_detail.html'

    def get_queryset(self):
        return self.queryset.filter(jurisdiction__name=self.kwargs['jurisdiction_name'])


# CONTENT CORRELATIONS
################################################################################

class ContentCorrelationViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}/contentcorrelations/{cs.id}
    queryset = ContentCorrelation.objects.all()
    serializer_class = ContentCorrelationSerializer
    pagination_class = LargeResultsSetPagination(100)
    template_name = 'standards/contentcorrelation_detail.html'

    def get_queryset(self):
        return self.queryset.filter(jurisdiction__name=self.kwargs['jurisdiction_name'])


class ContentStandardRelationViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}/contentstandardrels/{csr.id}
    queryset = ContentStandardRelation.objects.all()
    serializer_class = ContentStandardRelationSerializer
    pagination_class = LargeResultsSetPagination(100)
    template_name = 'standards/contentstandardrelation_detail.html'

    def get_queryset(self):
        return self.queryset.filter(correlation__jurisdiction__name=self.kwargs['jurisdiction_name'])