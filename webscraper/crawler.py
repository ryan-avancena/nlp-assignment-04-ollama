# crawler.py

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
        self.client = MongoClient(MONGO_HOST, MONGO_PORT)
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION]
        self.info_collection = self.db['info']
        try:
            # Use the ping() method to check the connection
            self.client.admin.command('ping')
            print("MongoDB connected successfully!")
        except Exception as e:
            print("Failed to connect to MongoDB:", str(e))

    def normalize_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url._replace(scheme='').geturl()

    def extract_info_web_page(self, url, soup):
        name = ""
        unit = ""
        if (compare_urls(self.urls, url)):
            return

        self.urls.add(url)

        sitename_element = soup.find('p', id='unit')

        if sitename_element is not None:
            a_tag_unit = sitename_element.find('a')
            unit = a_tag_unit.string

        sitename_element = soup.find('p', id='sitename')
        if sitename_element is not None:
            a_tag = sitename_element.find('a')

            name = a_tag.string

        # Extract the necessary information and store it in a structured format

        val = {"parent": unit if unit else name,
               "child": name if unit else ""}


        print(val)


        data = []
        current_object = None

        for element in soup.find_all():
            if element.name == "h1" or element.name == "h2":
                if current_object:
                    data.append(current_object)
                current_object = {
                    "head": [element.text],
                    "Text": [],
                    "url": url,
                    "Link": []
                }
            elif element.name in ["p", "ul", "li","h3","h4","h6","i","u","s"]:
                if current_object:
                    current_object["Text"].append(element.text)
            elif element.name == "a" or "img":
                if current_object:
                    href = element.get('href', '')
                    if not href.startswith(('http://', 'https://')):
                        if not url.endswith('/'):
                            href = urllib.parse.urljoin(url, href)
                            href = href.replace("/resources/_resources/", "/_resources/")

                        # Add a trailing slash to the base URL if it doesn't already have one
                        parsed_url = urlparse(href)
                        path = parsed_url.path
                        file_extension = path.split('.')[-1]
                        # Task 1: Store href in a unique structure named 'download_links' which has URL and ID,
                        # and create a dynamic ID with the extension appended.

                        value = {
                            "href": href,
                            "id": generate_unique_filename() + "." + file_extension,  # Dynamic ID with extension
                            "text": url

                        }
                        if href.endswith(".pdf") or href.endswith(".img") or href.endswith("png"):
                            self.download_urls.append(value)

                        current_object["Link"].append(value)
        if current_object:
            data.append(current_object)

        # Save the extracted data as JSON
        value = {
            "_id": url,
            "url": url,
            "parent": unit if unit else name,
            "child": name if unit else "",
            "data": data
        }
        result = self.collection.replace_one({"_id": url}, value, upsert=True)

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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36"
        }
        response = requests.get(url, allow_redirects=False, headers=headers)
        if response.status_code != 200:
            return
        content_type = response.headers.get('content-type')
        if 'text/html' not in content_type:
            value = {
                "href": url,
                "id": f"{str(time.time())}",  # Dynamic ID with extension
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


                    if True:
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
                                    "id": f"{str(time.time())}",  # Dynamic ID with extension
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

            diff = time.time() - start_time
            print_time(diff)

            # Save time information to MongoDB
            time_info = {
                "_id": "info",
                "main_url": main_url,
                "date": time.time,
                "time_taken": diff

            }
            self.info_collection.replace_one({"_id": "info"}, time_info, upsert=True)

            print("downloadble url:" + str(self.download_urls))
            self.db['urls'].insert_many(self.download_urls)
            ##download_files(self.download_urls)

            return self.urls

        except Exception as e:
            print("An error occurred:", str(e))


def crawl_website(main_url):
    start_time = time.time()
    crawler = WebsiteCrawler(main_url)

    return crawler.crawl_website()

crawl_website(main_url)
