#Database Documentation

##Database Requirements
The database needs to be able to complete the following tasks.

1. Store the results of a crawling session, including URIs that point to RDF data, seeds with failed responses that require retrying, and seeds with no RDF data attached.
2. Be able to update seed records if they exist when the seed is reattempted.
3. Be able to have seeds that need to be retried added to RDF URI and removed from the list of seeds that need to be retried.
4. Store information about crawling sessions (such as number of seeds considered, a count of failed seeds and time periods, etc.) as well as the time when RDF seeds were discovered or last tested.
5. Store information of the seed at which an RDF URI was discovered through.


##Database Schema
The relational database includes 5 tables which are outlined as follows. It is assumed that an attribute does not allow null values unless specifically stated.

| Table Name | Attributes | Constraints |
|--------|--------|--------|
|**Seed**|*++seedURI++* VARCHAR(2083)<br>*invalidationDate* INTEGER|NULL&nbsp;&nbsp;Allowed for *invalidationDate*|
|**Crawl**|*++crawlId++* INTEGER<br>*startDate* INTEGER<br>*endDate* INTEGER|NULL&nbsp;&nbsp;Allowed for *endDate*|
|**CrawlSeeds**|*++seedURI++* VARCHAR(2083)<br>*++crawlId++* INTEGER|FK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;crawlId references **Crawl** *crawlId*<br> FK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*seedURI* references **Seed** *seedURI*|
|**FailedSeed**|*++seedURI++* VARCHAR(2083)<br>*++crawlId++* INTEGER<br>*requestDate* INTEGER<br>*statusCode* VARCHAR(3)|FK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;crawlId references **Crawl** *crawlId*<br>FK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*seedURI* references **Seed** *seedURI*|
|**RdfURI**|*++rdfSeedURI++* VARCHAR(2083)<br>*crawlId* INTEGER<br>*originSeedURI* VARCHAR(2083)<br>*dateDiscovered* INTEGER |FK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;crawlId references **Crawl** *crawlId*<br> FK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*originSeedURI* references **Seed** *seedURI*<br>NULL&nbsp;&nbsp;Allowed for *originSeedURI*<br>UNQ&nbsp;&nbsp;&nbsp;&nbsp;*rdfSeedURI*|



##Database Queries
The following queries are required of the database and are presented below.

1. Retrieve a list of URIs that have previously failed and need to be attempted again.
2. Retrieve a list of URIs known to point to RDF data.
3. Retrieve a list of URIs known to point to RDF data that were discovered within a specific time period.
4. Retrieve a list of URIs that were tested during a specific crawl.
5. Retrieve a list of URIs that point to RDF information from a specific domain.
6. Retrieve a list of URIs and the number of discovered RDF URIs.