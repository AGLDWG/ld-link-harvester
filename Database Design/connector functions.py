def insert_crawl_seed(uri, crawlid):
    insert_seed(uri)
    try:
        cursor.execute("INSERT INTO CrawlSeeds (seedURI, crawlId) VALUES ('{uri}', {crawlId})".format(uri=uri, crawlId=crawlid))
    except sqlite3.Error as er:
        print(er, end='\n\t...')
        if str(er) == 'UNIQUE constraint failed: CrawlSeeds.seedURI, CrawlSeeds.crawlId':
            print("Already tested the '{}' seed during this crawl.".format(uri))


def insert_seed(uri):
    try:
        cursor.execute("INSERT INTO Seed (seedURI) VALUES ('{uri}')".format(uri=uri))
    except sqlite3.Error as er:
        print(er, end='\n\t...')
        if str(er) == 'UNIQUE constraint failed: Seed.seedURI':
            print("'{}' Already in Seeds!".format(uri))


def insert_link(uri, crawlid, source, failed=0):
    try:
        cursor.execute("Insert INTO Link (address, crawlId, originSeedURI, failed) VALUES ('{uri}', '{crawlId}', '{source}', {failed})".format(uri=uri, crawlId=crawlid, source=source, failed=failed))
    except sqlite3.Error as er:
        print(er, end='\n\t...')
        if str(er) == 'UNIQUE constraint failed: Link.address, Link.originSeedURI, Link.crawlId':
            print("'{}' Already visited in this crawl through this seed. Ignoring.".format(uri))


def insert_crawl(crawlid):
    try:
        cursor.execute("INSERT INTO Crawl (crawlId) VALUES ({crawlId})".format(crawlId=crawlid))
    except sqlite3.Error as er:
        print(er)
        if str(er) == 'UNIQUE constraint failed: Crawl.crawlId':
            print('\t...crawlId exists.')
        print('Critical Error.')
        print('Exiting!')
        exit(1)


def insert_valid_rdfuri(uri, crawlid, source, response_format):
    try:
        cursor.execute("INSERT INTO RdfURI (rdfSeedURI, crawlId, originSeedURI, contentFormat) VALUES ('{uri}', {crawlId}, '{source}', '{format}')".format(uri=uri, crawlId=crawlid, source=source, format=response_format))
    except sqlite3.Error as er:
        print(er, end='\n\t...')
        if str(er) == 'UNIQUE constraint failed: RdfURI.rdfSeedURI, RdfURI.originSeedURI, RdfURI.crawlId':
            print("'{}' - '{}' pair is already discovered in this crawl! Ignoring.".format(uri, source))


def insert_failed_seed(uri, crawlid, code):
    try:
        cursor.execute("INSERT INTO FailedSeed (seedURI, crawlId, statusCode) VALUES ('{uri}', {crawlId}, '{code}')".format(uri=uri, crawlId=crawlid, code=code))
    except sqlite3.Error as er:
        print(er, end='\n\t...')
        if str(er) == 'UNIQUE constraint failed: FailedSeed.seedURI, FailedSeed.crawlId':
            print("Already attempted and failed to request '{}' during this crawl. Ignoring.".format(uri))