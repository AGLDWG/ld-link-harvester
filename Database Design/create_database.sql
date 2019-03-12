CREATE TABLE Seed(
	seedURI VARCHAR(2083) NOT NULL,
	invalidationDate INTEGER,
	PRIMARY KEY (seedURI)
);

CREATE TABLE Links(
	address VARCHAR(2083) NOT NULL,
	originalSeed VARCHAR(2083) NOT NULL,
	PRIMARY KEY (address, originalSeed),
	CONSTRAINT fk_links1 FOREIGN KEY (originalSeed) REFERENCES Seed(seedURI)
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
	statusCode varchar(3) NOT NULL,
	requestDate INTEGER DEFAULT (strftime('%s','now')) NOT NULL,
	PRIMARY KEY (seedURI, crawlId),
	CONSTRAINT fk_retryseed1 FOREIGN KEY (seedURI) REFERENCES Seed (seedURI),
	CONSTRAINT fk_retryseed2 FOREIGN KEY (crawlId) REFERENCES Crawl (crawlId)
);

CREATE TABLE RdfURI(
	rdfSeedURI VARCHAR(2083) NOT NULL,
	crawlId VARCHAR(2083) NOT NULL,
	originSeedURI VARCHAR(2083) NOT NULL,
	dateDiscovered INTEGER DEFAULT (strftime('%s','now')) NOT NULL,
	contentFormat VARCHAR(30),

	PRIMARY KEY (rdfSeedURI, originSeedURI, crawlId),
	CONSTRAINT fk_rdfuri1 FOREIGN KEY (crawlID) REFERENCES Crawl (crawlId),
	CONSTRAINT fk_rdfuri2 FOREIGN KEY (originSeedURI) REFERENCES Seed (seedURI)
);


