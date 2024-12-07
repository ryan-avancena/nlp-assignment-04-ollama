import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
import time
import os
from util import generate_unique_filename,compare_urls
from downloader import download_files
import urllib.parse
from pymongo import MongoClient
from config import *
import time
from datetime import timedelta

class ExportToJson:
    def __init__(self):
        self.client = MongoClient(MONGO_HOST, MONGO_PORT)
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION]
        self.info_collection = self.db['info']
        self.output_data = []
        self.others_webpages = []
        try:
            # Use the ping() method to check the connection
            self.client.admin.command('ping')
            print("MongoDB connected successfully!")
        except Exception as e:
            print("Failed to connect to MongoDB:", str(e))

    def findIdentifier(self,element):
        url=element.get("_id")

        for item in self.input_data:
            if "identifier" in item:
                identifier = item["identifier"]
                if self.check_identifier(url, identifier):
                    webpages = []
                    if "child" in item:
                        webpages = self.process_child(url + identifier + "/", item["child"])
                    item["webpages"] = webpages
                    self.output_data.append(url)
            else:
                self.others_webpages.append(item)
    def export(self):
        with open('structure/input.json',"r") as file:
            self.input_data = json.load(file)
        query = {}  # Specify your query criteria
        result = self.collection.find(query)

        # Read data into an ArrayList
        data_list = []
        for document in result:
            data_list.append(document)

        # Print the ArrayList

        for index, element in enumerate(data_list):
            url=element.get("_id")
            print(url);
            self.findIdentifier(element)
        output = {
            "department": self.output_data,
            "others": {
                "webpages": self.others_webpages
            }
        }
        print(output)

        # Write to output.json
        with open("output/output.json", "w") as file:
            json.dump(output, file, indent=4)

    def check_identifier(self,url, identifier):
        return identifier in url.lower()

    # Function to recursively process the child nodes
    def process_child(self,url, child):
        webpages = []
        for item in child:
            if "identifier" in item:
                identifier = item["identifier"]
                if self.check_identifier(url, identifier):
                    if "child" in item:
                        child_webpages = process_child(url + identifier + "/", item["child"])
                        item["webpages"] = child_webpages
                    webpages.append(item)
            else:
                webpages.append(item)
        return webpages







def fun():
    crawler = ExportToJson()
    return crawler.export()
fun()
