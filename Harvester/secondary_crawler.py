'''
LD-Seed Harvester (v1.0)
By Jake Hashim-Jones

'''
__author__='Jake Hashim-Jones'

import requests
import threading
from bs4 import BeautifulSoup
from urllib.parse import urlparse

URI_in_file = 'single_URI.txt'
URI_out_file = 'ld_seed_URIs.txt'
rdf_media_types = [
    "application/rdf+xml",
    "text/turtle",
    "application/n-triples",
    "application/ld+json",
    "application/owl+xml",
    "text/trig",
    "application/n-quads"
]
rdf_file_ending = [
    'rdf',
    'owl',
    'ttl',
    'n3',
    'nt',
    'json'  # candidate
]
global_header = {
    'Accept': ",".join(rdf_media_types),
    'User-Agent': 'LD Link Harvester'
}
recursion_depth_limit = 3 # Can turn off limit if set to -1


def find_links_html(response_content, uri, depth=0):
    # Function to parse links from a web document (presumably html)
    parsed_uri = urlparse(uri)
    netloc = '{uri.netloc}'.format(uri=parsed_uri).strip('www.')
    links = []
    soup = BeautifulSoup(response_content, "lxml")
    for link in soup.findAll('a'):
        link = link.get('href')
        if isinstance(link, str):
            if link in visited:
                 continue
            if link.startswith('/'):
                link = uri + link
            if link not in visited:
                links.append((link, depth))
    return links


def make_request(uri, depth, header=global_header):
    try:
        response = requests.get(uri, headers=header)
    except:
        print("Cannot Reach ", uri)
        return False
    print(uri, depth)
    print(response.headers['Content-type'])
    if response.status_code == 200:
        if uri.split('.')[-1] in rdf_file_ending:
            ld_seed_URIs.append(uri)
            visited.append(uri)
            with open(URI_out_file, 'a') as dump:
                dump.write(uri + '\n')
            return True
        if response.headers['Content-type'].split(';')[0] in rdf_media_types: # Possibly need to trunicate Content-type field to include other properties (e.g. encoding)
            ld_seed_URIs.append(uri)
            visited.append(uri)
            with open(URI_out_file, 'a') as dump:
                dump.write(uri + '\n')
            return True
        elif response.headers['Content-type'].split(';')[0] == 'text/html':
            child_links = find_links_html(response.content.decode('utf-8'), uri, depth+1)
            bulk_threaded_request(child_links)
        elif response.headers['Content-type'].split(';')[0] == 'application/xhtml+xml':
            pass
    else:
        return False


def bulk_threaded_request(uri_list):
    threads = []
    #print(URI_list)
    for (URI, depth) in uri_list:
        if recursion_depth_limit == -1 or depth <= recursion_depth_limit:
            new_thread = threading.Thread(target=make_request, args=(URI, depth, global_header))
            threads.append(new_thread)
    [thread.start() for thread in threads]
    [thread.join() for thread in threads] # May need to move this elsewhere and use the global thread list?
    #active_threads.extend(threads) # May need to look at how to monitor and look after recursive thread creation.


active_threads = []
ld_seed_URIs = []
visited = []
open(URI_out_file, 'w').close()
initial_URI_list = [(URI.strip(), 0) for URI in open(URI_in_file, 'r')]
bulk_threaded_request(initial_URI_list)

exit(0) # Will need to remove this later need to ensure that all threads complete before this point.