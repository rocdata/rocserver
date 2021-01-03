from collections import OrderedDict

from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from standards.models import Jurisdiction
from standards.serializers import JurisdictionSerializer
from standards.publishing import get_publishing_context

from standards.models import ControlledVocabulary, Term, TermRelation
from standards.serializers import ControlledVocabularySerializer, TermSerializer, TermRelationSerializer

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



TREE_DATA_SKIP_KEYS = ["lft", "rght", "tree_id"]   # MPTT internal impl. details

class CustomHTMLRendererRetrieve:
    """
    Custom list and retrieve methods that process all ROC data URIs depending on
    the publishing context, and render hyperlinks in HTML output, based on
    django-rest-framework.org/api-guide/renderers/#varying-behaviour-by-media-type
    """
    template_name_list = 'standards/generic_list.html'

    def list(self, request, *args, **kwargs):
        """
        Used for HTML format of list-create endpoints.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        publishing_context = get_publishing_context(request=request)
        processed_datas = []
        for data in serializer.data:
            processed_data = self.process_uris(data, publishing_context=publishing_context)
            processed_datas.append(processed_data)
        if request.accepted_renderer.format == 'html':
            # HTML browsing
            htmlized_datas = [self.htmlize_data_values(pd) for pd in processed_datas]
            class_name = queryset.model.__name__
            context = {'class_name': class_name, 'datas': htmlized_datas}
            return Response(context, template_name=self.template_name_list)
        else:
            # JSON + API
            return Response(processed_datas)

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





# JURISDICTION
################################################################################

class JurisdictionViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}
    queryset = Jurisdiction.objects.all()
    serializer_class = JurisdictionSerializer
    lookup_field = "name"
    template_name = 'standards/jurisdiction_detail.html'


# VOCABULARIES and TERMS
################################################################################

class ControlledVocabularyViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}/terms/{vocab.name}
    queryset = ControlledVocabulary.objects.all()
    serializer_class = ControlledVocabularySerializer
    pagination_class = LargeResultsSetPagination(100)
    template_name = 'standards/vocabulary_detail.html'
    lookup_field = "name"
    lookup_value_regex = '[\w_\-]*'

    def get_queryset(self):
        return self.queryset.filter(jurisdiction__name=self.kwargs['jurisdiction_name'])


class TermViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}/terms/{vocab.name}/               GET(list) POST(create)
    # /{juri}/terms/{vocab.name}/{term.path}    GET PUT PATCH DELETE
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    pagination_class = LargeResultsSetPagination(100)
    template_name = 'standards/term_detail.html'
    lookup_field = "path"

    def get_queryset(self):
        return self.queryset.filter(
            vocabulary__jurisdiction__name=self.kwargs['jurisdiction_name'],
            vocabulary__name=self.kwargs['vocabulary_name'],
        )

class TermRelationViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    # /{juri}/termrels/{pk}
    queryset = TermRelation.objects.all()
    serializer_class = TermRelationSerializer
    pagination_class = LargeResultsSetPagination(100)
    template_name = 'standards/termrelation_detail.html'

    def get_queryset(self):
        return self.queryset.filter(jurisdiction__name=self.kwargs['jurisdiction_name'])






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
        return self.queryset.filter(crosswalk__jurisdiction__name=self.kwargs['jurisdiction_name'])



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