from rest_framework import serializers
from rest_framework.reverse import reverse

from standards.models import Jurisdiction, UserProfile
from standards.models import ControlledVocabulary, Term
from standards.models import TERMREL_KINDS, TermRelation



# CUTSOM HYPERLINK FIELDS
################################################################################

class ControlledVocabularyHyperlink(serializers.HyperlinkedRelatedField):
    # /terms/<jurisdiction__name>/<name>
    # We define these as class attributes so we don't need to pass them as args.
    view_name = 'api-juri-vocab-detail'
    queryset = ControlledVocabulary.objects.all()

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




# HIERARCHICAL API
################################################################################

class JurisdictionSerializer(serializers.ModelSerializer):
    vocabularies = ControlledVocabularyHyperlink(many=True)

    class Meta:
        model = Jurisdiction
        fields = [
            "id", "name", "display_name", "country", "language", "alt_name", "notes",
            "vocabularies",
        ]


class ControlledVocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlledVocabulary
        fields = '__all__'


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'

