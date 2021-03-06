# Linked Data link harvester
This is a student project based at CSIRO.

## Getting Started

### Installing
The scripts can be downloaded directly from the git repository via the following command.
```
$ git clone https://github.com/AGLDWG/ld-link-harvester
$ cd ld-link-harvester
```

### Running the Web Link Harvester
In order to run the web link harvester, the key script to invoke is `harvest.py`. This script essentially utilizes the harvester module and creates a multiprocessing web crawler. Note that the bare minimum requirement for running the script is a text file containing a set of urls (separated by newlines). The script can be configured to accept said text file by altering the global variable `URL_SOURCE` at the top of the script (more details are in the [following section](#configuration-variables)).
```
$ python3 harvest.py
```

### Charting Data
The charts module is used to generate charts based on the database information available. A script to use this module is provided (/chart.py). Configure the global variables at the beginning of the `chart.py` to properly configure the script (i.e. provide the correct path to the database file, configure the desired output directory, etc.).

Once the script is properly configured (using the global variables), invoke `chart.py` as a script to generate charts (note that to display charts, an appropriate window server must be running for matplotlib to hook).

```
$ python3 charts.py
```

### Retrieving Statistics
A simple script is provided to generate spreadsheet summaries of the database. It is used to scan the database and obtain various analytics from the database. In order to use, configure the global variables at the beginning of '/stats.py' (as done with the charts module) and invoke it as follows.

Note that if the `INSERT_FIGURES` global variable is set to 'True' the appropriate figures should be generated using chart.py first. 

```
$ python3 stats.py
```


## Configuration Variables
Basic configuration options can be provided by modifying the global variables located at the top of the script. These variables (case-sensitive) are set globally in the Harvester module, however a user-created script (such as harvest.py) can override the default values of these as necessary. Descriptions of each variable are as follows.

| Variable | Function/Description |
|--------|--------|
| `URL_SOURCE` (*str*)| A path to a text file containing a list of URIs to run the crawler over.|
| `AUTO_PROCESS_OVERFLOW` (*bool*) | A toggleable variable controlling whether or not queue overflow is automatically handled by the program. |
| `DATABASE_FILE` (*str*) | A path to an sqlite3 database file that the program will output to (note, if this does not exist one will be created). |
| `DATABASE_TEMPLATE` (*str*) | A path to an sql script that is used to create the database. If the database already exists, then this script is used to verify the existing database integrity and structure (unless this setting is turned off). |
| `SCHEMA_INTEGRITY_CHECK` (*bool*) | A toggle controlling whether or not the schema of the database is verified against the original creation script (True for verification, False for no verification). |
| `WORK_QUEUE_OVERFLOW_FILE` (*str*) | A path to a file that will be created where work queue overflow is stored if the queue becomes full. |
| `CRAWL_RECORD_REPAIR` (*bool*) | A toggle controlling whether or not crawls in the database that lack an endDate will be automatically assigned one based on the time that the last link of that crawl was requested. This is useful if a particular run was ended via user intervention or some form of error that prevented the program from shutting down properly (True for record repairing, False for no record repairing). |
| `RESPONSE_TIMEOUT` (*int*) | Specifies the number of seconds that a response can wait for until timeout. |
| `MAX_REDIRECTS` (*int*) | The maximum number of redirects allowed before the program terminates an attempt to visit a link. |
| `KILL_PROCESS_TIMEOUT` (*int*) | Specifies the number of seconds that the monitoring process will wait for more output from the request workers. If there is no activity from any of the workers (i.e. they are all inactive or frozen) for this period of time, all request workers are terminated and restarted if there is any more jobs in the work queue or in the overflow file. |
| `RECURSION_DEPTH_LIMIT` (*int*) | Specifies the maximum level of recursive depth into a domain that the crawler will visit (note that increasing the recursion depth limit causes a sharp exponential increase in the number of links to visit in most domains). |
| `PROC_COUNT`(*int*) | Specifies the number of request worker processes that will be created. Note that the memory required of the whole program will be multiplied n-fold where n is the number of processes active. The user should also take into account that the monitoring (main) process exists in addition to the worker processes. Thus the total number of process active will be PROC_COUNT + 1. |
| `COMMIT_FREQ` (*int*) | Specifies the number of iterations of the monitoring process that must be completed before the changes to the database are commited. |
| `WORK_QUEUE_MAX_SIZE` (*int*) | Specifies the number of jobs allowed in the work queue. If this number is exceeded, jobs will be added to the overflow file. |
| `RESP_QUEUE_MAX_SIZE` (*int*) | Specifies the maximum number of responses needing processing that the response queue can store. This is not usually an issue because the responses from the workers usually work a lot slower, hence this point in the software is not usually rate limiting. As a result, *overflow handling here is not yet implemented*. |
| `RDF_MEDIA_TYPES` (*list*) | A list (of *str*) that specifies the possible rdf media types (i.e. content-types in HTTP responses) that are flagged as Linked Data. **Note:** *Do NOT put 'text/html' in this list as links will not be parsed if this is considered and rdf media type.* |
| `RDF_FORMATS` (*list*) | A list (of *str*) that specifies the file formats of a uri that (e.g. <span>https:/</span>/example.com/linkeddata.rdf) indicate Linked Data. |
| `GLOBAL_HEADER` (*dict*) | A python dictionary object that contains the parameters to be sent in the default HTTP header used at runtime. Parameters/fields should be passed as keys and the parameter values as dictionary values. |
| `BLACKLIST_FORMATS` (*list*) | A list (of *str*) that specifies a range of file types that the crawler should avoid (e.g. images, videos, pdf, etc.). |

> NOTE: When invoking the script from the command line directly, there an optional command line argument can be passed in order to override whatever the value in the URL_SOURCE variable with that of the command line argument. This is particularly useful when running batch runs from a script.
> For example, the command below would override the URL_SOURCE variable specified in the script with 'some_urls.txt'.
> ```
> $ python3 harvest.py some_urls.txt
> ```

## Unit Testing
A unit testing suite is included in `harvester/tests`. This suite contains 5 scripts that collectively run 19 unit tests to ensure basic functionality of the crawler. Note that this does not test for complex bugs that may occur in revisions. There is also a test website included to support these unit tests. In order to get the tests to work, this website MUST be running on a simple HTTP server at the loopback address of the localhost, at port 8080 (i.e. site must be available at http://127.0.0.1:8080 on the local machine). If this requirement is not met, tests will fail.

The unit tests provided (19 in total) per each of the 5 scripts are outlined as follows.

| Functional Area | Script | Unit Tests |
|-----------------|--------|------------|
| Database Verification | test_database_verification.py | <ul><li>Appropriate verification of  normal schema</li><li>Appropriate rejection of damaged schema</li></ul> |
| Link Parsing | test_link_parser.py | <ul><li>Appropriate conversion of relative to absolute links</li><li>Appropriate detection of external links.</li><li>Appropriate filtering of blacklisted file types</li><li>Appropriate removal of anchor links</li></ul> |
| Response Handling | test_response_handler.py | <ul><li>Appropriate handling of valid response.</li><li>Appropriate handling of erroneous response.</li><li> Appropriate handling of missing file formats in response.</li><li>Appropriate handling of rdf detection in URL file name.</li><li>Appropriate handling of rdf detection based on response content type.</li><li>Appropriate handling of invalid formats.</li><li>Appropriate handling of redirection and seed modification.</li></ul> |
| Worker Function (Single) | test_worker.py | <ul><li>Appropriate behaviour of worker function.</li><li>Appropriate compilation of visited list (dictionary).</li><li>Not adding duplicate entries to visited list.</li></ul> |
| Parallel Processing | test_workers_parallel.py | *When parallel processing…*<br><ul><li>Appropriate behaviour of   worker function.</li><li>Appropriate compilation of visited list (dictionary).</li><li>Not adding duplicate entries to visited list.</li></ul> |

All unit tests were designed and tested using the **PyTest** module.


## License
This code is licensed using the Apache 2.0 licence. See the [LICENSE file](LICENSE) for the deed.


## Contacts
Developer:  
**Jake Hashim-Jones**  
*Computer Science Student*  
Griffith University  
<jake.hashim-jones@griffithuni.edu.au>  

Product Owner:  
**Nicholas Car**  
*Senior Experimental Scientist*  
CSIRO Land & Water, Environmental Informatics Group  
<nicholas.car@csiro.au>  


