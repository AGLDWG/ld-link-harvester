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

-- Find a list of URIs Pointing to Linked Data
SELECT rdfSeedURI FROM RdfURI;

