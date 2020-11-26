import pytest

from standards.models import Jurisdiction, UserProfile

from standards.models import ControlledVocabulary, Term, TermRelation

@pytest.fixture
def juri():
    juri = Jurisdiction(name="Ghana NaCCA", short_name="Ghana")
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