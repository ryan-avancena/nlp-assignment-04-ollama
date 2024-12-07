# main.py

import os
from crawler import crawl_website
from downloader import download_files
from config import *
import sys

#set recersion limit
sys.setrecursionlimit(NEW_LIMIT)
# Crawl website
urls = crawl_website(main_url)

# Create downloads directory if it doesn't exist
os.makedirs('downloads', exist_ok=True)

# Download files
download_files(urls)
