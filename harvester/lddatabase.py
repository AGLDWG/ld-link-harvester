import sqlite3
__author__ = 'Jake Hashim-Jones'


class LDHarvesterDatabaseConnector(sqlite3.Connection):
    """
    Specialized Extension of the sqlite3.connection object which adds functions to interact specifically with the ld database.
    """
    def __init__(self, file):
        super().__init__(file)
        self.cursor = sqlite3.Cursor(self)

    def get_new_crawlid(self):
        """
        Generate the next logical crawlId for the run.
        :return new_crawlid: int
        """
        response = self.cursor.execute("SELECT MAX(crawlid) FROM Crawl")
        resp = response.fetchall()[0][0]
        if resp is None:
            new_crawlid = 0
        else:
            new_crawlid = resp + 1
        return new_crawlid

    def end_crawl(self, crawlid):
        """
        Update crawl record to include finishing time (as current time).
        :param crawlid: int
        :return: None
        """
        self.cursor.execute("UPDATE Crawl SET endDate=strftime('%s','now') WHERE crawlId={crawlId}".format(crawlId=crawlid))

    def insert_crawl_seed(self, uri, crawlid, newseed=0):
        """
        Insert new record into the CrawlSeeds table.
        :param uri: str
        :param crawlid: int
        :param newseed: int
        :return: None
        """
        if newseed:
            self.insert_seed(uri)
        try:
            self.cursor.execute("INSERT INTO CrawlSeeds (seedURI, crawlId) VALUES ('{uri}', {crawlId})".format(uri=uri, crawlId=crawlid))
        except sqlite3.Error as er:
            print(er, end='\n\t...')
            if str(er) == 'UNIQUE constraint failed: CrawlSeeds.seedURI, CrawlSeeds.crawlId':
                print("Already tested the '{}' seed during this crawl.".format(uri))

    def insert_seed_bulk(self, url_list):
        """
        Insert a group of seeds from an array.
        :param url_list: list
        :return: None
        """
        for url in url_list:
            try:
                self.cursor.execute("INSERT INTO Seed (seedURI) VALUES ('{uri}')".format(uri=url[0]))
            except Exception as er:
                if str(er) == 'UNIQUE constraint failed: Seed.seedURI':
                    print("'{}' Already in Seeds!".format(url[0]))
                else:
                    print("'{}' Error: {}".format(url[0], er))

    def insert_seed(self, uri):
        """
        Insert new seed into the database.
        :param uri: str
        :return: None
        """
        try:
            self.cursor.execute("INSERT INTO Seed (seedURI) VALUES ('{uri}')".format(uri=uri))
        except sqlite3.Error as er:
            print(er, end='\n\t...')
            if str(er) == 'UNIQUE constraint failed: Seed.seedURI':
                print("'{}' Already in Seeds!".format(uri))

    def insert_link(self, uri, crawlid, source, content_format, failed=0):
        """
        Insert new link visited into the database.
        :param uri: str
        :param crawlid: str
        :param source: str
        :param content_format: str
        :param failed: int
        :return:
        """
        if failed not in [0,1]:
            print("Warning! 'failed' parameter should be 0 or 1. Making it 1.")
            failed = 1
        try:
            self.cursor.execute(
                "Insert INTO Link (address, crawlId, originSeedURI, contentFormat, failed) VALUES ('{uri}', '{crawlId}', '{source}','{contentFormat}', {failed})".format(uri=uri, crawlId=crawlid, source=source, contentFormat=content_format, failed=failed))
        except sqlite3.Error as er:
            print(er, end='\n\t...')
            if str(er) == 'UNIQUE constraint failed: Link.address, Link.originSeedURI, Link.crawlId':
                print("'{}' Already visited in this crawl through this seed. Ignoring.".format(uri))

    def insert_crawl(self, crawlid):
        """
        Create new entry for crawl in the database.
        :param crawlid: int
        :return: None
        """
        try:
            self.cursor.execute("INSERT INTO Crawl (crawlId) VALUES ({crawlId})".format(crawlId=crawlid))
        except sqlite3.Error as er:
            print(er)
            if str(er) == 'UNIQUE constraint failed: Crawl.crawlId':
                print('\t...crawlId exists.')
            print('Critical Error.')
            print('Exiting!')
            exit(1)

    def insert_valid_rdfuri(self, uri, crawlid, source, response_format):
        """
        Insert valid URI pointing to RDF data into the appropriate table.
        :param uri:  str
        :param crawlid: int
        :param source: str
        :param response_format: str
        :return: None
        """
        try:
            self.cursor.execute(
                "INSERT INTO RdfURI (rdfSeedURI, crawlId, originSeedURI, contentFormat) VALUES ('{uri}', {crawlId}, '{source}', '{format}')".format(uri=uri, crawlId=crawlid, source=source, format=response_format))
        except sqlite3.Error as er:
            print(er, end='\n\t...')
            if str(er) == 'UNIQUE constraint failed: RdfURI.rdfSeedURI, RdfURI.originSeedURI, RdfURI.crawlId':
                print("'{}' - '{}' pair is already discovered in this crawl! Ignoring.".format(uri, source))

    def insert_failed_seed(self, uri, crawlid, code):
        """
        Record if a seed specifically fails in the database.
        :param uri: str
        :param crawlid: int
        :param code: str
        :return: None
        """
        try:
            self.cursor.execute(
                "INSERT INTO FailedSeed (seedURI, crawlId, statusCode) VALUES ('{uri}', {crawlId}, '{code}')".format(
                    uri=uri, crawlId=crawlid, code=code))
        except sqlite3.Error as er:
            print(er, end='\n\t...')
            if str(er) == 'UNIQUE constraint failed: FailedSeed.seedURI, FailedSeed.crawlId':
                print("Already attempted and failed to request '{}' during this crawl. Ignoring.".format(uri))


if __name__ == '__main__':
    connector = LDHarvesterDatabaseConnector('..\ld-database.db')
    crawlid = connector.get_new_crawlid()
    connector.insert_crawl(crawlid)
    connector.insert_crawl_seed('www.nothing.com', crawlid)
    connector.insert_failed_seed('www.nothing.com', crawlid, '404')
    connector.insert_crawl_seed('www.google.com', crawlid)
    connector.insert_link('www.google.com/data.rdf', crawlid, 'www.google.com')
    connector.insert_valid_rdfuri('www.google.com/data.rdf', crawlid, 'google.com', 'application/rdf+xml')
    connector.insert_link('www.google.com/no_data.rdf', crawlid, 'www.google.com', 1)
    from time import sleep
    sleep(2)
    connector.end_crawl(crawlid)
    connector.commit()
    connector.close()