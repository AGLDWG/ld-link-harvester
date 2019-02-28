import requests
from bs4 import BeautifulSoup
import re

def find_links(content, uri):
    #print(content)
    links = []
    soup = BeautifulSoup(content, "lxml")
    for link in soup.findAll('a'):
        link = link.get('href')
        if isinstance(link, str):
            if link.startswith('/'):
                link = uri + link
            if uri in link:
                print(link)
    return links

if __name__=='__main__':
    uri = 'http://linked.data.gov.au/showcase'
    print(find_links(requests.get(uri, headers={'Accept': 'text/html'}).content.decode('utf-8'), uri))
