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
acceptible_content_types = [ "application/rdf+xml", "text/turtle", "application/n-triples", "application/ld+json", "application/owl+xml", "text/trig", "application/n-quads"]
URI_out_file = 'ld_seed_URIs.txt'
global_header = {'Accept': "application/rdf+xml, text/turtle, application/n-triples, application/ld+json, application/owl+xml, text/trig, application/n-quads", 'User-Agent': 'LD Link Harvester'}

def find_links(response_content, URI):
    # Function to parse links from a web document (presumably html)
    parsed_URI = urlparse(URI)
    netloc = '{uri.netloc}'.format(uri=parsed_URI).strip('www.')
    links = []
    soup = BeautifulSoup(response_content, "lxml")
    for link in soup.findAll('a'):
        link = link.get('href')
        if isinstance(link, str):
            if link in visited:
                 continue
            if link.startswith('/'):
                link = URI + link
            if link not in visited:
                links.append(link)
    return links

def make_request(URI, header=global_header):
    try:
        response = requests.get(URI, headers=header)
    except:
        print("Cannot Reach ", URI)
        return False
    print(URI)
    print(response.headers['Content-type'])
    if response.status_code == 200:
        if response.headers['Content-type'].split(';')[0] in acceptible_content_types: # Possibly need to trunicate Content-type field to include other properties (e.g. encoding)
            ld_seed_URIs.append(URI)
            visited.append(URI)
            with open(URI_out_file, 'a') as dump:
                dump.write(URI+'\n')
            return True
        elif response.headers['Content-type'].split(';')[0] == 'text/html':
            child_links = find_links(response.content.decode('utf-8'), URI)
            bulk_threaded_request(child_links)
    else:
        return False

def bulk_threaded_request(URI_list):
    threads = []
    #print(URI_list)
    for URI in URI_list:
        new_thread = threading.Thread(target=make_request, args=(URI, global_header))
        threads.append(new_thread)
    [thread.start() for thread in threads]
    [thread.join() for thread in threads] # May need to move this elsewhere and use the global thread list?
    #active_threads.extend(threads) # May need to look at how to monitor and look after recursive thread creation.

active_threads = []
ld_seed_URIs = []
visited = []
open(URI_out_file, 'w').close()
initial_URI_list = [URI.strip() for URI in open(URI_in_file, 'r')]
bulk_threaded_request(initial_URI_list)

exit(0) # Will need to remove this later need to ensure that all threads complete before this point.