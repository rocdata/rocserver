from rest_framework import serializers
from rest_framework.reverse import reverse

from standards.models import Jurisdiction, UserProfile
from standards.models import ControlledVocabulary, Term
from standards.models import TERMREL_KINDS, TermRelation



# CUTSOM HYPERLINK FIELDS
################################################################################


class JurisdictionHyperlink(serializers.HyperlinkedRelatedField):
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



# HIERARCHICAL API
################################################################################

class JurisdictionSerializer(serializers.ModelSerializer):
    vocabularies = ControlledVocabularyHyperlink(many=True, required=False)

    class Meta:
        model = Jurisdiction
        fields = [
            "id",
            "name",
            "display_name",
            "country",
            "language",
            "alt_name",
            "notes",
            "vocabularies",
        ]



class ControlledVocabularySerializer(serializers.ModelSerializer):
    terms = TermHyperlink(many=True, required=False)

    class Meta:
        model = ControlledVocabulary
        fields = [
            "id",
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
            "jurisdiction",
            "creator",
            "terms",
        ]



class TermSerializer(serializers.ModelSerializer):
    jurisdiction = JurisdictionHyperlink(source='vocabulary.jurisdiction', required=True)
    vocabulary = ControlledVocabularyHyperlink(required=True)

    class Meta:
        model = Term
        fields = [
            "jurisdiction",
            "vocabulary",
            "id",
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

