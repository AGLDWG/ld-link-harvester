import sqlite3

def insert_seed(uri):
    try:
        cursor.execute("INSERT INTO Seed (seedURI) VALUES ('{uri}')".format(uri=uri))
    except sqlite3.Error as er:
        print(er, end='...')
        if str(er) == 'UNIQUE constraint failed: Seed.seedURI':
            print("'{}' Already In Seeds!".format(uri))

def insert_crawl(crawlId):
    cursor.execute("INSERT INTO Crawl (crawlId) VALUES ({crawlId})".format(crawlId=crawlId))

def insert_valid_rdfuri(uri, crawlId, source):
    insert_seed(source)
    #exit(0)
    try:
        cursor.execute("INSERT INTO RdfURI (rdfSeedURI, crawlId, originSeedURI) VALUES ('{uri}', {crawlId}, '{source}')".format(uri=uri, crawlId=crawlId, source=source))
    except sqlite3.Error as er:
        print(er, end='...')
        if str(er) == 'UNIQUE constraint failed: RdfURI.rdfSeedURI, RdfURI.originSeedURI':
            print("'{}' - '{}' pair is already discovered in this crawl! Ignoring.".format(uri, source))

def insert_failed_seed(uri, crawlId, code):
    insert_seed(uri)
    try:
        cursor.execute("INSERT INTO FailedSeed (seedURI, crawlId, statusCode) VALUES ('{uri}', {crawlId}, '{code}')".format(uri=uri, crawlId=crawlId, code=code))
    except sqlite3.Error as er:
        print(er)

if __name__=='__main__':
    connector = sqlite3.Connection('/home/jake/MEGA/CSIRO/ld-link-harvester/ld-database.db')
    cursor = sqlite3.Cursor(connector)

    #insert_crawl(1)
    insert_valid_rdfuri('www.google.com/data.rdf', 1, 'google.com')
    insert_failed_seed('www.nothing.com', 1, '404')
    connector.commit()
    connector.close()