import requests
from multiprocessing import Queue, Process, Manager
import time
import signal
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from modules.lddatabase import LDHarvesterDatabaseConnector

URL_BATCH = [(url.strip(), 0, url.strip()) for url in open('single_URI.txt')]
DATABASE_FILE = 'ld-database.db'
RECURSION_DEPTH_LIMIT = 4
PROC_COUNT = 8
RDF_MEDIA_TYPES = [
    "application/rdf+xml",
    "text/turtle",
    "application/n-triples",
    "application/ld+json",
    "application/owl+xml",
    "text/trig",
    "application/n-quads"
]
RDF_FORMATS = [
    'rdf',
    'owl',
    'ttl',
    'n3',
    'nt',
    'json'  # candidate
]
GLOBAL_HEADER = {
    'Accept': ",".join(RDF_FORMATS),
    'User-Agent': 'LD Link Harvester'
}


def close():
    dbconnector.end_crawl(crawlid)
    dbconnector.commit()
    dbconnector.close()
    print("Connection Closed.")


def find_links_html(response_content, uri, seed, depth=0):
    # Function to parse links from a web document (presumably html)
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
            #if link.strip('/#') not in visited:
            links.append((link, depth, seed))
    #print(links)
    return links


def process_response(response, uri, seed, depth):
    if response.status_code == 200:
        #dbconnector.insert_link(uri, crawlid, seed)
        #dbconnector.commit()
        file_format = response.headers['Content-type'].split(';')[0]
        if uri.split('.')[-1] in RDF_FORMATS:
            #dbconnector.insert_valid_rdfuri(uri, crawlid, seed, file_format)
            #dbconnector.commit()
            enhanced_resp = {'url': uri,
                             'opcode': 3,
                             'params':  {'source': seed, 'format': file_format}}
            return enhanced_resp
        if file_format in RDF_MEDIA_TYPES:
            #dbconnector.insert_valid_rdfuri(uri, crawlid, seed, file_format)
            #dbconnector.commit()
            enhanced_resp = {'url': uri,
                             'opcode': 3,
                             'params': {'source': seed, 'format': file_format}}
            return enhanced_resp
        elif file_format == 'text/html':
            try:
                child_links = find_links_html(response.content, uri, seed, depth+1)
                enhanced_resp = {'url': uri,
                                 'opcode': 2,
                                 'params': {'source': seed, 'failed': 0}}
                return enhanced_resp, child_links
            except Exception as er:
                print(er, end='...')
                print('Cannot decode response from {}. Continuing'.format(uri))
                enhanced_resp = {'url': uri,
                                 'opcode': 2,
                                 'params': {'source': seed, 'failed': 1}}
                return enhanced_resp
        else:
            enhanced_resp = {'url': uri,
                             'opcode': 2,
                             'params': {'source': seed, 'failed': 0}}
            return enhanced_resp
    else:
        #dbconnector.insert_link(uri, crawlid, seed, failed=1)
        enhanced_resp = {'url': uri,
                         'opcode': 2,
                         'params': {'source': seed, 'failed': 1}}
        return enhanced_resp


start_sentinal = "start"
end_sentinal = "end"
def worker_fn(p, in_queue, out_queue, visited):
    print("Process {} started.".format(p))
    signal.signal(signal.SIGTERM, close)
    signal.signal(signal.SIGINT, close)
    out_queue.put(start_sentinal)
    while not in_queue.empty():
        url = in_queue.get()
        url, depth, seed = url
        try:
            if url not in visited and depth <= RECURSION_DEPTH_LIMIT:
                visited[url.strip('/#')] = True
                resp = requests.get(url, headers=GLOBAL_HEADER)
            else:
                continue
        except Exception as e:
            if url == seed:  # Move this somewhere else??
                enhanced_resp = {'url': url,
                                 'opcode': 1,
                                 'params': {'source': seed, 'failed': 1}}
                # dbconnector.insert_failed_seed(uri, crawlid, response.status_code)
                # dbconnector.commit()
                out_queue.put((enhanced_resp, e))
            else:
                enhanced_resp = {'url': url,
                                 'opcode': 2,
                                 'params': {'source': seed, 'failed': 1}}
                out_queue.put((enhanced_resp, e))
            #Insert Failed Response, Insert Link OR Insert Failed Seed
            continue
        processed_response = process_response(resp, url, seed, depth)
        if isinstance(processed_response, tuple):
            [in_queue.put((child[0], child[1], child[2])) for child in processed_response[1]]
            out_queue.put((processed_response[0], resp))
            #Insert Link
        else:
            out_queue.put((processed_response, resp))
            #Insert RDF Data OR Insert Seed
    print("Process {} done.".format(p))
    out_queue.put(end_sentinal)
    raise SystemExit(0)

if __name__ == "__main__":
    dbconnector = LDHarvesterDatabaseConnector(DATABASE_FILE)
    crawlid = dbconnector.get_new_crawlid()
    dbconnector.insert_crawl(crawlid)
    signal.signal(signal.SIGTERM, close)
    signal.signal(signal.SIGINT, close)

    manager = Manager()
    visited = manager.dict()
    work_queue = manager.Queue()
    [work_queue.put(i) for i in URL_BATCH]
    resp_queue = manager.Queue()
    worker_procs = []
    for i in range(PROC_COUNT):
        p = Process(target=worker_fn, args=(i+1, work_queue, resp_queue, visited))
        worker_procs.append(p)
    begin = time.time()
    [p.start() for p in worker_procs]
    #wait for processes to start
    time.sleep(0.1)
    threads_started = 0
    threads_ended = 0
    i = 0
    while True:
        if i >= 50:
            dbconnector.commit()
            i =- 1
        i += 1
        resp_tuple = resp_queue.get()
        if resp_tuple == start_sentinal:
            threads_started += 1
            continue
        elif resp_tuple == end_sentinal:
            threads_ended += 1
            if threads_ended == PROC_COUNT:
                break
            else:
                continue
        if isinstance(resp_tuple[0], dict):
            '''
            OPCODES: 
            0 = Insert Seed (Deprecated)
            1 = Insert Failed Seed (Handled by 2)
            2 = Insert Link (Failed or otherwise)
            3 = Insert RDF Data
            '''
            opcode = resp_tuple[0]['opcode']
            if resp_tuple[0]['url'] == resp_tuple[0]['params']['source']:
                dbconnector.insert_crawl_seed(uri=resp_tuple[0]['url'], crawlid=crawlid)
            if opcode == 2:
                dbconnector.insert_link(uri=resp_tuple[0]['url'], crawlid=crawlid, source=resp_tuple[0]['params']['source'], failed=resp_tuple[0]['params']['failed'])
                if resp_tuple[0]['params']['failed'] == 1 and resp_tuple[0]['url'] == resp_tuple[0]['params']['source']:
                    dbconnector.insert_failed_seed(uri=resp_tuple[0]['url'], crawlid=crawlid, code=resp_tuple[1].status_code)
            if opcode == 3:
                dbconnector.insert_valid_rdfuri(uri=resp_tuple[0]['url'], crawlid=crawlid, source=resp_tuple[0]['params']['source'], response_format=resp_tuple[0]['params']['format'])
        if isinstance(resp_tuple[1], Exception):
            print("{} : {}".format(str(resp_tuple[0]['url']), str(resp_tuple[1])))
        else:
            print("{} : {}".format(str(resp_tuple[0]['url']), str(resp_tuple[1].status_code)))
    [p.join() for p in worker_procs]
    end = time.time()
    close()
    print(visited)
    print("Duration: {} seconds".format(end - begin))