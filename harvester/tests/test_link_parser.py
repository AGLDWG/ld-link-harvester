import harvester
import requests


def test_parser_relative_to_absolute_links():
    """
    The parser should be able to return a set of URLs that are absolute links, even if they are published as
    relative links.
    """
    expected_response = [
        ('http://127.0.0.1:8080/birds.html', 1, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/mammals.html', 1, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/fish.html', 1, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/reptiles.html', 1, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/amphibians.html', 1, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/anthropods.html', 1, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/form.html', 1, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/contact.html', 1, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/amphibians/growling.html', 1, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/amphibians/red-crowned.html', 1, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/amphibians/crucifix.html', 1, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/index.html', 1, 'http://127.0.0.1:8080'),
    ]
    uri = 'http://127.0.0.1:8080/amphibians.html'
    seed = 'http://127.0.0.1:8080'
    depth = 1
    response = requests.get(uri)
    links = harvester.find_links_html(response.content, uri, seed, depth)
    assert set(links) == set(expected_response)


def test_parser_external_links():
    """
    The parser should also be able to return local as well as external links (all in absolute formats).
    """
    expected_response = [
        ('http://127.0.0.1:8080/birds.html', 0, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/mammals.html', 0, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/fish.html', 0, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/reptiles.html', 0, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/amphibians.html', 0, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/anthropods.html', 0, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/form.html', 0, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/form.html', 0, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/contact.html', 0, 'http://127.0.0.1:8080'),
        ('https://www.australia.com/en/facts-and-planning/australias-animals.html', 0, 'http://127.0.0.1:8080'),
        ('https://en.wikipedia.org/wiki/Fauna_of_Australia', 0, 'http://127.0.0.1:8080'),
        ('https://www.csiro.au/en/Research/Collections/ANIC', 0, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/index.html', 0, 'http://127.0.0.1:8080')
    ]
    uri = 'http://127.0.0.1:8080'
    seed = 'http://127.0.0.1:8080'
    depth = 0
    response = requests.get(uri)
    links = harvester.find_links_html(response.content, uri, seed, depth)
    assert set(links) == set(expected_response)


def test_parser_blacklisted_files():
    """
    The parser function should  be able to filter out black listed file types and ignore the associated links
    (e.g. no '.jpg' links).
    """
    expected_response = [
        ('http://127.0.0.1:8080/birds.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/mammals.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/fish.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/reptiles.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/amphibians.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/anthropods.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/form.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/contact.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/index.html', 2, 'http://127.0.0.1:8080')
    ]
    uri = 'http://127.0.0.1:8080/mammals.html'
    seed = 'http://127.0.0.1:8080'
    depth = 2
    response = requests.get(uri)
    links = harvester.find_links_html(response.content, uri, seed, depth)
    assert set(links) == set(expected_response)


def test_parser_remove_anchors():
    """
    The parser should remove link anchors from links - i.e. remove hashes from urls
    (e.g.   http://127.0.0.1:8080/fish.html#introduced-fish --> http://127.0.0.1:8080/fish.html)
    """
    expected_response = [
        ('http://127.0.0.1:8080/birds.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/mammals.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/fish.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/fish.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/reptiles.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/amphibians.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/anthropods.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/form.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/contact.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/index.html', 2, 'http://127.0.0.1:8080')
    ]
    incorrect_response = [
        ('http://127.0.0.1:8080/birds.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/mammals.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/fish.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/fish.html#introduced-fish', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/reptiles.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/amphibians.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/anthropods.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/form.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/contact.html', 2, 'http://127.0.0.1:8080'),
        ('http://127.0.0.1:8080/index.html', 2, 'http://127.0.0.1:8080')
    ]
    uri = 'http://127.0.0.1:8080/fish.html'
    seed = 'http://127.0.0.1:8080'
    depth = 2
    response = requests.get(uri)
    links = harvester.find_links_html(response.content, uri, seed, depth)
    assert set(links) != set(incorrect_response)
    assert set(links) == set(expected_response)
