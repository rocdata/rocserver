import json
import os
import re
import shutil
import urllib.request

from django.shortcuts import get_object_or_404
from rest_framework import serializers, viewsets, views, status, response
from rest_framework.response import Response
from rest_framework.reverse import reverse


from standards.models import Jurisdiction
from standards.models import ControlledVocabulary, Term
from standards.models import TERMREL_KINDS, TermRelation


from standards.serializers import JurisdictionSerializer
from standards.serializers import ControlledVocabularySerializer
from standards.serializers import TermSerializer



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
            if self.kwargs[field]: # Ignore empty fields.
                filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)  # Lookup the object
        self.check_object_permissions(self.request, obj)
        return obj


class CustomHTMLRendererRetrieve:
    """
    Custom reteive method that skips the serialization when rendering HTML, via
    django-rest-framework.org/api-guide/renderers/#varying-behaviour-by-media-type
    """
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.accepted_renderer.format == 'html':
            data = {'object': instance}
            return Response(data, template_name=self.template_name)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)



# HEARARCHICAL API    /terms/{juri_name}/{vocab_name}/{term_path}
################################################################################

class JuriViewSet(CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    queryset = Jurisdiction.objects.all()
    serializer_class = JurisdictionSerializer
    lookup_field = "name"
    template_name = 'standards/jurisdiction_detail.html'


class JuriVocabViewSet(MultipleFieldLookupMixin, CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    queryset = ControlledVocabulary.objects.select_related('jurisdiction').all()
    lookup_fields = ["jurisdiction__name", "name"]
    serializer_class = ControlledVocabularySerializer
    template_name = 'standards/vocabulary_detail.html'


class JuriVocabTermViewSet(MultipleFieldLookupMixin, CustomHTMLRendererRetrieve, viewsets.ModelViewSet):
    queryset = Term.objects.all()
    lookup_fields = ["vocabulary__jurisdiction__name", "vocabulary__name", "path"]
    serializer_class = TermSerializer
    template_name = 'standards/term_detail.html'

