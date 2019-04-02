import requests
from multiprocessing import Queue, Process, Manager
import time
import signal
import sqlite3
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from modules.lddatabase import LDHarvesterDatabaseConnector

URL_BATCH = [(url.strip(), 0, url.strip()) for url in open('single_URI.txt')]
DATABASE_FILE = 'ld-database.db'
DATABASE_TEMPLATE = '../database/create_database.sql'
SCHEMA_INTEGRITY_CHECK = True  # If False and not creating new db, do not need template file. RECOMMEND TO LEAVE True.
RECURSION_DEPTH_LIMIT = 4
PROC_COUNT = 8
COMMIT_FREQ = 50
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
    'json'
]
GLOBAL_HEADER = {
    'Accept': ",".join(RDF_MEDIA_TYPES),
    'User-Agent': 'LD Link Harvester'
}


def verify_database(connector):
    virtual_db = sqlite3.Connection(':memory:')
    virtual_cursor = virtual_db.cursor()
    with open(DATABASE_TEMPLATE, 'r') as script:
        virtual_cursor.executescript(script.read())
    if virtual_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall() == connector.cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall():
        return True
    else:
        return False


def connect():
    print('Opening connector to database...')
    try:
        if os.path.isfile(DATABASE_FILE):
            dbconnector = LDHarvesterDatabaseConnector(DATABASE_FILE)
            print("Successfully connected to '{}'.".format(DATABASE_FILE))
            crawlid = dbconnector.get_new_crawlid()
            dbconnector.insert_crawl(crawlid)
            if SCHEMA_INTEGRITY_CHECK:
                if verify_database(dbconnector):
                    print("Database schema integrity has been verified.")
                else:
                    print("Error, database schema does not match the provided template.")
                    exit(1)
            return dbconnector, crawlid
        else:
            print("Cannot find '{}'.".format(DATABASE_FILE))
            ans = str(input("Would you like to create '{}' now? [y/n] ".format(DATABASE_FILE)))
            if ans.lower() == 'y':
                dbconnector = LDHarvesterDatabaseConnector(DATABASE_FILE)
                with open(DATABASE_TEMPLATE, 'r') as script:
                    dbconnector.cursor.executescript(script.read())
                print("Successfully created '{}'.".format(DATABASE_FILE))
                crawlid = dbconnector.get_new_crawlid()
                dbconnector.insert_crawl(crawlid)
                return dbconnector, crawlid
            else:
                print('Exiting')
                exit(0)
    except Exception as er:
        print("Could not connect to a database. Something went wrong...")
        print("\t{}".format(er))
        exit(1)


def close():
    dbconnector.end_crawl(crawlid)
    dbconnector.commit()
    dbconnector.close()
    print("Connection Closed.")


def find_links_html(response_content, uri, seed, depth=0):
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
            links.append((link, depth, seed))
    return links


def process_response(response, uri, seed, depth):
    file_format = response.headers['Content-type'].split(';')[0]
    if response.status_code == 200:
        if uri.split('.')[-1] in RDF_FORMATS:
            enhanced_resp = {'url': uri,
                             'opcode': 3,
                             'params':  {'source': seed, 'format': file_format}}
            return enhanced_resp
        if file_format in RDF_MEDIA_TYPES:
            enhanced_resp = {'url': uri,
                             'opcode': 3,
                             'params': {'source': seed, 'format': file_format}}
            return enhanced_resp
        elif file_format == 'text/html':
            try:
                child_links = find_links_html(response.content, uri, seed, depth+1)
                enhanced_resp = {'url': uri,
                                 'opcode': 2,
                                 'params': {'source': seed, 'format': file_format, 'failed': 0}}
                return enhanced_resp, child_links
            except Exception as er:
                print(er, end='...')
                print('Cannot decode response from {}. Continuing'.format(uri))
                enhanced_resp = {'url': uri,
                                 'opcode': 2,
                                 'params': {'source': seed, 'format': file_format, 'failed': 1}}
                return enhanced_resp
        else:
            enhanced_resp = {'url': uri,
                             'opcode': 2,
                             'params': {'source': seed,'format': file_format, 'failed': 0}}
            return enhanced_resp
    else:
        enhanced_resp = {'url': uri,
                         'opcode': 2,
                         'params': {'source': seed, 'format': file_format,'failed': 1}}
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
            enhanced_resp = {'url': url,
                             'opcode': 2,
                             'params': {'source': seed, 'format': "N/A", 'failed': 1}}
            out_queue.put((enhanced_resp, e))
            continue
        processed_response = process_response(resp, url, seed, depth)
        if isinstance(processed_response, tuple):
            [in_queue.put((child[0], child[1], child[2])) for child in processed_response[1]]
            out_queue.put((processed_response[0], resp))
        else:
            out_queue.put((processed_response, resp))
    print("Process {} done.".format(p))
    out_queue.put(end_sentinal)
    raise SystemExit(0)

if __name__ == "__main__":
    dbconnector, crawlid = connect()
    print("Adding seeds to database.")
    dbconnector.insert_seed_bulk(URL_BATCH)
    dbconnector.commit()
    print("Seeds added to database.")
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
        if i >= COMMIT_FREQ:
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
                dbconnector.insert_link(uri=resp_tuple[0]['url'], crawlid=crawlid, source=resp_tuple[0]['params']['source'], content_format=resp_tuple[0]['params']['format'], failed=resp_tuple[0]['params']['failed'])
                if resp_tuple[0]['params']['failed'] == 1 and resp_tuple[0]['url'] == resp_tuple[0]['params']['source']:
                    if isinstance(resp_tuple[1], Exception):
                        dbconnector.insert_failed_seed(uri=resp_tuple[0]['url'], crawlid=crawlid, code='000')
                    else:
                        dbconnector.insert_failed_seed(uri=resp_tuple[0]['url'], crawlid=crawlid,  code=resp_tuple[1].status_code)
            if opcode == 3:
                dbconnector.insert_link(uri=resp_tuple[0]['url'], crawlid=crawlid, source=resp_tuple[0]['params']['source'],content_format=resp_tuple[0]['params']['format'], failed=0)
                dbconnector.insert_valid_rdfuri(uri=resp_tuple[0]['url'], crawlid=crawlid, source=resp_tuple[0]['params']['source'], response_format=resp_tuple[0]['params']['format'])
        #print(resp_tuple)
        if isinstance(resp_tuple[1], Exception):
            print("{} : {}".format(str(resp_tuple[0]['url']), str(resp_tuple[1])))
        else:
            print("{} : {}".format(str(resp_tuple[0]['url']), str(resp_tuple[1].status_code)))
    [p.join() for p in worker_procs]
    end = time.time()
    close()
    print(visited)
    print("Duration: {} seconds".format(end - begin))