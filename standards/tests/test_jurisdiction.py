import pytest


from standards.models import Jurisdiction, UserProfile


@pytest.mark.django_db
def test_juri():
    juri = Jurisdiction(name="Ghana NaCCA", short_name="Ghana")
    juri.save()
    assert juri.id
    # print(juri.__dict__)
