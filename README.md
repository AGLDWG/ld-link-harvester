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
In order to run the web link harvester, the key script to invoke is harvest.py script of the harvester module. This script essentially utilizes the harvester module and creates a multiprocessing web crawler. Note that the bare minimum requirement for running the script is a text file containing a set of urls (separated by newlines). The script can be configured to accept said text file by altering the global variable 'URL_SOURCE' at the top of the script (more details are in the [following section](#configuration-variables)).
```
$ python3 harvest.py
```

### Charting Data
The charts module is used to generate charts based on the database information available. The configuration of this script/module is simple. Configure the global variables at the beginning of the '/charts/\_\_init\_\_.py' to properly configure the script (i.e. provide the correct path to the database file, configure the desired output directory, etc.).

Once the script is properly configured, invoke \_\_init\_\_.py as a script to generate charts (note that to display charts, an appropriate window server, must be running).

```
$ python3 charts/__init__.py
```

### Retrieving Statistics
The stats module is a simple module that is used to scan the database and obtain various analytics from the database. In order to use, configure the global variables at the beginning of '/stats/\_\_init\_\_.py' (as done with the charts module) and invoke it as follows.

```
$ python3 stats/__init__.py
```


## Configuration Variables
Basic configuration options can be provided by modifying the global variables located at the top of the script. These variables (case-sensitive) are set globally in the Harvester module, however a user-created script (such as harvest.py) can override the default values of these as necessary. Descriptions of each variable are as follows.

| Variable | Function/Description |
|--------|--------|
| URL_SOURCE (*str*)| A path to a text file containing a list of URIs to run the crawler over.|
| AUTO_PROCESS_OVERFLOW (*bool*) | A toggleable variable controlling whether or not queue overflow is automatically handled by the program. |
| DATABASE_FILE (*str*) | A path to an sqlite3 database file that the program will output to (note, if this does not exist one will be created). |
| DATABASE_TEMPLATE (*str*) | A path to an sql script that is used to create the database. If the database already exists, then this script is used to verify the existing database integrity and structure (unless this setting is turned off). |
| SCHEMA_INTEGRITY_CHECK (*bool*) | A toggle controlling whether or not the schema of the database is verified against the original creation script (True for verification, False for no verification). |
| WORK_QUEUE_OVERFLOW_FILE (*str*) | A path to a file that will be created where work queue overflow is stored if the queue becomes full. |
| CRAWL_RECORD_REPAIR (*bool*) | A toggle controlling whether or not crawls in the database that lack an endDate will be automatically assigned one based on the time that the last link of that crawl was requested. This is useful if a particular run was ended via user intervention or some form of error that prevented the program from shutting down properly (True for record repairing, False for no record repairing). |
| RESPONSE_TIMEOUT (*int*) | Specifies the number of seconds that a response can wait for until timeout. |
| MAX_REDIRECTS (*int*) | The maximum number of redirects allowed before the program terminates an attempt to visit a link. |
| KILL_PROCESS_TIMEOUT (*int*) | Specifies the number of seconds that the monitoring process will wait for more output from the request workers. If there is no activity from any of the workers (i.e. they are all inactive or frozen) for this period of time, all request workers are terminated and restarted if there is any more jobs in the work queue or in the overflow file. |
| RECURSION_DEPTH_LIMIT (*int*) | Specifies the maximum level of recursive depth into a domain that the crawler will visit (note that increasing the recursion depth limit causes a sharp exponential increase in the number of links to visit in most domains). |
| PROC_COUNT(*int*) | Specifies the number of request worker processes that will be created. Note that the memory required of the whole program will be multiplied n-fold where n is the number of processes active. The user should also take into account that the monitoring (main) process exists in addition to the worker processes. Thus the total number of process active will be PROC_COUNT + 1. |
| COMMIT_FREQ (*int*) | Specifies the number of iterations of the monitoring process that must be completed before the changes to the database are commited. |
| WORK_QUEUE_MAX_SIZE (*int*) | Specifies the number of jobs allowed in the work queue. If this number is exceeded, jobs will be added to the overflow file. |
| RESP_QUEUE_MAX_SIZE (*int*) | Specifies the maximum number of responses needing processing that the response queue can store. This is not usually an issue because the responses from the workers usually work a lot slower, hence this point in the software is not usually rate limiting. As a result, *overflow handling here is not yet implemented*. |
| RDF_MEDIA_TYPES (*list*) | A list (of *str*) that specifies the possible rdf media types (i.e. content-types in HTTP responses) that are flagged as Linked Data. **Note:** *Do NOT put 'text/html' in this list as links will not be parsed if this is considered and rdf media type.* |
| RDF_FORMATS (*list*) | A list (of *str*) that specifies the file formats of a uri that (e.g. <span>https:/</span>/example.com/linkeddata.rdf) indicate Linked Data. |
| GLOBAL_HEADER (*dict*) | A python dictionary object that contains the parameters to be sent in the default HTTP header used at runtime. Parameters/fields should be passed as keys and the parameter values as dictionary values. |
| BLACKLIST_FORMATS (*list*) | A list (of *str*) that specifies a range of file types that the crawler should avoid (e.g. images, videos, pdf, etc.). |

> NOTE: When invoking the script from the command line directly, there an optional command line argument can be passed in order to override whatever the value in the URL_SOURCE variable with that of the command line argument. This is particularly useful when running batch runs from a script.
> For example, the command below would override the URL_SOURCE variable specified in the script with 'some_urls.txt'.
> ```
> $ python3 harvest.py some_urls.txt
> ```

## License
This code is licensed using the GPL v3 licence. See the [LICENSE file](LICENSE) for the deed.


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


