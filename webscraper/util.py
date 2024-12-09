import time
import random
import string
from urllib.parse import urlparse
import re
def generate_unique_filename():
    timestamp = str(time.time()).replace('.', '')  # Get timestamp and remove the decimal point
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))  # Generate a random string
    unique_filename = timestamp + '_' + random_string
    return unique_filename
def calculate_time(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return hours, minutes, seconds
def print_time(total_seconds):
    hours, remaining_seconds = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remaining_seconds, 60)

    print(f"Time: {hours} hours, {minutes} minutes, {seconds} seconds")

def remove_hash_from_url(url):
    hash_index = url.find('#')
    if hash_index != -1:
        return url[:hash_index]
    return url

def compare_urls(url_list, target_url):
    target_url = re.sub(r'^https?://', '', target_url)
    target_url = re.sub(r'/$', '', target_url)

    for url in url_list:

        current_url = re.sub(r'^https?://', '', url)
        current_url = re.sub(r'/$', '', current_url)

        if current_url == target_url:
            return True

    return False