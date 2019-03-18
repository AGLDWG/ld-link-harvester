'''
LD-Seed Harvester (v1.0)
By Jake Hashim-Jones

'''
__author__='Jake Hashim-Jones'

import requests
import signal
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from modules.lddatabase import LDHarvesterDatabaseConnector

URI_in_file = 'single_URI.txt'
URI_out_file = 'ld_seed_URIs.txt'
database_file = 'ld-database.db'
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
recursion_depth_limit = 4 # Can turn off limit if set to -1


def find_links_html(response_content, uri, seed, depth=0):
    # Function to parse links from a web document (presumably html)
    parsed_uri = urlparse(uri)
    netloc = '{uri.netloc}'.format(uri=parsed_uri).strip('www.')
    links = []
    soup = BeautifulSoup(response_content, "lxml")
    all = soup.findAll()
    ids = []
    for item in all:
        ids.append(item.get('id'))
    for link in soup.findAll('a'):
        link = link.get('href')
        if isinstance(link, str):
            if link in visited:
                 continue
            if link.startswith('/') and len(link) > 1:
                link = uri + link
            elif link.startswith('#') and len(link) > 1:
                link = uri.split('#')[0] + link
                search = (re.findall(r'#[^\s\/]*', link))
                if len(search) > 0:
                    id_detected = False
                    for result in search:
                        if result.strip('#') in ids:
                            id_detected = True
                            break
                    if id_detected:
                        continue
            if link not in visited and len(link) > 1 and not re.search(r'#[^\s\/]*\/', link): # Potential issue with the parser and URIs that end up with #maincontent#maincontent#maincontent
                links.append((link, depth, seed))
    #print(links)
    return links


def make_request(uri, depth, seed, header=global_header):
    try:
        if depth <= recursion_depth_limit:
            response = requests.get(uri, headers=header)
        else:
            return False
    except:
        print("Cannot Reach ", uri)
        dbconnector.insert_link(uri, crawlid, seed, failed=1)
        if uri == seed:
            dbconnector.insert_failed_seed(uri, crawlid, '000')
        dbconnector.commit()
        return False
    print(uri, depth)
    print(response.headers['Content-type'])
    if response.status_code == 200:
        dbconnector.insert_link(uri, crawlid, seed)
        dbconnector.commit()
        file_format = response.headers['Content-type'].split(';')[0]
        if uri.split('.')[-1] in rdf_file_ending:
            ld_seed_URIs.append(uri)
            visited.append(uri)
            dbconnector.insert_valid_rdfuri(uri, crawlid, seed, format)
            dbconnector.commit()
            with open(URI_out_file, 'a') as dump:
                dump.write(uri + '\n')
            return True
        if file_format in rdf_media_types:
            ld_seed_URIs.append(uri)
            visited.append(uri)
            dbconnector.insert_valid_rdfuri(uri, crawlid, seed, format)
            dbconnector.commit()
            with open(URI_out_file, 'a') as dump:
                dump.write(uri + '\n')
            return True
        elif file_format == 'text/html':
            try:
                child_links = find_links_html(response.content, uri, seed, depth+1)
            except Exception as er:
                print(er, end='...')
                print('Cannot decode response from {}. Continuing'.format(uri))
                return False
            bulk_request(child_links)
        elif file_format == 'application/xhtml+xml':
            pass
    else:
        dbconnector.insert_link(uri, crawlid, seed, failed=1)
        if uri == seed:
            dbconnector.insert_failed_seed(uri, crawlid, response.status_code)
        dbconnector.commit()
        return False


def bulk_request(uri_list):
    for (uri, depth, seed) in uri_list:
        if depth == 0:
            dbconnector.insert_crawl_seed(uri, crawlid)
            dbconnector.commit()
        make_request(uri, depth, seed)


def close():
    dbconnector.end_crawl(crawlid)
    dbconnector.commit()
    dbconnector.close()
    print("Connection Closed.")


ld_seed_URIs = []
visited = []
open(URI_out_file, 'w').close()
dbconnector = LDHarvesterDatabaseConnector(database_file)
crawlid = dbconnector.get_new_crawlid()
dbconnector.insert_crawl(crawlid)
signal.signal(signal.SIGTERM, close)
signal.signal(signal.SIGINT, close)

try:
    initial_URI_list = [(URI.strip(), 0, URI.strip()) for URI in open(URI_in_file, 'r')]
    bulk_request(initial_URI_list)
except Exception as er:
    print(er)
    close()
    exit(1)
close()
