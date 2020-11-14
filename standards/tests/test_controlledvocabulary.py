import pytest


from standards.models import ControlledVocabulary, ControlledVocabularyTerm

@pytest.mark.django_db
def test_vocab():
    vocab  = ControlledVocabulary(name='GradeLevels', label='Ghana Grade Levels')
    vocab.save()
    assert vocab.id
    print(vocab.__dict__)


@pytest.mark.django_db
def test_vocab_terms():
    vocab  = ControlledVocabulary.objects.create(name='GradeLevels', label='Ghana Grade Levels')
    b1  = ControlledVocabularyTerm.objects.create(name='B1', label='Basic 1', vocabulary=vocab)
    b2  = ControlledVocabularyTerm.objects.create(name='B2', label='Basic 2', vocabulary=vocab)
    assert b1.id
    assert b2.id
    print(vocab.__dict__)
    print(b1.__dict__)


