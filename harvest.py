from multiprocessing import Process, Manager, current_process
import time
import os
import sys
import harvester
import pickle

# Set Global Variables
URL_SOURCE = 'URI.txt'
if len(sys.argv) > 1:
    URL_SOURCE = sys.argv[1]
AUTO_PROCESS_OVERFLOW = True
DATABASE_FILE = 'data/ld-database.db'
DATABASE_TEMPLATE = 'database/create_database.sql'
RESTORE_SESSION = False
# WORK_QUEUE_BACKUP = 'data/work_queue_backup_{}.queue'.format(URL_SOURCE.split('/')[-1].split('.txt')[0])
WORK_QUEUE_BACKUP = 'data/work_queue_backup_{}.bqueue'.format(URL_SOURCE.split('/')[-1].split('.txt')[0])
SESSION_AUTH_KEY_BACKUP = 'data/work_queue_backup_{}.authkey'.format(URL_SOURCE.split('/')[-1].split('.txt')[0])
WORK_QUEUE_OVERFLOW_FILE = 'data/{}_overflow.txt'.format(URL_SOURCE.split('/')[-1])
SCHEMA_INTEGRITY_CHECK = True
CRAWL_RECORD_REPAIR = True
RESPONSE_TIMEOUT = 60
MAX_REDIRECTS = 3
KILL_PROCESSES_TIMEOUT = 600
RECURSION_DEPTH_LIMIT = 3
PROC_COUNT = 8
COMMIT_FREQ = 50
WORKQ_BACKUP_FREQUENCY = 5
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

#Override Harvester Module Settings With User Selected Values
global_vars = globals().copy()
for var in global_vars:
    if var in locals() or var in globals():
        if var == 'DATABASE_TEMPLATE':
            harvester.DATABASE_TEMPLATE = DATABASE_TEMPLATE
        elif var == 'WORK_QUEUE_OVERFLOW_FILE':
            harvester.WORK_QUEUE_OVERFLOW_FILE = WORK_QUEUE_OVERFLOW_FILE
        elif var == 'AUTO_PROCESS_OVERFLOW':
            harvester.AUTO_PROCESS_OVERFLOW = AUTO_PROCESS_OVERFLOW
        elif var == 'DATABASE_FILE':
            harvester.DATABASE_FILE = DATABASE_FILE
        elif var == 'SCHEMA_INTEGRITY_CHECK':
            harvester.SCHEMA_INTEGRITY_CHECK = SCHEMA_INTEGRITY_CHECK
        elif var == 'CRAWL_RECORD_REPAIR':
            harvester.CRAWL_RECORD_REPAIR = CRAWL_RECORD_REPAIR
        elif var == 'RESPONSE_TIMEOUT':
            harvester.RESPONSE_TIMEOUT = RESPONSE_TIMEOUT
        elif var == 'KILL_PROCESSES_TIMEOUT':
            harvester.KILL_PROCESSES_TIMEOUT = KILL_PROCESSES_TIMEOUT
        elif var == 'MAX_REDIRECTS':
            harvester.MAX_REDIRECTS = MAX_REDIRECTS
        elif var == 'RECURSION_DEPTH_LIMIT':
            harvester.RECURSION_DEPTH_LIMIT = RECURSION_DEPTH_LIMIT
        elif var == 'PROC_COUNT':
            harvester.PROC_COUNT = PROC_COUNT
        elif var == 'COMMIT_FREQ':
            harvester.COMMIT_FREQ = COMMIT_FREQ
        elif var == 'WORK_QUEUE_MAX_SIZE':
            harvester.WORK_QUEUE_MAX_SIZE = WORK_QUEUE_MAX_SIZE
        elif var == 'RESP_QUEUE_MAX_SIZE':
            harvester.RESP_QUEUE_MAX_SIZE = RESP_QUEUE_MAX_SIZE
        elif var == 'RDF_MEDIA_TYPES':
            harvester.RDF_MEDIA_TYPES = RDF_MEDIA_TYPES
        elif var == 'RDF_FORMATS':
            harvester.RDF_FORMATS = RDF_FORMATS
        elif var == 'GLOBAL_HEADER':
            harvester.GLOBAL_HEADER = GLOBAL_HEADER
        elif var == 'BLACKLIST_FORMATS':
            harvester.BLACKLIST_FORMATS = BLACKLIST_FORMATS


if __name__ == "__main__":
    """
    Main runtime script. Essentially calls on the functions as appropriate. Handles workers, and processes contents of the response queue.
    """
    dbconnector, crawlid = harvester.connect(DATABASE_FILE)
    if SCHEMA_INTEGRITY_CHECK:
        if harvester.verify_database(dbconnector, DATABASE_TEMPLATE):
            print("Database schema integrity has been verified.")
        else:
            print("Error, database schema does not match the provided template.")
            exit(1)
    if CRAWL_RECORD_REPAIR:
        repairs_required, repairs_made = dbconnector.self_repair_crawl_periods()
        if repairs_required != 0:
            print("Repairing Crawl records.\nRepairs Required: {}\nRepairs Made: {}".format(repairs_required,
                                                                                            repairs_made))
        else:
            print("No Crawl record repairs are required.")
    if not RESTORE_SESSION:
        URL_BATCH = [(url.strip(), 0, url.strip()) for url in open(URL_SOURCE)]
        print("Adding seeds to database.")
        dbconnector.insert_seed_bulk(URL_BATCH)
        dbconnector.commit()
        print("Seeds added to database.")
    full_msg = False
    manager = Manager()
    visited = manager.dict()
    if not RESTORE_SESSION:
        with open(SESSION_AUTH_KEY_BACKUP, 'wb') as key_file:
            key_file.write(current_process().authkey)
        work_queue = manager.Queue(maxsize=WORK_QUEUE_MAX_SIZE)
        work_queue = harvester.add_bulk_to_work_queue(work_queue, URL_BATCH)
    else:
        try:
            with open(SESSION_AUTH_KEY_BACKUP, 'rb') as key_file:
                authkey = key_file.read()
            current_process().authkey = authkey
        except Exception as e:
            print('Error restoring session authkey: {}'.format(e))
            exit(1)
        try:
            with open(WORK_QUEUE_BACKUP, 'rb') as backup_file:
                work_queue = pickle.load(backup_file)
        except Exception as e:
            print("Error restoring session work queue from '{}': {}".format(WORK_QUEUE_BACKUP, e))
            exit(1)
    resp_queue = manager.Queue(maxsize=RESP_QUEUE_MAX_SIZE)
    begin = time.time()
    while True:
        worker_procs = []
        for i in range(PROC_COUNT):
            p = Process(target=harvester.worker_fn, args=(i+1, work_queue, resp_queue, visited))
            worker_procs.append(p)
        [p.start() for p in worker_procs]
        # wait for processes to start
        time.sleep(0.1)
        threads_started = 0
        threads_ended = 0
        i = 0
        j = 0
        emergency_timeout_start = time.time()
        emergency_timeout = False
        while True:
            if not resp_queue.empty():
                emergency_timeout_start = time.time()
            if i >= COMMIT_FREQ:
                dbconnector.commit()
                i =- 1
            if j >= WORKQ_BACKUP_FREQUENCY:
                with open(WORK_QUEUE_BACKUP, 'wb+') as backup_file:
                    pickle.dump(work_queue, backup_file)
                j = -1
            i += 1
            j += 1
            resp_tuple = resp_queue.get()
            if resp_tuple == harvester.start_sentinel:
                threads_started += 1
                continue
            elif resp_tuple == harvester.end_sentinel:
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
            if time.time() - emergency_timeout_start > KILL_PROCESSES_TIMEOUT:
                print("FROZEN. Emergency Timeout.")
                emergency_timeout = True
                break
        if not emergency_timeout:
            [p.join() for p in worker_procs]
        else:
            [p.terminate() for p in worker_procs]
            if not work_queue.empty():
                emergency_timeout = False
                continue
        if time.time() - emergency_timeout_start > KILL_PROCESSES_TIMEOUT:
            print("FROZEN. Emergency Timeout.")
            emergency_timeout = True
            [p.terminate() for p in worker_procs]
            break
        if not AUTO_PROCESS_OVERFLOW:
            break
        else:
            if os.path.isfile(WORK_QUEUE_OVERFLOW_FILE):
                new_urls = [(url.split()[0], int(url.split()[1]), url.split()[2]) for url in open(WORK_QUEUE_OVERFLOW_FILE, 'r')]
                open(WORK_QUEUE_OVERFLOW_FILE, 'w').close()
                if len(new_urls) > 0:
                    harvester.add_bulk_to_work_queue(work_queue, new_urls, visited)
                    continue
                else:
                    break
            else:
                break
    #os.remove(SESSION_AUTH_KEY_BACKUP)
    #os.remove(WORK_QUEUE_BACKUP)
    end = time.time()
    harvester.close(dbconnector, crawlid)
    print("Duration: {} seconds".format(end - begin))