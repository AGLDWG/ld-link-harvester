--QUERIES RELATED TO VALIDITY OF SEEDS
-- Retrieve a list of URIs that need to be reattempted.
SELECT seedURI, COUNT(seedURI)
FROM FailedSeed
GROUP BY seedURI
HAVING COUNT(seedURI) < 2; -- THRESHOLD GOES HERE

-- Retrieve a list of URIs that need to be Invalidated.
SELECT seedURI, COUNT(seedURI)
FROM FailedSeed
GROUP BY seedURI
HAVING COUNT(seedURI) >= 2; -- THRESHOLD GOES HERE

-- Invalidate seeds above a threshold
UPDATE Seed
SET invalidationDate=strftime('%s','now')
WHERE seedURI in (
    SELECT seedURI
    FROM FailedSeed
    GROUP BY seedURI
    HAVING COUNT(seedURI) >= 2);

-- Retrieve seeds that have been invalidated
SELECT *
FROM SEED
WHERE invalidationDate IS NOT NULL;

-- Retrieve a list of seeds that are still valid
SELECT *
FROM SEED
WHERE invalidationDate IS NULL;


-- QUERIES RELATED TO THE RDF LINKS
-- Find a list of URIs Pointing to Linked Data
SELECT rdfSeedURI FROM RdfURI;

-- List the formats (and counts) that the Linked data was found in
SELECT contentFormat, COUNT(contentFormat)
FROM RdfURI
GROUP BY contentFormat;

-- List the formats (and counts) that the Linked data was found in during a specific crawl.
SELECT contentFormat, COUNT(contentFormat)
FROM RdfURI
WHERE crawlId=1 -- CrawlId goes here
GROUP BY contentFormat;

-- List the number of URIs found per each seed
SELECT originSeedURI, COUNT(DISTINCT rdfSeedURI)
FROM RdfURI
GROUP BY originSeedURI;


--QUERIES RELATING TO  CRAWLS
--List the number of URLs Tested Per Crawl
SELECT crawlId, COUNT(address)
FROM Link
GROUP BY crawlId;

--
SELECT
    Link.crawlId AS Crawl,
    Failed.failCount + Successful.successCount AS 'Total Requests',
    Failed.failCount AS 'Failed Requests',
    Successful.successCount AS 'Successful Requests',
    LinkedData.ldSeeds AS 'Linked Data Seeds'
FROM
    Link,
    (SELECT crawlId, count(crawlId) as failCount
        FROM Link
        WHERE failed=1
        GROUP BY crawlId) AS Failed,
    (SELECT crawlId, count(crawlId) as successCount
        FROM Link
        WHERE failed=0
        GROUP BY crawlId) AS Successful,
    (SELECT crawlId, COUNT(rdfSeedURI) as ldSeeds
        FROM RdfURI
        GROUP BY crawlId) AS LinkedData
WHERE
    Link.crawlId = Failed.crawlId AND
    Link.crawlId = Successful.crawlId AND
    Link.crawlId = LinkedData.crawlId
GROUP BY Link.crawlId;

--Get the count of each format encountered during a crawl (can filter for specific crawl if necessary)
SELECT crawlId, contentFormat, COUNT(contentFormat)
FROM Link
GROUP BY crawlId, contentFormat;