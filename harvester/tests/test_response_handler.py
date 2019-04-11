import harvester
import requests
import sys
import os
from copy import copy

def test_valid_response():
    """
    If the response is from a page with the format text/html, the handler should hand it to the parser
    function to obtain appropriate child links.
    """
    expected_response = ({'url': 'http://127.0.0.1:8080',
                          'opcode': 2,
                          'params': {'source': 'http://127.0.0.1:8080',
                                     'format': 'text/html',
                                     'failed': 0}},
                         {('http://127.0.0.1:8080/index.html', 1, 'http://127.0.0.1:8080'),
                          ('http://127.0.0.1:8080/birds.html', 1, 'http://127.0.0.1:8080'),
                          ('http://127.0.0.1:8080/mammals.html', 1, 'http://127.0.0.1:8080'),
                          ('http://127.0.0.1:8080/fish.html', 1, 'http://127.0.0.1:8080'),
                          ('http://127.0.0.1:8080/reptiles.html', 1, 'http://127.0.0.1:8080'),
                          ('http://127.0.0.1:8080/amphibians.html', 1, 'http://127.0.0.1:8080'),
                          ('http://127.0.0.1:8080/anthropods.html', 1, 'http://127.0.0.1:8080'),
                          ('http://127.0.0.1:8080/form.html', 1, 'http://127.0.0.1:8080'),
                          ('http://127.0.0.1:8080/contact.html', 1, 'http://127.0.0.1:8080'),
                          ('http://127.0.0.1:8080/form.html', 1, 'http://127.0.0.1:8080'),
                          ('https://www.australia.com/en/facts-and-planning/australias-animals.html', 1, 'http://127.0.0.1:8080'),
                          ('https://en.wikipedia.org/wiki/Fauna_of_Australia', 1, 'http://127.0.0.1:8080'),
                          ('https://www.csiro.au/en/Research/Collections/ANIC', 1, 'http://127.0.0.1:8080')})
    response = requests.get('http://127.0.0.1:8080')
    uri = 'http://127.0.0.1:8080'
    seed = 'http://127.0.0.1:8080'
    depth = 0
    result = harvester.process_response(response, uri, seed, depth)
    result = (result[0], set(result[1]))
    assert isinstance(result, tuple)
    assert response.status_code == 200
    assert result == expected_response


def test_error_response():
    """
    The response handler should be able to handle responses that return some form of error (e.g. 404)
    """
    sys.stdout = open(os.devnull, 'w')
    expected_result = {'url': 'http://127.0.0.1:8080/no-exist',
                       'opcode': 2,
                       'params': {'source': 'http://127.0.0.1:8080',
                                  'format': 'N/A',
                                  'failed': 1}}
    uri = 'http://127.0.0.1:8080/no-exist'
    response = requests.get(uri)
    seed = 'http://127.0.0.1:8080'
    depth = 0
    result = harvester.process_response(response, uri, seed, depth)
    assert isinstance(result, dict)
    assert response.status_code == 404
    assert result == expected_result

def test_error_no_file_format():
    """
    The response handler function should be capable of detecting if the content-format is missing and replacing it
    with placeholder value N/A if necessary.
    """
    sys.stdout = open(os.devnull, 'w')
    expected_result = {'url': 'http://127.0.0.1:8080/mammals.html',
                       'opcode': 2,
                       'params': {'source': 'http://127.0.0.1:8080',
                                  'format': 'N/A',
                                  'failed': 1}}
    uri = 'http://127.0.0.1:8080/mammals.html'
    response = requests.get(uri)
    response.headers.pop('content-type')
    seed = 'http://127.0.0.1:8080'
    depth = 0
    result = harvester.process_response(response, uri, seed, depth)
    assert result == expected_result


def test_rdf_detected_in_name():
    """
    The crawler should also detect rdf files if it encounters a file ending in the URL matching a known type.
    """
    sys.stdout = open(os.devnull, 'w')
    expected_result = {'url': 'http://127.0.0.1:8080/mammals.rdf',
                       'opcode': 3,
                       'params': {'source': 'http://127.0.0.1:8080',
                                  'format': 'application/rdf+xml'}}
    uri = 'http://127.0.0.1:8080/mammals.html'
    response = requests.get(uri)
    uri = 'http://127.0.0.1:8080/mammals.rdf'
    response.headers['content-type'] = 'application/rdf+xml'
    seed = 'http://127.0.0.1:8080'
    depth = 0
    result = harvester.process_response(response, uri, seed, depth)
    assert result == expected_result


def test_rdf_detected_in_format():
    """
    The response handler should be able to detect rdf file format in the response headers and act accordingly.
    """
    sys.stdout = open(os.devnull, 'w')
    expected_result = {'url': 'http://127.0.0.1:8080/mammals.html',
                       'opcode': 3,
                       'params': {'source': 'http://127.0.0.1:8080',
                                  'format': 'application/rdf+xml'}}
    uri = 'http://127.0.0.1:8080/mammals.html'
    response = requests.get(uri)
    response.headers['content-type'] = 'application/rdf+xml'
    seed = 'http://127.0.0.1:8080'
    depth = 0
    result = harvester.process_response(response, uri, seed, depth)
    assert result == expected_result


def test_error_invalid_format():
    """
    The response handler should be able to encounter an 'invalid' file format and return a valid result
    (i.e. failed=0) to be recorded but not attempt to pass it to the parser.
    """
    sys.stdout = open(os.devnull, 'w')
    expected_result = {'url': 'http://127.0.0.1:8080/mammals.html',
                       'opcode': 2,
                       'params': {'source': 'http://127.0.0.1:8080',
                                  'format': 'text/xml',
                                  'failed': 0}}
    uri = 'http://127.0.0.1:8080/mammals.html'
    response = requests.get(uri)
    response.headers['content-type'] = 'text/xml'
    seed = 'http://127.0.0.1:8080'
    depth = 0
    result = harvester.process_response(response, uri, seed, depth)
    assert result == expected_result


def test_redirect_change_seed():
    """
    The response handler should modify the uri and seeds appropriately if a 3xx redirect is detected to have occurred.
    """
    expected_result = ({'url': 'http://127.0.0.1:8080/mammals.html',
                        'opcode': 2,
                        'params': {'source': 'http://127.0.0.1:8080',
                                   'format': 'text/html',
                                   'failed': 0}},
                       {('http://127.0.0.1:8080/index.html', 1, 'http://127.0.0.1:8080'),
                        ('http://127.0.0.1:8080/birds.html', 1, 'http://127.0.0.1:8080'),
                        ('http://127.0.0.1:8080/mammals.html', 1, 'http://127.0.0.1:8080'),
                        ('http://127.0.0.1:8080/fish.html', 1, 'http://127.0.0.1:8080'),
                        ('http://127.0.0.1:8080/reptiles.html', 1, 'http://127.0.0.1:8080'),
                        ('http://127.0.0.1:8080/amphibians.html', 1, 'http://127.0.0.1:8080'),
                        ('http://127.0.0.1:8080/anthropods.html', 1, 'http://127.0.0.1:8080'),
                        ('http://127.0.0.1:8080/form.html', 1, 'http://127.0.0.1:8080'),
                        ('http://127.0.0.1:8080/contact.html', 1, 'http://127.0.0.1:8080')})

    uri = 'http://127.0.0.1:8080/mammals.html'
    response = requests.get(uri)
    # Modifying a response to make it look like a redirect
    uri = 'http://nonexists.com/mammals.html'
    hist_response = copy(response)
    hist_response.status_code = 301
    hist_response.headers = {'Location': 'http://127.0.0.1:8080/mammals.html', 'Content-Type': 'text/html; charset=UTF-8', 'Content-Encoding': 'gzip', 'Date': 'Thu, 11 Apr 2019 03:24:58 GMT', 'Expires': 'Thu, 11 Apr 2019 03:24:58 GMT', 'Cache-Control': 'private, max-age=0', 'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'SAMEORIGIN', 'X-XSS-Protection': '1; mode=block', 'Content-Length': '177', 'Server': 'GSE'}
    response.history.append(hist_response)
    seed = 'http://nonexists.com'
    depth = 0
    result = harvester.process_response(response, uri, seed, depth)
    result = (result[0], set(result[1]))
    assert result == expected_result
