import pytest


from standards.models import Jurisdiction, UserProfile


@pytest.mark.django_db
def test_juri():
    juri = Jurisdiction(
        short_name="Ghana",
        name="Ghana NaCCA",
        country='GH'
    )
    juri.save()
    assert juri.id
    # print(juri.__dict__)
