*** Web Scaper ***
The goal of this component is to extract the data from a website, including PDF files posted on the site. 

This tool crawls a specified website, extracts its content, and saves it in text format.

# Prerequisites
1. This tool is developed using Python 3.x.
2. The following packages as specified in `requirements.txt':
    BeautifulSoup
    requests
    tqdm
    pymongo

### Setup Instructions:
1.  Navigate to the `webscraper` directory:
      `cd webscraper`
2.  Set up a virtual environment:
    `python3 -m venv venv`
3.  Activate the virtual environment:
    `source venv/bin/activate`
4.  Install the required libraries:

    `pip install -r requirements.txt`

5.  **Configuration**: Before running the crawler, modify the `config.py` file with the appropriate main and MongoDB configurations.

### Execution:

-   **Full Website Crawl**: To crawl the entire website with struture fromat, run:
    `python crawler.py`

    This program systematically crawls every page of an entire website, extracting information from each page and saves it into a specific hierarchical structure. It utilizes MongoDB to store and manages the collected information. 

    'read_urls.py' will print all URLs in hierarchical structure from MongoDB.

-   **Full crawler_without_structure**: To crawl the subdomain website without struture, run:
    `python crawler_without_structure.py`

    This program crawls the website, extracting information page by page and save the results in a single text file. All PDF files will be downloaded into a designated folder. 
- 
