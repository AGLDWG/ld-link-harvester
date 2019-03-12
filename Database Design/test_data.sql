-- Crawl 1 Data
INSERT INTO Crawl (crawlID, endDate) VALUES (1, Null);

INSERT INTO Seed (seedURI) VALUES ('https://www.chapman.org/blog/blog/search.html');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('https://www.chapman.org/blog/blog/search.html', 1);

INSERT INTO Seed (seedURI) VALUES ('http://www.thomas.biz/home.asp');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('http://www.thomas.biz/home.asp', 1);
INSERT INTO FailedSeed(seedURI, crawlId, statusCode) VALUES ('http://www.thomas.biz/home.asp', 1, '404');

INSERT INTO Seed (seedURI) VALUES ('https://www.miller.net/category/');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('https://www.miller.net/category/', 1);
INSERT INTO FailedSeed(seedURI, crawlId, statusCode) VALUES ('https://www.miller.net/category/', 1, '500');


INSERT INTO Seed (seedURI) VALUES ('http://sharp-myers.net/tags/explore/');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('http://sharp-myers.net/tags/explore/', 1);
INSERT INTO RdfURI(crawlId, rdfSeedURI, originSeedURI) VALUES (1, 'http://sharp-myers.net/tags/rdf_catalogue/data.ttl', 'http://sharp-myers.net/tags/explore/');

INSERT INTO Seed (seedURI) VALUES ('https://www.mccormick.com/search.htm');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('https://www.mccormick.com/search.htm', 1);

INSERT INTO Seed (seedURI) VALUES ('https://www.davis.com/posts/main/');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('https://www.davis.com/posts/main/', 1);


-- Crawl 2 Data
-- NOTE: Also need to think about updating retried values (Could be handled in python?)

INSERT INTO Crawl (crawlID, endDate) VALUES (2, Null);

INSERT INTO Seed (seedURI) VALUES ('http://miller-morse.info/tag/category/category/search/');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('http://miller-morse.info/tag/category/category/search/', 2);

INSERT INTO Seed (seedURI) VALUES ('https://wise.net/register/');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('https://wise.net/register/', 2);
INSERT INTO FailedSeed(seedURI, crawlId, statusCode) VALUES ('https://wise.net/register/', 2, '404');

INSERT INTO Seed (seedURI) VALUES ('https://www.mendoza.com/');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('https://www.mendoza.com/', 2);
INSERT INTO RdfURI(crawlId, rdfSeedURI, originSeedURI) VALUES (2, 'https://www.mendoza.com/rdflibrary/book_data.rdf', 'https://www.mendoza.com/');

INSERT INTO Seed (seedURI) VALUES ('https://www.griffin.biz/tags/wp-content/blog/login//');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('https://www.griffin.biz/tags/wp-content/blog/login/', 2);
INSERT INTO RdfURI(crawlId, rdfSeedURI, originSeedURI) VALUES (2, 'https://www.griffin.biz/tags/rdf/turtles_are_cool.n3', 'https://www.griffin.biz/tags/wp-content/blog/login/');

INSERT INTO Seed (seedURI) VALUES ('https://jennings.info/terms/');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('https://jennings.info/terms/', 2);

INSERT INTO Seed (seedURI) VALUES ('http://bradley-ramirez.net/posts/main.php');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('http://bradley-ramirez.net/posts/main.php', 2);


-- Crawl 3 Data
INSERT INTO Crawl (crawlID, endDate) VALUES (3, Null);

INSERT INTO Seed (seedURI) VALUES ('http://www.hernandez.com/tag/posts/about.asp');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('http://www.hernandez.com/tag/posts/about.asp', 3);

INSERT INTO Seed (seedURI) VALUES ('https://www.reynolds.com/');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('https://www.reynolds.com/', 3);
INSERT INTO FailedSeed(seedURI, crawlId, statusCode) VALUES ('https://www.reynolds.com/', 3, '404');

INSERT INTO Seed (seedURI) VALUES ('http://www.smith-cox.com/main/wp-content/wp-content/faq.php');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('http://www.smith-cox.com/main/wp-content/wp-content/faq.php', 3);
INSERT INTO RdfURI(crawlId, rdfSeedURI, originSeedURI) VALUES (3, 'http://www.smith-cox.com/main/wp-content/wp-content/faq', ' http://www.smith-cox.com/main/wp-content/wp-content/faq.php');

INSERT INTO Seed (seedURI) VALUES ('http://banks.com/home.htm');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('http://banks.com/home.htm', 3);
INSERT INTO RdfURI(crawlId, rdfSeedURI, originSeedURI) VALUES (3, 'http://banks.com/home', 'http://banks.com/home.htm');

INSERT INTO Seed (seedURI) VALUES ('https://www.poole-blair.org/home.php');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('https://www.poole-blair.org/home.php', 3);

INSERT INTO Seed (seedURI) VALUES ('http://brown-reyes.com/login.jsp');
INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('http://brown-reyes.com/login.jsp', 3);

INSERT INTO CrawlSeeds(seedURI, crawlId) VALUES ('http://www.thomas.biz/home.asp', 3);
INSERT INTO FailedSeed(seedURI, crawlId, statusCode) VALUES ('http://www.thomas.biz/home.asp', 3, '404');
