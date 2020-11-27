from rest_framework import serializers

from standards.models import Jurisdiction, UserProfile
from standards.models import ControlledVocabulary, Term
from standards.models import TERMREL_KINDS, TermRelation


# FLAT REST API
################################################################################

class JurisdictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jurisdiction
        lookup_field = "name"
        fields = '__all__'


class ControlledVocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlledVocabulary
        lookup_field = "name"
        fields = '__all__'


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'

