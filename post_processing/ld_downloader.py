import rdflib
import requests
import bs4
import os
import sys
import shutil

URL_FILE = "C:\\Users\\Has112\\Documents\\db_history\\21-05-2019\\rdf_seeds.txt"
FAILED_URL_OUT = 'url_failed.txt'
PASSED_URL_OUT = 'url_passed.txt'
URL_ID_KEY_OUT = 'url_key.txt'
LD_OUT_DIR = 'ld_store'
FAILED_LOG_FILE = 'url_log.txt'

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


def parse_embedded_ld_json(content):
    rdf_data = []
    soup = bs4.BeautifulSoup(content, "lxml")
    scripts = soup.find_all('script')
    for script in scripts:
        if script.get('type') == 'application/ld+json':
            rdf_data.append(script.get_text())
    return rdf_data


URL_BATCH = open(URL_FILE).readlines()
if not os.path.isfile(FAILED_URL_OUT):
    open(FAILED_URL_OUT, 'w').close()
if not os.path.isfile(FAILED_LOG_FILE):
    open(FAILED_LOG_FILE, 'w').close()
if not os.path.isfile(PASSED_URL_OUT):
    open(PASSED_URL_OUT, 'w').close()
if not os.path.isfile(URL_ID_KEY_OUT):
    open(URL_ID_KEY_OUT, 'w').close()
    key_counter = 0
else:
    lines = open(URL_ID_KEY_OUT, 'r').readlines()
    key_counter = int(lines[-1].split('.ttl')[0]) if len(lines) > 0 else 0
if not os.path.exists(LD_OUT_DIR):
    os.mkdir(LD_OUT_DIR)

key_counter = 0
for url in URL_BATCH:
    url = url.strip()
    print("Validating '{}'.".format(url))

    g = rdflib.Graph()
    r = requests.get(url, headers=GLOBAL_HEADER)

    if r.status_code == 200:
        response_content_type = r.headers['content-type'].split(';')[0]
        try:
            if 'application/ld+json' in r.text:
                ld_json = parse_embedded_ld_json(r.content)
                if len(ld_json) > 0:
                    for array in ld_json:
                        g.parse(data=array, format='json-ld')
                    with open('{}/{}.ttl'.format(LD_OUT_DIR, key_counter), 'w') as f:
                        f.write(g.serialize(format='turtle').decode('utf-8'))
                    with open(URL_ID_KEY_OUT, 'a') as f:
                        f.write('{}.ttl\t{}\n'.format(key_counter, url))
                    key_counter += 1
                else:
                    with open(FAILED_URL_OUT, 'a') as f:
                        f.write('{url}\n'.format(url=url))
                    with open(FAILED_LOG_FILE, 'a') as f:
                        f.write('{url}\nNo JSON_LD data found.\n\n'.format(url=url))
            else:
                g.parse(data=r.text, format=response_content_type)
                with open('{}/{}.ttl'.format(LD_OUT_DIR, key_counter), 'w') as f:
                    f.write(g.serialize(format='turtle').decode('utf-8'))
                with open(URL_ID_KEY_OUT, 'a') as f:
                    f.write('{}.ttl\t{}\n'.format(key_counter, url))
                key_counter += 1
            print('Passed! {} Triplets.'.format(len(g)))
            with open(PASSED_URL_OUT, 'a') as f:
                f.write('{url}\n'.format(url=url))
        except Exception as e:
            print(e)
            with open(FAILED_URL_OUT, 'a') as f:
                f.write('{url}\n'.format(url=url))
            with open(FAILED_LOG_FILE, 'a') as f:
                f.write('{url}\n{error}\n\n'.format(url=url, error=e))
    else:
        print("Url '{}' broken.".format('url'))
        with open(FAILED_URL_OUT, 'a') as f:
            f.write('{url}\n'.format(url=url))
        with open(FAILED_LOG_FILE, 'a') as f:
            f.write('{url}\nBroken.\n'.format(url=url))