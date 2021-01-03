import pytest

from bs4 import BeautifulSoup

TEST_SERVER_HOST = "http://testserver"


def parse_object_properties(html):
    """
    Extract key-value pairs from the HTML markup.
    """
    if isinstance(html, bytes):
        html = html.decode('utf-8')
    page = BeautifulSoup(html, "html5lib")
    propery_ps = page.find_all('p', {'class': "list-group-item-text"})
    obj_props_dict = {}
    for p in propery_ps:
        if 'data-name' in p.attrs:
            key = p.attrs['data-name']
            value = p.get_text().strip()
            obj_props_dict[key] = value
    return obj_props_dict


@pytest.mark.django_db
def test_get_html_endpoints(juri, vocab, vocabterms, client):
    # Jurisdiciton
    response = client.get('/Ghana')
    data = parse_object_properties(response.content)
    assert data['name'] == juri.name
    assert juri.uri in data['uri']
    assert data['display_name'] == juri.display_name
    #
    # Vocabulary
    response = client.get('/Ghana/terms/GradeLevels')
    data = parse_object_properties(response.content)
    # assert data['jurisdiction'] == TEST_SERVER_HOST + juri.uri        # TODO
    assert data['name'] == vocab.name
    assert vocab.uri in data['uri'] 
    assert data['label'] == vocab.label
    #
    # Term
    response = client.get('/Ghana/terms/GradeLevels/B2/2')
    data = parse_object_properties(response.content)
    term = vocabterms['b22']
    # assert data['jurisdiction'] == TEST_SERVER_HOST + juri.uri        # TODO
    # assert data['vocabulary'] == TEST_SERVER_HOST + vocab.uri         # TODO
    assert data['path'] == term.path
    assert term.uri in data['uri']
    assert data['label'] == term.label


@pytest.mark.django_db
def test_get_json_endpoints(juri, vocab, vocabterms, client):
    # Jurisdiciton
    response = client.get('/Ghana.json')
    data = response.json()
    assert data['name'] == juri.name
    assert juri.uri in data['uri']
    assert data['display_name'] == juri.display_name
    #
    # Vocabulary
    response = client.get('/Ghana/terms/GradeLevels.json')
    data = response.json()
    assert data['jurisdiction'] == TEST_SERVER_HOST + juri.uri
    assert data['name'] == vocab.name
    assert vocab.uri in data['uri']
    assert data['label'] == vocab.label
    assert len(data['terms']) == 3
    #
    # Term
    response = client.get('/Ghana/terms/GradeLevels/B2/2.json')
    data = response.json()
    term = vocabterms['b22']
    assert data['jurisdiction'] == TEST_SERVER_HOST + juri.uri
    assert data['vocabulary'] == TEST_SERVER_HOST + vocab.uri
    assert data['path'] == term.path
    assert term.uri in data['uri']
    assert data['label'] == term.label
