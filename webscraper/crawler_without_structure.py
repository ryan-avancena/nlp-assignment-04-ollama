
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
import os
from util import *

from downloader import download_files
import urllib.parse
from pymongo import MongoClient
from config import *
import time
import traceback

def extract_a_tags(element, base_url):
    urls = []

    if element is not None:
        if hasattr(element, 'name') and element.name == 'a' and 'href' in element.attrs:
            href = element['href']
            absolute_url = urljoin(base_url, href)
            urls.append(absolute_url)

        if hasattr(element, 'contents'):
            for child in element.contents:
                urls.extend(extract_a_tags(child, base_url))

    return urls

class WebsiteCrawler:
    def __init__(self, start_url):
        self.start_url = start_url
        self.visited = set()
        self.urls = set()
        self.download_urls = []

    def normalize_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url._replace(scheme='').geturl()

    def extract_info_web_page(self, url, soup):
        name = ""
        unit = ""
        if (compare_urls(self.urls, url)):
            return

        self.urls.add(url)

        response = requests.get(url, allow_redirects=True)

        content = BeautifulSoup(response.text, 'html.parser').getText()

        # Data cleaning: removing multiple spaces and separating content by paragraph.
        cleaned_content = '\n'.join(paragraph.strip() for paragraph in content.split('\n\n\n\n') if paragraph.strip())
        print("extracted:" + url)

        with open("output/content.txt", 'a', encoding='utf-8') as txt_file:
                txt_file.write(url+cleaned_content+"\n")

    def normalize(self, url):
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

    def compare_last_domain(self, url1, url2):

        return self.normalize(url1) == self.normalize(url2)

    def crawl_urls(self, url, domain):

        normalized_url = self.normalize_url(url)

        if normalized_url in self.visited:
            return

        self.visited.add(normalized_url)
       
        response = requests.get(url, allow_redirects=False)
        if response.status_code != 200:
            return
        content_type = response.headers.get('content-type')
        if 'text/html' not in content_type:
            value = {
                "href": url,
                "id": f"{str(time.time())}.pdf",  # Dynamic ID with extension
                "text": "downloadable url"
            }
            self.download_urls.append(value)
            return True

        soup = BeautifulSoup(response.text, 'html.parser')
        extractedAnchors = extract_a_tags(soup.find("html"), main_url)

        # Extract URLs from anchor tags
        try:
            for anchor in extractedAnchors:
                href = anchor

                if href and not href.startswith("mailto:") and not href.startswith(
                        '#') and not "javascript:ShowMainNavMobile()" in href:

                    if not href.startswith(('http://', 'https://')):
                        absolute_url = urllib.parse.urljoin(url, href)

                    else:
                        absolute_url = href

                    parsed_url = urlparse(absolute_url)
                    path = parsed_url.path
                    val = parsed_url.netloc
                    absolute_url=remove_hash_from_url(absolute_url)

                    if "ecs/cs" in absolute_url:
                        if (self.compare_last_domain(main_url, absolute_url)):
                            if ('.' not in path or path.endswith('.php') or path.endswith('.html')) or path.endswith(
                                    '.aspx') and (
                                    self.normalize_url(absolute_url) not in self.visited):

                                self.crawl_urls(absolute_url, domain)

                                try:

                                    self.extract_info_web_page(absolute_url, soup)
                                except Exception as e:
                                    traceback_info = traceback.format_exc()
                                    print(traceback_info)
                                    print(e)

                            elif path.endswith('.pdf') or path.endswith(".png") or path.endswith(".jpg"):
                                value = {
                                    "href": absolute_url,
                                    "id": f"{str(time.time())}.pdf"
                                ,  # Dynamic ID with extension
                                    "text": "from top url"
                                }

                                self.download_urls.append(value)
        except Exception as e:
            print(e)

    def crawl_website(self):
        domain = urlparse(self.start_url).netloc

        try:
            start_time = time.time()
            self.crawl_urls(self.start_url, domain)
            end_time = time.time()

            # Save time information to MongoDB
            time_info = {
                "_id": "info",
                "main_url": main_url
            }
            ## print("downloadble url:" + str(self.download_urls))
            download_files(self.download_urls)

            ##download_files(self.download_urls)

            return self.urls

        except Exception as e:
            print("An error occurred:", str(e))

def crawl_website(main_url):
    start_time = time.time()
    crawler = WebsiteCrawler(main_url)

    return crawler.crawl_website()

crawl_website(main_url)