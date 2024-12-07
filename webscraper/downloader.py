import os
import requests
import time
from tqdm import tqdm

def download_file(url, file_path):
    response = requests.head(url)
    if response.status_code == 200 and 'content-length' in response.headers:
        content_length = int(response.headers['content-length'])
        if content_length > 0:
            response = requests.get(url, stream=True)
            file_size = 0
            block_size = 8192  # 8 KB
            progress_bar = tqdm(total=content_length, unit='B', unit_scale=True)
            start_time = time.time()

            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        file.write(chunk)
                        file_size += len(chunk)
                        progress_bar.update(len(chunk))

            progress_bar.close()
            elapsed_time = time.time() - start_time
            print(f"Download complete: {file_path}")
            print(f"Time elapsed: {elapsed_time:.2f} seconds")
        else:
            print(f"Skipped download: {url} (Empty file)")
    else:
        print(f"Skipped download: {url} (Unreachable or unsupported file)")


def download_files(download_urls):
    for download_url in download_urls:
        url = download_url['href']
        file_id = download_url['id']
        file_name = file_id
        file_path = os.path.join('downloads', file_name)
        download_file(url, file_path)