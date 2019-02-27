## Summary of Proposed Methods (Burgess et. al, 2018)
This sections outlines the three key methods to discover Australian URIs for harvesting linked data and linked data seeds. *NOTE: These methods are not mutually exclusive and can be used to support one another.*

| Method | Description | Potential Advantages | Potential Disadvantages |
|--------|-------------|----------------------|-------------------------|
| Second Crawler | Using a second web crawler to find RDF seeds on regular HTML web pages for use with LD Spider. | Second crawler can be either built from scratch (relatively easily) or pre-existing tools can be investigated to do the job.| Approach is not targeted and would likely require a list of Top Level Domains within Australia to start on.|
| Google API | Searching the web for RDF seeds using the google custom search API. | Service is already developed and Google already has significant information indexed. It is also possible to search through domains such as '.au' directly and filter for linked data filetypes, making it a far more efficient and targeted approach. | Google APIs have heavy usage restrictions and limitations which may potentially make this method an inviable option. |
| DNS Replication | Set up a DNS server such that it may populate itself with a large list of domains to work with. | There may be alternative uses for such a server (i.e. the primary purpose does not need to be to get domains for this project).| This approach is very complex and would require specialist knowledge to set up (requiring up-skilling). The time frame required is also unpredictable without further research, development and testing. There may also be easier methods to get the same information (e.g. getting a URI list from *ausdomainleger*) |



## Method Evaluation Metrics
We propose the following metrics be used to evaluate the success of the search methods if such an evaluation is necessary.

### Primary Performance Metrics
These metrics relate to the direct performance of a method rather than the higher-level consideration required. These metrics are usually tangible and can be represented quantitatively.

- Number of Seed URIs Gathered.
- Number of Dead Linked Data Links Detected.
- Time Required (as an average per x number of URIs).

### Secondary Performance Metrics
These metrics are generally associated with the wider implications of a method that are not necessarily performance related. These metrics can also be intangible and represented qualitatively as well as tangible and qualitative.

- Financial Cost Analysis
- Memory Usage
- Potential for Increasing Performance (e.g. multithreading)

## Proposed Secondary Crawler Method (Using Python)
This section outlines a potential (high-level) approach for a secondary crawler implemented in Python. Using a list of known domains (possibly top-level), iterate through each URI and test each for linked data formats. A more detailed explaination is provided by the pseudocode below.

A large benefit of such a setup is that it can lend itself to the possibility of multi-threading using the python 'threading' module.

```
For URI in URI List:
	Send HTTP request to URI for linked data.
    Check the response format.
    If there is linked data:
    	Store URI in memory (or flush to disk).
    Else if there is no linked data returned:
    	Compile a list of URIs found within the document.
        Filter URIs accordingly (e.g. remove URIs to different domains).
        Iterate through the new list of URIs and repeat the entire process (recursion).
		If there are no new links:
        	Move to the next URI in the parent list
```

### Considerations
In order to use such a method, we would still require a list of top-level domains in Australia rather than finding them on their own. It is also essential to formally define what the definition of 'Australian Internet' constitutes such that URI filtering parameters accurately reflect this.

Care must also be taken for resources used. For example, the capacity of multithreading using python and our machines should be investigated on different scales to ensure that hardware resources are adequate. It is important to consider that machines must have enough memory and computing power to handle and schedule a high number of request threads. This requires investigation.

Recursion depth must also be considered if implementing the above pseudocode as a recursive-style function or set of functions. If necessary, maximum recursion thresholds can be adjusted in python, however it is essential to take care that recursion does not get out of control. The filtering of URIs collected from a web page may help with this. Alternatively, the funciton could also be implemented in a non-recursive way, although this may not necessarily bring the function under control.