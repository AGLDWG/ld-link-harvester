import harvester
from multiprocessing import Queue, Process, Manager

WORK_QUEUE_MAX_SIZE = 100
RESP_QUEUE_MAX_SIZE = 100
URL_BATCH = [("http://127.0.0.1:8080", 0, "http://127.0.0.1:8080")]
manager = Manager()
visited = manager.dict()
work_queue = manager.Queue(maxsize=WORK_QUEUE_MAX_SIZE)
work_queue = harvester.add_bulk_to_work_queue(work_queue, URL_BATCH)
resp_queue = manager.Queue(maxsize=RESP_QUEUE_MAX_SIZE)
proc = Process(target=harvester.worker_fn, args=(1, work_queue, resp_queue, visited))
proc.start()
proc.join()
results = []
visited_links = []
while not resp_queue.empty():
    out_entry = resp_queue.get()
    if out_entry in ['start', 'end']:
        continue
    visited_links.append(out_entry[0]['url'])
    results.append(out_entry)


def test_worker():
    """
    Worker should recursively search a web domain and find all links up to a specific depth.
    """
    assert len(set(visited)) == 16


def test_visited_dictionary():
    expected_visited = {'http://127.0.0.1:8080': True,
                        'http://127.0.0.1:8080/index.html': True,
                        'http://127.0.0.1:8080/birds.html': True,
                        'http://127.0.0.1:8080/mammals.html': True,
                        'http://127.0.0.1:8080/fish.html': True,
                        'http://127.0.0.1:8080/reptiles.html': True,
                        'http://127.0.0.1:8080/amphibians.html': True,
                        'http://127.0.0.1:8080/anthropods.html': True,
                        'http://127.0.0.1:8080/form.html': True,
                        'http://127.0.0.1:8080/contact.html': True,
                        'https://www.australia.com/en/facts-and-planning/australias-animals.html': True,
                        'https://en.wikipedia.org/wiki/Fauna_of_Australia': True,
                        'https://www.csiro.au/en/Research/Collections/ANIC': True,
                        'http://127.0.0.1:8080/amphibians/growling.html': True,
                        'http://127.0.0.1:8080/amphibians/crucifix.html': True,
                        'http://127.0.0.1:8080/amphibians/red-crowned.html': True}
    assert list(visited.keys()) == list(expected_visited.keys())


def test_worker_visited_once():
    """
    Links should only be visited once per crawl and ignored if already visited
    """
    assert len(set(visited_links)) == len(visited_links)
