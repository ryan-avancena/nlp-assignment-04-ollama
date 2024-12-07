import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
import time
import sys
import os
from util import *
from downloader import download_files
import urllib.parse
from pymongo import MongoClient
from config import *
import time
from datetime import timedelta


def normalize(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme == '':
        url = 'http://' + url
        parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.lower().split('.')
    if len(domain_parts) > 1:
        last_domain = domain_parts[-2] + '.' + domain_parts[-1]
    else:
        last_domain = ''
    return last_domain

current_limit = sys.getrecursionlimit()
print("Current recursion limit:", current_limit)

# Set a new recursion limit
new_limit = 500000
sys.setrecursionlimit(new_limit)

# Verify the updated recursion limit
updated_limit = sys.getrecursionlimit()
print("Updated recursion limit:", updated_limit)
def compare_last_domain( url1, url2):
    print(normalize(url1))
    print(normalize(url2))
    return normalize(url1) == normalize(url2)

print(compare_last_domain("https://www.chapman.edu/","library.fullerton.edu/about/profiles"))