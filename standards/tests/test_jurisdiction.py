import django
import pytest

from standards.models import Jurisdiction, UserProfile


@pytest.mark.django_db
def test_juri():
    juri = Jurisdiction(
        name="Ghana",
        display_name="Ghana NaCCA",
        country='GH'
    )
    juri.save()
    assert juri.id
    # print(juri.__dict__)


@pytest.mark.django_db
def test_no_duplicate_names():
    juri = Jurisdiction(name="Ghana", display_name="Ghana NaCCA", country='GH')
    juri.save()
    assert juri.id
    juri2 = Jurisdiction(name="Ghana", display_name="Ghana NaCCA", country='GH')
    with pytest.raises(django.db.utils.IntegrityError):
        juri2.save()

