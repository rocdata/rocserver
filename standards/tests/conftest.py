import pytest

from standards.models import Jurisdiction, UserProfile

from standards.models import ControlledVocabulary, Term, TermRelation

@pytest.fixture
def juri():
    juri = Jurisdiction(
        name="Ghana",
        display_name="Ghana NaCCA",
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


@pytest.fixture
def vocabterms(vocab):
    b1  = Term.objects.create(path='B1', label='Basic 1', vocabulary=vocab)
    b2  = Term.objects.create(path='B2', label='Basic 2', vocabulary=vocab)
    b22 = Term.objects.create(path='B2/2', label='Basic 2.2', vocabulary=vocab)
    return dict(b1=b1, b2=b2, b22=b22)
