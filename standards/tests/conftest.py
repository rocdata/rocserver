import pytest

from standards.models import Jurisdiction, UserProfile

from standards.models import ControlledVocabulary, Term, TermRelation

@pytest.fixture
def juri():
    juri = Jurisdiction(
        short_name="Ghana",
        name="Ghana NaCCA",
        country='GH'
    )
    juri.save()
    return juri


@pytest.fixture
def vocab(juri):
    vocab  = ControlledVocabulary(
        name='GradeLevels',
        label='Ghana Grade Levels',
        jurisdiction=juri
    )
    vocab.save()
    return vocab