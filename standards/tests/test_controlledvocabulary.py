import django
import pytest


from standards.models import ControlledVocabulary, jurisdictions
from standards.models.terms import Term
from standards.models.terms import TermRelation, TERM_REL_KINDS


# VOCABS
################################################################################

@pytest.mark.django_db
def test_vocab(juri):
    vocab  = ControlledVocabulary(
        name='GradeLevels',
        label='Ghana Grade Levels',
        jurisdiction=juri)
    vocab.save()
    assert vocab.id


@pytest.mark.django_db
def test_no_duplicate_within_juri(juri):
    vocab = ControlledVocabulary(name='GradeLevels', label='Ghana Grade Levels', jurisdiction=juri)
    vocab.save()
    vocab2 = ControlledVocabulary(name='GradeLevels', label='Ghana Grade Levels', jurisdiction=juri)
    with pytest.raises(django.db.utils.IntegrityError):
        vocab2.save()



# TERMS
################################################################################

@pytest.mark.django_db
def test_vocab_terms(vocab):
    b1  = Term.objects.create(path='B1', label='Basic 1', vocabulary=vocab)
    b2  = Term.objects.create(path='B2', label='Basic 2', vocabulary=vocab)
    assert b1.id
    assert b2.id

@pytest.mark.django_db
def test_no_duplicate_terms_within_vocab(vocab):
    Term.objects.create(path='B1', label='Basic 1', vocabulary=vocab)
    with pytest.raises(django.db.utils.IntegrityError):
        Term.objects.create(path='B1', label='Basic 1', vocabulary=vocab)



# TERM RELATIONS
################################################################################

@pytest.mark.django_db
def test_terms_relation(juri, vocab):
    b1  = Term.objects.create(path='B1', label='Basic 1', vocabulary=vocab)
    b2  = Term.objects.create(path='B2', label='Basic 2', vocabulary=vocab)
    rel12 = TermRelation(source=b1, kind=TERM_REL_KINDS.related, target=b2, jurisdiction=juri)
    rel12.save()
    assert rel12.id
