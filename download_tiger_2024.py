import os
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from tqdm import tqdm
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://www2.census.gov/geo/tiger/TIGER2024/"
DEST_DIR = "<YOUR_DESTINATION_PATH>"  # Replace with the path where you want to store files

os.makedirs(DEST_DIR, exist_ok=True)

EXCLUDE_FILES = {"?C=N;O=D", "?C=M;O=A", "?C=S;O=A", "?C=D;O=A"}

VISITED_URLS = set()
MAX_RETRIES = 3
TIMEOUT = 10

def get_links(url):
    """
    Fetch and parse links from a directory page.
    Retries up to MAX_RETRIES times if the request fails.
    Returns a list of valid links to files or subdirectories.
    """
    retries = 0
    while retries < MAX_RETRIES:
        try:
            logging.info(f"Fetching links from {url} (Attempt {retries + 1}/{MAX_RETRIES})")
            response = requests.get(url, timeout=TIMEOUT)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = [unquote(a['href']) for a in soup.find_all('a', href=True) if a['href'] not in ('../', './')]
                filtered_links = [link for link in links if link not in EXCLUDE_FILES and BASE_URL in urljoin(url, link)]
                logging.info(f"Found {len(filtered_links)} valid links in {url}")
                return filtered_links
            else:
                logging.error(f"Failed to access {url}, status code {response.status_code}")
        except (requests.RequestException, requests.Timeout) as e:
            logging.error(f"Error fetching links from {url}: {e}")
        
        retries += 1
        time.sleep(5)
    
    logging.error(f"Max retries reached. Skipping link fetch for: {url}")
    return []

def download_file(url, dest_path):
    """
    Downloads a file to the specified destination.
    Skips downloading if the file already exists and is non-empty.
    Retries up to MAX_RETRIES times if the request fails.
    """
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        logging.info(f"File already exists and is non-empty: {dest_path}")
        return
    
    retries = 0
    while retries < MAX_RETRIES:
        try:
            logging.info(f"Downloading: {url} (Attempt {retries + 1}/{MAX_RETRIES})")
            response = requests.get(url, stream=True, timeout=TIMEOUT)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                total_size = int(response.headers.get('content-length', 0))
                with open(dest_path, 'wb') as f, tqdm(
                    desc=os.path.basename(dest_path),
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024
                ) as bar:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                        bar.update(len(chunk))
                logging.info(f"Downloaded: {dest_path}")
                return
            else:
                logging.error(f"Failed to download {url}, status code {response.status_code}")
        except (requests.RequestException, requests.Timeout) as e:
            logging.error(f"Error downloading {url}: {e}")
        
        retries += 1
        time.sleep(5)
    
    logging.error(f"Max retries reached. Skipping: {url}")

def recursive_download(base_url, local_dir):
    """
    Recursively downloads files from the Census TIGER directory.
    Ensures that only files within the TIGER2024 directory are followed.
    """
    if base_url in VISITED_URLS:
        logging.info(f"Skipping already visited: {base_url}")
        return
    VISITED_URLS.add(base_url)
    
    logging.info(f"Entering directory: {base_url}")
    links = get_links(base_url)
    for link in links:
        full_url = urljoin(base_url, link)
        local_path = os.path.join(local_dir, link)
        
        if link.endswith('/') and full_url.startswith(BASE_URL):
            logging.info(f"Recursing into: {full_url}")
            recursive_download(full_url, local_path)
        elif full_url.startswith(BASE_URL):
            download_file(full_url, local_path)

if __name__ == "__main__":
    logging.info("Starting download process...")
    recursive_download(BASE_URL, DEST_DIR)
    logging.info("Download process completed.")
