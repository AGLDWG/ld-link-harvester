import requests
import pickle
from multiprocessing import Queue, Process, Manager
import time
import signal
import sqlite3
import os
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from lddatabase import LDHarvesterDatabaseConnector

# Set Global Variables
URL_SOURCE = 'single_URI.txt'
if len(sys.argv) > 1:
    URL_SOURCE = sys.argv[1]
WORK_QUEUE_OVERFLOW_FILE = 'data/overflow_urls.txt'
AUTO_PROCESS_OVERFLOW = True
DATABASE_FILE = 'data/ld-database.db'
DATABASE_TEMPLATE = '../database/create_database.sql'
SCHEMA_INTEGRITY_CHECK = True  # If False and not creating new db, do not need template file. RECOMMEND TO LEAVE True.
CRAWL_RECORD_REPAIR = True
RECURSION_DEPTH_LIMIT = 3
PROC_COUNT = 8
COMMIT_FREQ = 50
WORK_QUEUE_MAX_SIZE = 1000000
RESP_QUEUE_MAX_SIZE = 1000000
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
BLACKLIST_FORMATS = [
    'jpg',
    'JPG',
    'BMP',
    'bmp',
    'png',
    'PNG',
    'jpeg',
    'JPEG',
    'MP4',
    'mp4',
    'flv',
    'pdf',
    'PDF',
    'eps',
    'EPS',
    'svg',
    'SVG'
]

def verify_database(connector, template):
    """
    Verifies the schema of the database attached to a connector against an external SQL script (template).
    :param connector: lddatabase.LDHarvesterDatabaseConnector
    :param template:  str
    :return: bool
    """
    virtual_db = sqlite3.Connection(':memory:')
    virtual_cursor = virtual_db.cursor()
    with open(template, 'r') as script:
        virtual_cursor.executescript(script.read())
    if virtual_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall() == connector.cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall():
        return True
    else:
        return False


def connect(database_file, crawl=True):
    """
    Connect to the database as necessary using the custom database connector (uses the database file name provided). A new crawl is also created if specified.
    :param database_file: str
    :param crawl: bool = True
    :return: tuple
    """
    print('Opening connector to database...')
    try:
        if os.path.isfile(database_file):
            dbconnector = LDHarvesterDatabaseConnector(database_file)
            print("Successfully connected to '{}'.".format(database_file))
            if crawl:
                crawlid = dbconnector.get_new_crawlid()
                dbconnector.insert_crawl(crawlid)
                return dbconnector, crawlid
            else:
                return dbconnector, None
        else:
            print("Cannot find '{}'.".format(database_file))
            ans = str(input("Would you like to create '{}' now? [y/n] ".format(database_file)))
            if ans.lower() == 'y':
                dbconnector = LDHarvesterDatabaseConnector(database_file)
                with open(DATABASE_TEMPLATE, 'r') as script:
                    dbconnector.cursor.executescript(script.read())
                print("Successfully created '{}'.".format(database_file))
                if crawl:
                    crawlid = dbconnector.get_new_crawlid()
                    dbconnector.insert_crawl(crawlid)
                    return dbconnector, crawlid
                else:
                    return dbconnector, 0
            else:
                print('Exiting')
                exit(0)
    except Exception as er:
        print("Could not connect to a database. Something went wrong...")
        print("\t{}".format(er))
        exit(1)


def close():
    """
    End the crawl, commit database changes and close the database connection.
    :return: None
    """
    dbconnector.end_crawl(crawlid)
    dbconnector.commit()
    dbconnector.close()
    print("Connection Closed.")


def find_links_html(response_content, uri, seed, depth=0):
    """
    Take web response content, create a beautifulsoup map of it and find appropriate links to visit.
    :param response_content: str
    :param uri: str
    :param seed: str
    :param depth: int
    :return: list
    """
    links = []
    soup = BeautifulSoup(response_content, "lxml")
    for link in soup.findAll('a'):
        link = link.get('href')
        link = urljoin(uri, link)
        link = link.split('#')[0]
        if urlparse(link).path.split('/')[-1].split('.')[-1] in BLACKLIST_FORMATS:
            continue
        if isinstance(link, str):
            links.append((link, depth, seed))
    return links


def process_response(response, uri, seed, depth):
    """
    Process a response appropriately and generate an 'enhanced response' containing metadata about the response and approptiate actions to do with it.
    :param response: requests.Response()
    :param uri: str
    :param seed: str
    :param depth: int
    :return: tuple or dict
    """
    try:
        file_format = response.headers['Content-type'].split(';')[0]
    except:
        print('Bad response from {}. Continuing'.format(uri))
        enhanced_resp = {'url': uri,
                         'opcode': 2,
                         'params': {'source': seed, 'format': "N/A", 'failed': 1}}
        return enhanced_resp
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
                if urlparse(uri).netloc == urlparse(seed).netloc:
                    if depth == 0 and len(response.history) > 0 and response.history[0].status_code in [300, 301, 302, 303, 304, 305, 307, 308]:
                        try:
                            seed = "http://" + urlparse(response.history[0].headers['Location']).netloc
                            uri = response.history[0].headers['Location']
                        except Exception as er:
                            print("Could not find redirect location in headers for {}: {}".format(uri, er))
                    child_links = find_links_html(response.content, uri, seed, depth+1)
                    enhanced_resp = {'url': uri,
                                    'opcode': 2,
                                    'params': {'source': seed, 'format': file_format, 'failed': 0}}
                    return enhanced_resp, child_links
                else:
                    enhanced_resp = {'url': uri,
                                     'opcode': 2,
                                     'params': {'source': seed, 'format': file_format, 'failed': 0}}
                    return enhanced_resp
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


start_sentinel = "start"
end_sentinel = "end"


def worker_fn(p, in_queue, out_queue, visited):
    """
    Individual worker function which takes items from the work queue, sends a request and adds the processed response to the response queue.
    :param p: str
    :param in_queue: multiprocessing.Queue
    :param out_queue: multiprocessing.Queue
    :param visited: dict
    :return: None
    """
    print("Process {} started.".format(p))
    out_queue.put(start_sentinel)
    while not in_queue.empty():
        url = in_queue.get()
        url, depth, seed = url
        try:
            if url not in visited and depth <= RECURSION_DEPTH_LIMIT:
                visited[url] = True
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
            in_queue = add_bulk_to_work_queue(in_queue, processed_response[1], visited)
            out_queue.put((processed_response[0], resp))
        else:
            out_queue.put((processed_response, resp))
    print("Process {} done.".format(p))
    out_queue.put(end_sentinel)
    raise SystemExit(0)


def add_bulk_to_work_queue(queue, content_list, visited_urls=dict()):
    """
    Add a bulk load of URIs to a queue at once.
    :param queue: multiprocessing.Queue()
    :param content_list: list
    :param visited_urls: dict
    :return: multiprocessing.Queue()
    """
    full_msg = False
    for child in content_list:
        if queue.full():
            if not full_msg:
                print("Work Queue is full. Flushing content to disk.")
                full_msg = True
            if child[0] not in visited_urls:
                with open(WORK_QUEUE_OVERFLOW_FILE, 'a') as overflow:
                    overflow.write("{} {} {}\n".format(child[0], child[1], child[2]))
        else:
            full_msg = False
            if child[0] not in visited_urls:
                queue.put((child[0], child[1], child[2]))
    return queue


if __name__ == "__main__":
    """
    Main runtime script. Essentially calls on the functions as appropriate. Handles workers, and processes contents of the response queue.
    """
    URL_BATCH = [(url.strip(), 0, url.strip()) for url in open(URL_SOURCE)]
    dbconnector, crawlid = connect(DATABASE_FILE)
    if SCHEMA_INTEGRITY_CHECK:
        if verify_database(dbconnector, DATABASE_TEMPLATE):
            print("Database schema integrity has been verified.")
        else:
            print("Error, database schema does not match the provided template.")
            exit(1)
    if CRAWL_RECORD_REPAIR:
        repairs_required, repairs_made = dbconnector.self_repair_crawl_periods()
        if repairs_required != 0:
            print("Repairing Crawl records.\nRepairs Required: {}\nRepairs Made: {}".format(repairs_required, repairs_made))
        else:
            print("No Crawl record repairs are required.")
    print("Adding seeds to database.")
    dbconnector.insert_seed_bulk(URL_BATCH)
    dbconnector.commit()
    print("Seeds added to database.")
    signal.signal(signal.SIGTERM, close)
    signal.signal(signal.SIGINT, close)
    full_msg = False
    manager = Manager()
    visited = manager.dict()
    work_queue = manager.Queue(maxsize=WORK_QUEUE_MAX_SIZE)
    work_queue = add_bulk_to_work_queue(work_queue, URL_BATCH)
    resp_queue = manager.Queue(maxsize=RESP_QUEUE_MAX_SIZE)
    begin = time.time()
    while True:
        worker_procs = []
        for i in range(PROC_COUNT):
            p = Process(target=worker_fn, args=(i+1, work_queue, resp_queue, visited))
            worker_procs.append(p)
        [p.start() for p in worker_procs]
        # wait for processes to start
        time.sleep(0.1)
        threads_started = 0
        threads_ended = 0
        i = 0
        while True:
            #print(resp_queue.qsize())
            if i >= COMMIT_FREQ:
                dbconnector.commit()
                i =- 1
            i += 1
            resp_tuple = resp_queue.get()
            if resp_tuple == start_sentinel:
                threads_started += 1
                continue
            elif resp_tuple == end_sentinel:
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
            if isinstance(resp_tuple[1], Exception):
                print("{} : {}".format(str(resp_tuple[0]['url']), str(resp_tuple[1])))
            else:
                print("{} : {}".format(str(resp_tuple[0]['url']), str(resp_tuple[1].status_code)))
        [p.join() for p in worker_procs]
        if not AUTO_PROCESS_OVERFLOW:
            break
        else:
            if os.path.isfile(WORK_QUEUE_OVERFLOW_FILE):
                new_urls = [(url.split()[0], int(url.split()[1]), url.split()[2]) for url in open(WORK_QUEUE_OVERFLOW_FILE, 'r')]
                open(WORK_QUEUE_OVERFLOW_FILE, 'w').close()
                if len(new_urls) > 0:
                    add_bulk_to_work_queue(work_queue, new_urls, visited)
                    continue
                else:
                    break
            else:
                break
    end = time.time()
    close()
    print("Duration: {} seconds".format(end - begin))
