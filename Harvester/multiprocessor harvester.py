import requests
from multiprocessing import Queue, Process, Manager
import time

URL_BATCH = [url.strip() for url in open('single_URI.txt')]
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
start_sentinal = "start"
end_sentinal = "end"
def worker_fn(p, in_queue, out_queue, visited):
    print("Process {} started.".format(p))
    out_queue.put(start_sentinal)
    while not in_queue.empty():
        url = in_queue.get()
        #print("Process: {}, getting: {}".format(p, url))
        try:
            if url not in visited:
                resp = requests.get(url, headers=GLOBAL_HEADER)
                visited[url.strip('/#')] = True
            else:
                resp = None
        except Exception as e:
            resp = None
            out_queue.put((url, e))
        if resp:
            out_queue.put((url, resp))
    print("Process {} done.".format(p))
    out_queue.put(end_sentinal)
    raise SystemExit(0)

if __name__ == "__main__":
    visited = Manager().dict()
    work_queue = Queue()
    [work_queue.put(i) for i in URL_BATCH]
    resp_queue = Queue()
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