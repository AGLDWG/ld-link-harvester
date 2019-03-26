DROP TABLE IF EXISTS Seed;
DROP TABLE IF EXISTS Crawl;
DROP TABLE IF EXISTS CrawlSeeds;
DROP TABLE IF EXISTS FailedSeed;
DROP TABLE IF EXISTS Link;
DROP TABLE IF EXISTS RdfURI;

CREATE TABLE Seed(
	seedURI VARCHAR(2083) NOT NULL,
	invalidationDate INTEGER,
	PRIMARY KEY (seedURI)
);

CREATE TABLE Crawl(
        crawlId INTEGER NOT NULL,
        startDate INTEGER DEFAULT (strftime('%s','now')),
        endDate INTEGER,
        PRIMARY KEY (crawlId)
);

CREATE TABLE Link(
	address VARCHAR(2083) NOT NULL,
	originSeedURI VARCHAR(2083) NOT NULL,
	crawlId VARCHAR(2083) NOT NULL,
	dateVisited INTEGER DEFAULT (strftime('%s','now')) NOT NULL,
	contentFormat VARCHAR(30) NOT NULL,
	failed INTEGER DEFAULT (0) NOT NULL,
	PRIMARY KEY (address, originSeedURI, crawlId),
	CONSTRAINT fk_links1 FOREIGN KEY (originSeedURI) REFERENCES Seed (seedURI),
	CONSTRAINT fk_links2 FOREIGN KEY (crawlID) REFERENCES Crawl (crawlId),
	CONSTRAINT fk_links3 FOREIGN KEY (originSeedURI) REFERENCES Seed (seedURI),
	CONSTRAINT check_failed CHECK (failed in (0, 1))
);

CREATE TABLE CrawlSeeds(
	seedURI VARCHAR(2083) NOT NULL,
	crawlId INTEGER NOT NULL,
	PRIMARY KEY (seedURI, crawlId),
	CONSTRAINT fk_crawlseeds1 FOREIGN KEY (seedURI) REFERENCES Seed (seedURI),
	CONSTRAINT fk_crawlseeds2 FOREIGN KEY (crawlId) REFERENCES Crawl (crawlId)
);

CREATE TABLE FailedSeed(
	seedURI VARCHAR(2083) NOT NULL,
	crawlId INTEGER NOT NULL,
	statusCode VARCHAR(3) NOT NULL,
	requestDate INTEGER DEFAULT (strftime('%s','now')) NOT NULL,
	PRIMARY KEY (seedURI, crawlId),
	CONSTRAINT fk_retryseed1 FOREIGN KEY (seedURI) REFERENCES Seed (seedURI),
	CONSTRAINT fk_retryseed2 FOREIGN KEY (crawlId) REFERENCES Crawl (crawlId)
);

CREATE TABLE RdfURI(
	rdfSeedURI VARCHAR(2083) NOT NULL,
	originSeedURI VARCHAR(2083) NOT NULL,
	crawlId INTEGER NOT NULL,
	contentFormat VARCHAR(30),
	PRIMARY KEY (rdfSeedURI, originSeedURI, crawlId),
	CONSTRAINT fk_rdfuri3 FOREIGN KEY (rdfSeedURI, originSeedURI, crawlId) REFERENCES Link(address, originSeedURI, crawlId)
);
