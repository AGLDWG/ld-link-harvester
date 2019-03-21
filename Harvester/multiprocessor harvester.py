import requests
from multiprocessing import Queue, Process, Manager
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL_BATCH = [(url.strip(), 0, url.strip()) for url in open('single_URI.txt')]
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
#print(URL_BATCH)
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
            return True
        if file_format in RDF_MEDIA_TYPES:
            #dbconnector.insert_valid_rdfuri(uri, crawlid, seed, file_format)
            #dbconnector.commit()
            return True
        elif file_format == 'text/html':
            try:
                child_links = []
                child_links = find_links_html(response.content, uri, seed, depth+1)
                return child_links
            except Exception as er:
                print(er, end='...')
                print('Cannot decode response from {}. Continuing'.format(uri))
                return False
        elif file_format in ['application/xhtml+xml']:
            pass
    else:
        #dbconnector.insert_link(uri, crawlid, seed, failed=1)
        if uri == seed:
            pass
            #dbconnector.insert_failed_seed(uri, crawlid, response.status_code)
            #dbconnector.commit()
        return False

start_sentinal = "start"
end_sentinal = "end"
def worker_fn(p, in_queue, out_queue, visited):
    print("Process {} started.".format(p))
    out_queue.put(start_sentinal)
    while not in_queue.empty():
        url = in_queue.get()
        url, depth, seed = url
        try:
            if url not in visited:
                resp = requests.get(url, headers=GLOBAL_HEADER)
                visited[url.strip('/#')] = True
            else:
                resp = None
                continue
        except Exception as e:
            resp = None
            out_queue.put((url, e))
            continue
        processed_response = process_response(resp, url, seed, depth)
        if processed_response:
            if isinstance(processed_response, list):
                [in_queue.put((child[0], child[1], child[2])) for child in processed_response]
        if resp:
            out_queue.put((url, resp))
    print("Process {} done.".format(p))
    out_queue.put(end_sentinal)
    raise SystemExit(0)

if __name__ == "__main__":
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
    while True:
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
        if isinstance(resp_tuple[1], Exception):
            print("{} : {}".format(str(resp_tuple[0]), str(resp_tuple[1])))
        else:
            print("{} : {}".format(str(resp_tuple[0]), str(resp_tuple[1].status_code)))
    [p.join() for p in worker_procs]
    end = time.time()
    print(visited)
    print("Duration: {} seconds".format(end - begin))