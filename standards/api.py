import json
import os
import re
import shutil
import urllib.request

from django.contrib.auth.models import User
from django.conf import settings
from django.conf.urls import url, include
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, views, status, response
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse

from standards.models import Jurisdiction, UserProfile
from standards.models import ControlledVocabulary, Term
from standards.models import TERMREL_KINDS, TermRelation


from standards.serializers import JurisdictionSerializer
from standards.serializers import ControlledVocabularySerializer
from standards.serializers import TermSerializer





# HEARARCHICAL API   /api/terms/{juri_name}/{vocab_name}/{term_path}
#                         isomorphic to the canonical URIs but as REST endpoints
################################################################################

class JuriViewSet(viewsets.ModelViewSet):
    queryset = Jurisdiction.objects.all()
    serializer_class = JurisdictionSerializer
    lookup_field = "name"

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

class JuriVocabViewSet(MultipleFieldLookupMixin, viewsets.ModelViewSet):
    queryset = ControlledVocabulary.objects.select_related('jurisdiction').all()
    for vocab in queryset:
        print(vocab.__dict__)
        print(vocab.jurisdiction.__dict__)
    lookup_fields = ["jurisdiction__name", "name"]
    serializer_class = ControlledVocabularySerializer


class JuriVocabTermViewSet(MultipleFieldLookupMixin, viewsets.ModelViewSet):
    queryset = Term.objects.all()
    lookup_fields = ["vocabulary__jurisdiction__name", "vocabulary__name", "path"]
    serializer_class = TermSerializer