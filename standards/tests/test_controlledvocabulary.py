import pytest


from standards.models import ControlledVocabulary, Term, TermRelation

@pytest.mark.django_db
def test_vocab(juri):
    vocab  = ControlledVocabulary(
        name='GradeLevels',
        label='Ghana Grade Levels',
        jurisdiction=juri)
    vocab.save()
    assert vocab.id


@pytest.mark.django_db
def test_vocab_terms(vocab):
    b1  = Term.objects.create(path='B1', label='Basic 1', vocabulary=vocab)
    b2  = Term.objects.create(path='B2', label='Basic 2', vocabulary=vocab)
    assert b1.id
    assert b2.id
    # print(vocab.__dict__)
    # print(b1.__dict__)

