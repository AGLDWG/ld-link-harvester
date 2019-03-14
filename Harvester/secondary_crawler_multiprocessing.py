import requests
import threading
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import multiprocessing as mp
import logging


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
    links = []
    soup = BeautifulSoup(response_content, "lxml")
    for link in soup.findAll('a'):
        link = link.get('href')
        if isinstance(link, str):
            if link.startswith('/' or '#'):
                link = uri + link
            links.append((link, depth))
    return links

def make_request(url_queue, seen):
    #print('start')
    while True:
        pair = url_queue.get()
        uri, depth = pair[0], pair[1]
        if uri not in seen and depth <= recursion_depth_limit:
            try:
                response = requests.get(uri, headers=global_header)
            except:
                #print("Cannot Reach ", uri)
                return False
            print('{}\t{}'.format(uri, depth))
            #print(response.headers['Content-type'])
            if response.status_code == 200:
                if uri.split('.')[-1] in rdf_file_ending:
                    with open(URI_out_file, 'a') as dump:
                        dump.write(uri + '\n')
                if response.headers['Content-type'].split(';')[
                    0] in rdf_media_types:  # Possibly need to trunicate Content-type field to include other properties (e.g. encoding)
                    with open(URI_out_file, 'a') as dump:
                        dump.write(uri + '\n')
                elif response.headers['Content-type'].split(';')[0] == 'text/html':
                    child_links = find_links_html(response.content.decode('utf-8'), uri, depth + 1)
                    [url_queue.put(uri) for uri in child_links]
                elif response.headers['Content-type'].split(';')[0] == 'application/xhtml+xml':
                    pass
                seen[uri] = True
            else:
                pass
        url_queue.task_done()
        #print(url_queue, uri_queue)


open(URI_out_file, 'w').close()
initial_URI_list = [(URI.strip(), 0) for URI in open(URI_in_file, 'r')]

num_workers = 10
url_queue = mp.JoinableQueue()
manager = mp.Manager()
seen = manager.dict()
#bulk_threaded_request(initial_URI_list)

[url_queue.put(uri) for uri in initial_URI_list]

#print(url_queue.get())
crawlers = [threading.Thread(target=make_request, args=(url_queue, seen)) for i in range(num_workers)]

for p in crawlers:
    p.daemon = True
    p.start()
url_queue.join()