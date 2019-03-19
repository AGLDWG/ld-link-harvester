'''
LD-Seed Harvester (v1.0)
By Jake Hashim-Jones

'''
__author__='Jake Hashim-Jones'

import requests
import signal
import time
import multiprocessing as mp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from modules.lddatabase import LDHarvesterDatabaseConnector

URI_in_file = 'single_URI.txt'
database_file = 'ld-database.db'
worker_count = 4
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
    #uri = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(uri))
    links = []
    soup = BeautifulSoup(response_content, "lxml")
    all = soup.findAll()
    ids = []
    for item in all:
        ids.append(item.get('id'))
    for link in soup.findAll('a'):
        link = link.get('href')
        link = urljoin(uri, link)
        if isinstance(link, str):
            if link.strip('/#') not in visited:
                links.append((link, depth, seed))
    #print(links)
    return links


def make_request(uri, depth, seed, header=global_header):
    try:
        if depth <= recursion_depth_limit and uri not in visited:
            print(uri)
            response = requests.get(uri, headers=header)
            visited[uri.strip('/#')] = True
        else:
            return False
    except:
        dbconnector.insert_link(uri, crawlid, seed, failed=1)
        if uri == seed:
            dbconnector.insert_failed_seed(uri, crawlid, '000')
        dbconnector.commit()
        return "Cannot Reach " + uri
    if response.status_code == 200:
        dbconnector.insert_link(uri, crawlid, seed)
        dbconnector.commit()
        file_format = response.headers['Content-type'].split(';')[0]
        if uri.split('.')[-1] in rdf_file_ending:
            dbconnector.insert_valid_rdfuri(uri, crawlid, seed, file_format)
            dbconnector.commit()
            return "LD!"
        if file_format in rdf_media_types:
            dbconnector.insert_valid_rdfuri(uri, crawlid, seed, file_format)
            dbconnector.commit()
            return "LD!"
        elif file_format == 'text/html':
            try:
                child_links = find_links_html(response.content, uri, seed, depth+1)
                return child_links
            except Exception as er:
                print(er, end='...')
                return 'Cannot decode response. Continuing'
        elif file_format in ['application/xhtml+xml']:
            pass
        dbconnector.insert_link(uri, crawlid, seed)
        return 'Unknown File Format - {}'.format(file_format)
    else:
        dbconnector.insert_link(uri, crawlid, seed, failed=1)
        dbconnector.commit()
        if uri == seed:
            dbconnector.insert_failed_seed(uri, crawlid, '000')
        return 'Cannot retrieve document. Response {}'.format(response.status_code)


def close():
    dbconnector.end_crawl(crawlid)
    dbconnector.commit()
    dbconnector.close()
    print("Connection Closed.")

start_sentinal = "start"
end_sentinal = "end"
def worker_pc(w, in_queue, out_queue):
    #session = requests.Session()
    out_queue.put(start_sentinal)
    #print(in_queue.empty())
    #print(in_queue.get())
    while True:
        if in_queue.empty():
            break
        uri, depth, seed = in_queue.get()
        try:
            if depth == 0:
                dbconnector.insert_crawl_seed(uri, crawlid)
                dbconnector.commit()
            print(uri)
            response = make_request(uri, depth, seed, global_header)
        except Exception as e:
            response = None
            out_queue.put((uri, e))
        if isinstance(response, list):
            [in_queue.put(uri) for uri in response]
        if response:
            out_queue.put((uri, response))
    print("Worker {} done.".format(w))
    out_queue.put(end_sentinal)
    raise SystemExit(0)


if __name__ == '__main__':
    visited = {}
    dbconnector = LDHarvesterDatabaseConnector(database_file)
    crawlid = dbconnector.get_new_crawlid()
    dbconnector.insert_crawl(crawlid)
    signal.signal(signal.SIGTERM, close)
    signal.signal(signal.SIGINT, close)
    initial_URI_list = [(URI.strip(), 0, URI.strip()) for URI in open(URI_in_file, 'r')]

    try:
        work_queue = mp.Queue()
        [work_queue.put(uri) for uri in initial_URI_list]
        resp_queue = mp.Queue()
        workers = []
        for i in range(worker_count):
            worker = mp.Process(target=worker_pc, args=(i+1, work_queue, resp_queue))
            workers.append(worker)
        begin = time.time()
        [worker.start() for worker in workers]
        time.sleep(0.1)
        threads_started = 0
        threads_ended = 0
        while True:
            resp_tuple = resp_queue.get()
            if resp_tuple == start_sentinal:
                threads_started += 1
                continue
            elif resp_tuple == end_sentinal:
                threads_ended += 1
                if threads_ended == worker_count:
                    break
                else:
                    continue
            #if isinstance(resp_tuple, Exception):
            #    print("{} : {}".format(str(resp_tuple[0]), str(resp_tuple[1])))
            #else:
            #    print("{} : {}".format(str(resp_tuple[0]), str(resp_tuple[1].status_code)))
        [worker.join() for worker in workers]
        end = time.time()
        print("Duration: {} seconds".format(end - begin))
    except Exception as er:
        print(er)
        close()
        exit(1)
    close()
