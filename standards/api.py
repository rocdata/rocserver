import json
import os
import re
import shutil
import urllib.request

from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect
from rest_framework import serializers, viewsets, views, status, response
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.reverse import reverse

from standards.models import Jurisdiction
from standards.models import ControlledVocabulary, Term, TermRelation
from standards.models import StandardsDocument, StandardNode
from standards.models import StandardsCrosswalk, StandardNodeRelation

from standards.serializers import JurisdictionSerializer
from standards.serializers import ControlledVocabularySerializer
from standards.serializers import TermSerializer, TermRelationSerializer

from standards.serializers import StandardsDocumentSerializer

# HELPERS
################################################################################

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


class CustomHTMLRendererRetrieve:
    """
    Custom retrieve method that skips the serialization when rendering HTML, via
    django-rest-framework.org/api-guide/renderers/#varying-behaviour-by-media-type
    """

    def retrieve(self, request, *args, **kwargs):
        """
        This is used for HTML format of details endpoints.
        """
        instance = self.get_object()
        if request.accepted_renderer.format == 'html':
            data = {'object': instance}
            return Response(data, template_name=self.template_name)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)



# HIERARCHICAL API   /api/terms/{juri.name}/{vocab.name}/{term.path}
################################################################################

class JurisdictionViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    queryset = Jurisdiction.objects.all()
    serializer_class = JurisdictionSerializer
    lookup_field = "name"
    template_name = 'standards/jurisdiction_detail.html'         # /terms/{juri}


    def list(self, request, *args, **kwargs):                    # /terms/
        """Used for HTML format of the jurisdiction create-list endpoint."""
        if request.accepted_renderer.format == 'html':
            queryset = self.filter_queryset(self.get_queryset())
            data = {'jurisdictions': queryset}
            return Response(data, template_name='standards/jurisdictions.html')
        return super().list(request, *args, **kwargs)


juri_list = JurisdictionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
juri_detail = JurisdictionViewSet.as_view({
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
        """Used for HTML format of the jurisdiction create-list endpoint."""
        if request.accepted_renderer.format == 'html':
            queryset = self.filter_queryset(self.get_queryset())
            data = {'jurisdictions': queryset}
            return Response(data, template_name='standards/termrelations.html')
        return super().list(request, *args, **kwargs)


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






# STANDARDS DOCUMENTS
################################################################################

class StandardsDocumentSerializer(serializers.ModelSerializer):
    root_node_id = serializers.SerializerMethodField()

    class Meta:
        model = StandardsDocument
        fields = '__all__'

    def get_root_node_id(self, obj):
        try:
            return StandardNode.objects.get(level=0, document_id=obj.id).id
        except StandardNode.DoesNotExist:
            return None

def LargeResultsSetPagination(size=100):
    class CustomPagination(PageNumberPagination):
        page_size = size
        page_size_query_param = "page_size"
        max_page_size = page_size * 10
    return CustomPagination


class StandardsDocumentViewSet(viewsets.ModelViewSet):
    queryset = StandardsDocument.objects.all()
    serializer_class = StandardsDocumentSerializer
    pagination_class = LargeResultsSetPagination(100)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(is_draft=False)
