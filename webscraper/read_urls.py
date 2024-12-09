import json
from urllib.parse import urlparse
from pymongo import MongoClient
from config import *
import time
from util import *
def create_tree_structure(urls):
    tree = {}
    start_time = time.time()
    for url in urls:
        parsed_url = urlparse(url)
        path_components = parsed_url.path.strip('/').split('/')
        current_node = tree

        for component in path_components:
            if component not in current_node:
                current_node[component] = {"url":url}
            current_node = current_node[component]

    return tree

start_time=time.time()
client = MongoClient(MONGO_HOST, MONGO_PORT)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]
info_collection =db['info']
query = {}  # Specify your query criteria

pipeline = [{
        '$match': {
            'parent': {'$ne': ''},
            'child': {'$ne': ''}
        }
    },
    {
        '$group': {
            '_id': '$parent',
            'Parent': {'$first': '$parent'},
            'Children': {'$addToSet': '$child'}
        }
    }
]

# Execute the pipeline
result = list(collection.aggregate(pipeline))

# Print the result
print(result)

##print(json_output)